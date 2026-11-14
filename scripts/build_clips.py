#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_clips.py —— 分镜镜(shot) 重组为 生成段(clip)

三层架构的中间层。视频模型单段下限 3-4s，而分镜镜只有 1.5-3.0s，
本脚本把 2-4 个相邻分镜镜合并为 1 个可投喂的生成段。

用法:
    python build_clips.py shots.json --model minimax-h3
    cat shots.json | python build_clips.py --model seedance-2.5

输入 JSON:
{
  "model": "minimax-h3",
  "shots": [
    {"id": 1, "title": "起手", "duration": 2.0, "is_cut_point": true},
    {"id": 2, "title": "试探", "duration": 1.5, "is_cut_point": false}
  ]
}

输出 JSON:
{"status": "ok", "total_duration": 12, "clip_count": 3,
 "clips": [{"index":1, "duration_s":5, "shot_range":"分镜1-3", "shot_ids":[1,2,3]}],
 "warnings": []}
"""
import argparse
import json
import math
import sys

# 模型硬上限，与 config.yaml 保持一致
MODEL_LIMITS = {
    "seedance-2.5":     {"min": 4, "max": 30, "step": 1},
    "kling-4.0":        {"min": 3, "max": 30, "step": 1},
    "kling-4.0-flash":  {"min": 3, "max": 20, "step": 1},
    "minimax-h3":       {"min": 4, "max": 15, "step": 1},
}

# 跨模型交集安全值（默认天花板）
SAFE_MAX = 15
SHOTS_PER_CLIP = (2, 4)


def build_clips(shots, model, allow_long_clip=False):
    """把分镜镜列表重组为生成段列表。核心算法见 references/07-timeline-rules.md"""
    if model not in MODEL_LIMITS:
        return {"status": "error",
                "errors": [{"code": "E_MODEL_UNSUPPORTED",
                            "message": f"未知模型 {model}，支持: {', '.join(MODEL_LIMITS)}"}]}

    lim = MODEL_LIMITS[model]
    clip_max = lim["max"] if allow_long_clip else min(lim["max"], SAFE_MAX)
    clip_min = lim["min"]
    warnings = []

    clips = []
    current = []      # 当前段累积的 shot
    current_dur = 0.0

    def flush():
        nonlocal current, current_dur
        if not current:
            return
        # 向上取整到模型步进
        dur = int(math.ceil(current_dur / lim["step"]) * lim["step"])
        dur = max(dur, clip_min)
        clips.append({
            "index": len(clips) + 1,
            "duration_s": dur,
            "shot_range": f"分镜{current[0]['id']}-{current[-1]['id']}",
            "shot_ids": [s["id"] for s in current],
            "titles": [s.get("title", "") for s in current],
        })
        current, current_dur = [], 0.0

    for shot in shots:
        d = float(shot.get("duration", 1.5))
        is_cut = bool(shot.get("is_cut_point", False))

        # 单镜超模型上限 → 本身就必须独立成段且会溢出，直接报错
        if d > clip_max:
            warnings.append(
                f"【超规格】分镜{shot['id']} 时长 {d}s 超过 {model} 单段上限 {clip_max}s，"
                f"需人工拆分该镜"
            )

        current.append(shot)
        current_dur += d

        # 规则1: 段内镜数达到上限 → 强制切
        if len(current) >= SHOTS_PER_CLIP[1]:
            flush()
            continue
        # 规则2: 遇到可切点且已达模型下限 → 切
        if is_cut and current_dur >= clip_min:
            flush()
            continue
        # 规则3: 累计达上限 → 必须切
        if current_dur >= clip_max:
            flush()
            continue

    flush()  # 收尾

    # 后置检查
    for c in clips:
        n = len(c["shot_ids"])
        if n < SHOTS_PER_CLIP[0]:
            warnings.append(
                f"【镜数偏少】生成段{c['index']} 仅 {n} 个分镜镜，"
                f"低于建议下限 {SHOTS_PER_CLIP[0]}，动作可能做不完"
            )

    total = sum(c["duration_s"] for c in clips)
    raw_total = round(sum(float(s.get("duration", 1.5)) for s in shots), 1)
    drift = round(total - raw_total, 1)
    if abs(drift) >= 1.0:
        warnings.append(
            f"【时长漂移】分镜镜合计 {raw_total}s，向上取整后生成段合计 {total}s，"
            f"漂移 {drift}s。剪辑时需按生成段时长对齐"
        )
    return {
        "status": "ok",
        "model": model,
        "raw_duration": raw_total,
        "total_duration": total,
        "drift": drift,
        "clip_count": len(clips),
        "clips": clips,
        "warnings": warnings,
    }


def main():
    ap = argparse.ArgumentParser(description="分镜镜 → 生成段 重组器")
    ap.add_argument("input", nargs="?", help="输入 JSON 文件路径，缺省读 stdin")
    ap.add_argument("--model", default="seedance-2.5", choices=list(MODEL_LIMITS))
    ap.add_argument("--allow-long-clip", action="store_true",
                    help="允许超过 15s 的生成段（此时目标模型不能是 minimax-h3）")
    args = ap.parse_args()

    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    data = json.loads(raw)
    shots = data.get("shots", [])
    model = data.get("model", args.model)

    if args.allow_long_clip and model == "minimax-h3":
        print(json.dumps({"status": "error", "errors": [{
            "code": "E_SPEC_OVERFLOW",
            "message": "minimax-h3 单段上限 15s，不支持 allow_long_clip"}]},
            ensure_ascii=False, indent=2))
        sys.exit(1)

    result = build_clips(shots, model, args.allow_long_clip)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
