# duel-fight-prompt · 打斗分镜提示词生成 Skill

**仓库**：https://github.com/Dream2046-Light/duel-fight-prompt

打斗分镜提示词生成 Skill。把打斗意图变成**可直接复制投喂视频模型的提示词包**——默认输出纯文本文档（生成段提示词置于代码块，复制即用），可选 JSON 结构化返回。

目标模型：**Seedance 2.5**（默认主力·中文）/ **Kling 4.0**（复杂运镜·4K）/ **MiniMax H3**（英文短段·指令编辑）

---

## 安装

### WorkBuddy / CodeBuddy

```bash
git clone https://github.com/Dream2046-Light/duel-fight-prompt.git ~/.workbuddy/skills/duel-fight-prompt
```

### Claude Code

```bash
git clone https://github.com/Dream2046-Light/duel-fight-prompt.git ~/.claude/skills/duel-fight-prompt
```

### Codex

```bash
git clone https://github.com/Dream2046-Light/duel-fight-prompt.git ~/.codex/skills/duel-fight-prompt
```

装好后直接说「做一个 A 和 B 在某某场景对决的 30 秒分镜」即可触发。

环境要求：Python 3.8+（只有自检脚本需要，纯生成不跑脚本也能用）。

---

## 快速开始

### 调用 1 · 一句话

```text
帮我做一个白衣剑客和巨兽在瀑布边对决的分镜
```

### 调用 2 · 带参数

```text
fight_type=仙侠武侠
subjects=[{name:沈青梧, appearance:玄色长袍, weapon:三尺青锋, fx_system:{color:墨金, trigger:[剑格,指节,衣摆]}},
          {name:噬峦, role:monster, appearance:三十丈巨兽暗紫鳞甲}]
scene=巨型瀑布深潭
total_duration=30
target_model=seedance-2.5
```

### 调用 3 · 续镜（多轮连贯打斗）

```text
接着上一段。沈青梧已被压制单膝跪地，从这里写他起身反击到第一次大招爆发。
continuation={
  prev_tail_frame: "沈青梧单膝跪在水面，斗笠被削裂，墨金飞白散乱",
  character_state: "左肩受伤，长剑仍在手",
  move_progress: "已出九连斩，大招未放",
  unresolved_action: "顾停云的连续突刺尚未结束"
}
```

---

## 返回结构

**默认 `output_format=text`**：一份纯文本文档，每个生成段的提示词放在独立代码块内，整段复制进视频模型即可生成；负面词单独一行，便于按平台 UI 分别填入。版式见 `assets/templates/output-text.md`。

**`output_format=json`**（Agent 程序集成用）：

```json
{
  "status": "ok | degraded | blocked | error",
  "storyboard": "中文分镜稿（人读/审片）",
  "clips": [{ "index": 1, "duration_s": 8, "prompt": "...", "negative": "...", "params": {...} }],
  "warnings": [],
  "errors": [],
  "meta": { "mode": "create", "model": "seedance-2.5", "shot_style": "B",
            "selection_reason": "...", "template_version": "1.1.0" }
}
```

**两个轨**：
- `storyboard` —— 给人看的分镜稿，四段骨架
- `clips[]` —— 给模型吃的生成段，每段 4-15s，逐条投喂

---

## 错误码

| 码 | 含义 | Agent 该做什么 |
|---|---|---|
| `E_MISSING_REQUIRED` | 缺 `fight_type` / `subjects` / `scene` | 追问用户，不要自行编造 |
| `E_SPEC_OVERFLOW` | 超模型硬上限（如 H3 要 20s 单段） | 引导降规格或换模型 |
| `E_CONTENT_BLOCKED` | 命中风控黑名单 | 拒绝，说明边界，可建议白名单改写 |
| `E_MODEL_UNSUPPORTED` | 请求能力模型/版本不支持（如 Seedance 要 4K） | 建议替代模型 |
| `E_DEGRADED` | 已自动简化，非致命 | 把 `warnings` 透传给用户确认 |

---

## 降级处理建议

`status=degraded` 时，Agent 应把 `warnings` 原样透传给用户，并附上替代方案：

