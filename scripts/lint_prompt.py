#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint_prompt.py —— 分镜稿校验器

对生成的分镜稿做硬规则检查，输出 PASS / WARN / FAIL 三级报告。
任何 FAIL 都必须修复后才能交付。

用法:
    python lint_prompt.py storyboard.md
    python lint_prompt.py storyboard.md --model minimax-h3 --strict
    python lint_prompt.py storyboard.md --json
"""
import argparse
import json
import re
import sys

# ---- 三级碰撞配方（精确字符串，来自 references/03-collision-system.md）----
RECIPE_LIGHT = "水墨黑白冲击帧+0.05s抽帧+局部负片+镜头轴向微甩+属性粒子飞溅"
RECIPE_HEAVY = "水墨放射冲击帧+0.1s抽帧+中心负片+镜头猛沉/猛甩回弹+三层泼墨爆炸"
# 大招的冲击波色系随角色特效变化，只匹配前缀
RECIPE_ULT_PREFIX = ("全屏水墨冲击帧+0.15s抽帧定格+全屏负片闪白"
                     "+径向剧烈震动+中心鱼眼畸变+环形")

# ---- 四段骨架（顺序固定）----
REQUIRED_SECTIONS = ["【复合运镜】", "【极速动势与拆招】",
                     "【锚定特效与碰撞】", "【环境反馈】"]
OPTIONAL_SECTIONS = ["【受击反馈】"]

# ---- 触发源关键词 ----
TRIGGER_WORDS = ["贴附", "爬行", "缠绕", "触发源"]

# ---- 禁止词（质量类）----
BANNED_PATTERNS = [
    (r"→|->", "使用了禁用箭头 → / ->，请用 ➡️ 或 ⇒"),
    (r"[\u4e00-\u9fff]:", "使用了半角冒号，请用全角 ："),
    (r"\[镜头\d+\.\d+\]", "镜头编号出现小数，只允许整数"),
    (r"\[镜头(\d+)\][^\[]{0,40}?\[镜头\1\]", "镜头编号重复"),
]

# ---- 禁止词（安全类，命中即 FAIL）----
SAFETY_BLACKLIST = [
    "断肢", "内脏", "骨骼外露", "虐杀", "酷刑", "处刑",
    "砍断", "斩断四肢", "鲜血狂喷", "血肉模糊", "肢解", "开膛",
    "爆头", "血浆迸溅", "弹孔冒血",
]
# 组合模式（单看不违规，组合命中）
SAFETY_PATTERNS = [
    (r"(未成年|儿童|少年|少女|小孩|孩子|孩童).{0,12}(打斗|战斗|厮杀|被杀|受伤|殴打|砍)",
     "未成年人作为打斗主体或受害者"),
    (r"(殴打|折磨|虐待).{0,10}(求饶|惨叫|哀嚎)", "虐待/折磨描写"),
    (r"(处刑|处决|斩首).{0,10}(示众|公开)", "处刑式描写"),
]
# 隐喻绕过（上下文组合判定）
METAPHOR_PATTERNS = [
    (r"(番茄酱|红色颜料|红玫瑰|红色液体).{0,12}(喷|涌|染|炸|流)", "疑似用隐喻绕过血腥描写"),
    (r"(变成|化作|开成).{0,8}(一朵|一地|一片).{0,8}(鲜红|红色|玫瑰|血花)", "疑似用隐喻绕过死亡描写"),
    (r"(盛开|绽放).{0,6}(红玫瑰|血花|红花)", "疑似用隐喻绕过死亡描写"),
]

# ---- 模型硬上限 ----
MODEL_LIMITS = {
    "seedance-2.5": {"clip": (4, 30), "shot": (1.0, 3.0)},
    "kling-4.0": {"clip": (3, 30), "shot": (1.0, 3.0)},
    "kling-4.0-flash": {"clip": (3, 20), "shot": (1.0, 3.0)},
    "minimax-h3": {"clip": (4, 15), "shot": (1.0, 3.0)},
}


def parse_shots(text):
    """把分镜稿切成镜头块"""
    # 匹配 [镜头N] 或 【镜头N】 开头
    pattern = re.compile(r"[\[【]镜头\s*(\d+(?:\.\d+)?)\s*[\]】]")
    matches = list(pattern.finditer(text))
    shots = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        header = text[start:text.find("\n", start) if text.find("\n", start) > 0 else start + 120]
        shots.append({
            "num": m.group(1),
            "header": header.strip(),
            "body": text[start:end],
        })
    return shots


def parse_shot_duration(header):
    """从镜头标题解析时长，支持 '0.0-2.0s' 和 '2.0s' 和 't0-1.2s'"""
    m = re.search(r"t?(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*s", header)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"[\s|](\d+(?:\.\d+)?)\s*s", header)
    if m:
        return None, float(m.group(1))
    return None, None


def lint(text, model="seedance-2.5", strict=False):
    checks = []   # (level, name, detail)

    def add(level, name, detail=""):
        checks.append({"level": level, "check": name, "detail": detail})

    shots = parse_shots(text)

    # 1. 镜头存在性
    if not shots:
        add("FAIL", "镜头解析", "未解析到任何镜头块，格式应为 [镜头N] 或 【镜头N】")
        return summarize(checks)

    # 2. 镜头编号连续且为整数
    nums = []
    for s in shots:
        try:
            nums.append(float(s["num"]))
        except ValueError:
            pass
    if any(n != int(n) for n in nums):
        add("FAIL", "编号整数性", f"存在非整数编号: {[s['num'] for s in shots]}")
    else:
        int_nums = [int(n) for n in nums]
        expected = list(range(1, len(int_nums) + 1))
        if int_nums != expected:
            add("WARN", "编号连续性", f"编号为 {int_nums}，期望 {expected}")
        else:
            add("PASS", "编号连续性", f"1-{len(int_nums)} 连续")

    # 3. 四段骨架齐全率
    missing = []
    for s in shots:
        for sec in REQUIRED_SECTIONS:
            if sec not in s["body"]:
                missing.append(f"镜头{s['num']} 缺 {sec}")
    if missing:
        add("FAIL", "四段骨架", f"{len(missing)} 处缺失: " + "; ".join(missing[:5]))
    else:
        add("PASS", "四段骨架", f"{len(shots)} 个镜头四段齐全")

    # 4. 触发源 —— 检查章节头部的角色设定段，而非每个镜头块
    # 标准句式：死死贴附在...上跳跃、爬行、缠绕，从...触发源向外扩散
    head = text[:3000]
    has_anchor = "贴附" in head and ("触发源" in head or "向外扩散" in head)
    if not has_anchor:
        add("FAIL", "触发源",
            "章节头部缺少标准触发源句式（贴附…跳跃、爬行、缠绕 + 触发源向外扩散）")
    else:
        add("PASS", "触发源", "角色设定段含标准触发源句式")

    # 5. 碰撞配方精确匹配（文档级）
    if "轻碰撞" in text and RECIPE_LIGHT not in text:
        add("FAIL", "碰撞配方", "出现「轻碰撞」但缺少完整配方字符串")
    elif "轻碰撞" in text:
        add("PASS", "碰撞配方·轻", "配方精确匹配")

    if "重碰撞" in text and RECIPE_HEAVY not in text:
        add("FAIL", "碰撞配方", "出现「重碰撞」但缺少完整配方字符串")
    elif "重碰撞" in text:
        add("PASS", "碰撞配方·重", "配方精确匹配")

    if "大招" in text and RECIPE_ULT_PREFIX not in text:
        add("FAIL", "碰撞配方", "出现「大招」但缺少完整配方前缀")
    elif "大招" in text:
        add("PASS", "碰撞配方·大招", "配方前缀匹配")

    # 数值篡改检查
    for bad, good, name in [
        ("0.5s抽帧", "0.05s", "抽帧数值篡改"),
        ("0.15s抽帧+局部负片", "大招应为全屏负片", "大招负片范围错误"),
        ("两层泼墨", "三层泼墨", "泼墨层数错误"),
    ]:
        if bad in text:
            add("FAIL", name, f"发现「{bad}」，应为「{good}」")

    # 6. 符号规范
    for pat, msg in BANNED_PATTERNS:
        m = re.search(pat, text)
        if m:
            add("WARN", "符号规范", f"{msg}（位置: …{text[max(0,m.start()-15):m.end()+15]}…）")

    # 7. 安全黑名单
    # 负面词行（negative prompt）是"要排除的画面"，其中出现禁用词是合法用法，
    # 安全扫描前先剔除，避免"断肢/内脏"等排除项被误判为正内容。
    safety_text = re.sub(r"(?m)^.*负面词.*$", "", text)
    for w in SAFETY_BLACKLIST:
        if w in safety_text:
            add("FAIL", "安全黑名单", f"命中禁用词「{w}」")

    for pat, msg in SAFETY_PATTERNS:
        m = re.search(pat, safety_text)
        if m:
            add("FAIL", "安全黑名单",
                f"{msg}（…{safety_text[max(0,m.start()-10):m.end()+10]}…）")

    for pat, msg in METAPHOR_PATTERNS:
        m = re.search(pat, safety_text)
        if m:
            add("FAIL", "隐喻绕过", f"{msg}（…{safety_text[max(0,m.start()-10):m.end()+10]}…）")

    # 8. 音频声明
    if not re.search(r"无.{0,4}(背景音乐|BGM)", text):
        add("WARN", "音频声明", "未找到「无背景音乐」声明")
    else:
        add("PASS", "音频声明", "已声明无 BGM")

    # 9. 时长检查
    lim = MODEL_LIMITS.get(model, MODEL_LIMITS["seedance-2.5"])
    durations = []
    for s in shots:
        start, dur = parse_shot_duration(s["header"])
        if dur is None:
            add("WARN", "时长解析", f"镜头{s['num']} 未能解析时长: {s['header'][:60]}")
            continue
        shot_dur = dur - start if start is not None else dur
        durations.append((s["num"], shot_dur))
        if not (lim["shot"][0] <= shot_dur <= lim["shot"][1]):
            add("WARN", "单镜时长",
                f"镜头{s['num']} 时长 {shot_dur}s 超出建议区间 {lim['shot']}")

    if durations:
        total = round(sum(d for _, d in durations), 1)
        add("PASS" if 23.5 <= total <= 30.0 else "WARN", "总时长",
            f"{len(durations)} 镜合计 {total}s（建议 23.5-30s）")

    # 10. 有来有回（主角须至少被压制一次）
    if not re.search(r"被压制|单膝跪|被击中|受挫|踉跄|被迫防守", text):
        add("WARN", "有来有回", "未发现主角受挫/被压制描写，可能违反铁律")

    return summarize(checks)


def summarize(checks):
    fail = [c for c in checks if c["level"] == "FAIL"]
    warn = [c for c in checks if c["level"] == "WARN"]
    if fail:
        status = "FAIL"
    elif warn:
        status = "WARN"
    else:
        status = "PASS"
    return {"status": status,
            "fail_count": len(fail), "warn_count": len(warn),
            "checks": checks}


def main():
    ap = argparse.ArgumentParser(description="分镜稿校验器")
    ap.add_argument("file", help="分镜稿文件路径")
    ap.add_argument("--model", default="seedance-2.5", choices=list(MODEL_LIMITS))
    ap.add_argument("--strict", action="store_true", help="WARN 也视为不通过")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = open(args.file, encoding="utf-8").read()
    result = lint(text, args.model, args.strict)
    if args.strict and result["status"] == "WARN":
        result["status"] = "FAIL"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*58}\n  校验结果: {result['status']}"
              f"    FAIL {result['fail_count']} 项 / WARN {result['warn_count']} 项\n{'='*58}")
        for c in result["checks"]:
            mark = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}[c["level"]]
            print(f"  [{mark}] {c['check']:<16} {c['detail']}")
        print()

    sys.exit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
