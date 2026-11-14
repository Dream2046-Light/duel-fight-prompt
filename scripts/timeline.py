#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timeline.py —— 章节时长分配器

按九段式节奏曲线，把总时长分配给每个节拍的分镜镜。
配合 references/07-timeline-rules.md 使用。

用法:
    python timeline.py --duration 30 --genre 仙侠武侠
    python timeline.py --duration 30 --genre 巨兽搏斗 --json
"""
import argparse
import json

# 九段式节奏曲线：(节拍名, 镜数, 时长权重, 碰撞等级)
# 权重用于按总时长等比缩放，镜数固定（结构不可改）
BEATS = [
    ("起手",       2, 0.13, "none"),
    ("试探",       2, 0.13, "light"),
    ("连招升级",   4, 0.27, "light"),
    ("第一次重击", 1, 0.07, "heavy"),
    ("对手反击",   2, 0.13, "light"),
    ("主角被压制", 1, 0.07, "light"),
    ("大招蓄力",   1, 0.07, "none"),
    ("终极对撞",   2, 0.13, "ultimate"),
    ("收尾",       2, 0.13, "none"),
]

# 仙侠斗法可扩展节拍 7-8 为双大招
XIANXIA_BEATS = [
    ("起手",       2, 0.11, "none"),
    ("试探",       2, 0.11, "light"),
    ("连招升级",   4, 0.24, "light"),
    ("第一次重击", 1, 0.06, "heavy"),
    ("对手反击",   2, 0.11, "light"),
    ("主角被压制", 1, 0.06, "light"),
    ("大招蓄力",   2, 0.11, "none"),
    ("终极对撞",   2, 0.13, "ultimate"),
    ("收尾",       2, 0.07, "none"),
]

# 单镜时长建议（秒）
SHOT_DUR = {"none": 1.8, "light": 1.6, "heavy": 2.2, "ultimate": 2.4}


def allocate(total_duration, genre="仙侠武侠"):
    """把总时长按节奏曲线分配到每个分镜镜"""
    beats = XIANXIA_BEATS if genre in ("仙侠武侠", "仙侠") else BEATS
    shots = []
    shot_id = 1

    for name, count, weight, level in beats:
        beat_dur = total_duration * weight
        per_shot = round(beat_dur / count, 1)
        # 单镜时长收敛到 1.0-3.0 合法区间
        per_shot = max(1.0, min(3.0, per_shot))
        for i in range(count):
            shots.append({
                "id": shot_id,
                "beat": name,
                "duration": per_shot,
                "collision": level,
                # 重碰撞与大招是可切点；节拍末镜也是可切点
                "is_cut_point": level in ("heavy", "ultimate") or i == count - 1,
            })
            shot_id += 1

    actual = round(sum(s["duration"] for s in shots), 1)
    return {
        "genre": genre,
        "target_duration": total_duration,
        "actual_duration": actual,
        "shot_count": len(shots),
        "drift": round(actual - total_duration, 1),
        "shots": shots,
    }


def main():
    ap = argparse.ArgumentParser(description="章节时长分配器")
    ap.add_argument("--duration", type=int, default=30, help="章节总时长(秒)")
    ap.add_argument("--genre", default="仙侠武侠",
                    choices=["仙侠武侠", "冷兵器", "巨兽搏斗"])
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    r = allocate(args.duration, args.genre)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    print(f"题材: {r['genre']}  目标: {r['target_duration']}s  "
          f"实际: {r['actual_duration']}s  漂移: {r['drift']}s  镜数: {r['shot_count']}")
    print("-" * 62)
    cur = None
    for s in r["shots"]:
        if s["beat"] != cur:
            cur = s["beat"]
            print(f"\n【{cur}】")
        mark = " ★可切点" if s["is_cut_point"] else ""
        print(f"  镜头{s['id']:>2}  {s['duration']}s  碰撞:{s['collision']}{mark}")


if __name__ == "__main__":
    main()