| warning | 建议话术 |
|---|---|
| 【动作易崩坏】连续翻转已减至 2 次 | "连续三次翻转容易让肢体崩坏，我已减到两次，需要的话可以强行加回去" |
| 【同框主体过多】已拆为 N 段 | "三个人同框容易串位，我拆成了两段分别生成，用尾帧接首帧保持连贯" |
| 【超规格已降级】60s 已拆 4 段 | "单段最长 15 秒，我拆成了 4 段，剪的时候按生成段时长对齐" |
| 【时长漂移】取整后 +3.2s | "分镜合计 29.8s，取整后 33s，剪辑需按生成段对齐" |

---

## 模型选择

| 场景 | 模型 | 理由 |
|---|---|---|
| 中文提示词、多参考素材 | **Seedance 2.5**（默认） | 中文理解最强；参考上限 30图+10视频+10音频 |
| 复杂运镜、4K、关键帧精控 | Kling 4.0 | 官方强化大幅动态；10 张关键帧；唯一 4K |
| 英文短段、局部修改不重跑 | MiniMax H3 | 指令式编辑；但单段 ≤15s、无 4K、固定 24fps |

---

## 文件索引

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 主文件。工作流、八条铁律、错误码 |
| `config.yaml` | 全部默认值与模型硬上限 |
| `schema/` | 入参/出参 JSON Schema |
| `references/00-skeleton.md` | 三层架构、四段骨架、自检清单 |
| `references/03-collision-system.md` | **三级碰撞配方表（查表，不许改写）** |
| `references/04-camera-library.md` | 运镜词库（五档，中英对照） |
| `references/05-move-library.md` | 招式库（攻-防-反-收） |
| `references/07-timeline-rules.md` | 节奏曲线、生成段重组算法 |
| `references/08-banned-patterns.md` | 风控黑白名单 |
| `models/` | 三模型方言适配 |
| `scripts/build_clips.py` | 分镜镜 → 生成段重组器 |
| `scripts/timeline.py` | 章节时长分配器 |
| `scripts/lint_prompt.py` | 分镜稿校验器 |
| `assets/templates/output-text.md` | **默认输出的纯文本版式**（复制即投喂） |
| `examples/` | 两份黄金样本（A 型 / B 型） |

---

## 自检脚本

```bash
# 校验分镜稿
python scripts/lint_prompt.py storyboard.md --model seedance-2.5

# 分配时长
python scripts/timeline.py --duration 30 --genre 仙侠武侠

# 重组生成段
python scripts/timeline.py --duration 30 --json | python scripts/build_clips.py --model minimax-h3
```

---

## 三条铁律速记

1. **触发源** —— 特效必须有物理来源，禁止悬浮无源
2. **有结果** —— 每一击必须命中/格挡/闪避/拆招/反击，禁止打空气
3. **有来有回** —— 主角至少被压制一次，禁止全程碾压

---

## 支持范围

| 类型 | 状态 | 说明 |
|---|---|---|
| 仙侠斗法 / 武侠兵刃 | ✅ 核心 | 水墨特效体系主战场 |
| 冷兵器刀剑枪戟 | ✅ 核心 | 招式库一至六节 |
| 怪兽 / 巨兽搏斗 | ✅ 核心 | 吨位差异化的碰撞设计 |
| 拳脚搏击 / 功夫 | ✅ 支持 | 招式库第七节，靠位移与卸力做打击感 |
| 机甲格斗 | ✅ 支持 | 招式库第八节，受击统一为装甲损伤体系（全程无血） |
| 影视化枪战 | ⚠️ 受限 | 招式库第九节；中弹反馈强制改写为护具崩裂/装备脱手 |
| 多人混战（≥3 主体同框） | ❌ 单次不支持 | 实证高崩坏区，强制拆段，每段 ≤2 主体 |

## 风控边界

`violence_level` 三档：`none`（无血）/ `cinematic`（默认，风格化轻微血迹）/ `stylized_blood`（明确溅血）。

**永久禁止、任何档位不可绕过**：断肢、内脏外露、虐杀酷刑、公开处刑、未成年人打斗、真实暴力斗殴。
命中即返回 `E_CONTENT_BLOCKED`，不做静默改写。

真实血腥的影视化替代写法见 `references/08-banned-patterns.md` 黑白名单对照表。

---

## License

MIT © 2026 Dream2046

