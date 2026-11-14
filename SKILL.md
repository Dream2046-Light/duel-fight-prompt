---
name: duel-fight-prompt
display_name: 打斗分镜提示词生成
display_name_en: Duel Fight Prompt Generator
description_zh: 生成影视级打斗视频的分镜脚本与生成段提示词，对接 Seedance 2.5 / Kling 4.0 / MiniMax H3。当用户需要打斗、对决、PK、比武、仙侠斗法、武侠兵刃、冷兵器交锋、巨兽搏斗、怪兽对战、拳脚格斗、机甲对战、影视化枪战的分镜脚本、镜头脚本、视频提示词、AI 视频打斗片段时使用。支持水墨特效体系、三级碰撞冲击帧、四段式分镜骨架，并自动完成分镜重组、模型方言适配、暴力分级风控与动作崩坏兜底。
description_en: Generate cinematic fight-scene storyboards and clip prompts for Seedance 2.5 / Kling 4.0 / MiniMax H3. Use when the user needs fight choreography prompts, duel storyboards, wuxia/xianxia combat, cold-weapon clashes, monster battles, hand-to-hand combat, mecha duels, cinematic gunfights, ink-wash VFX shot lists, or AI fight video prompts. Handles shot-to-clip regrouping, model dialect adaptation, violence-grading and motion-collapse fallbacks.
category: video
version: 1.1.0
---

# 打斗分镜提示词生成

把一段打斗意图，变成**可直接复制投喂视频模型的纯文本提示词包**。

你输出的不是视频，是提示词。默认交付一份纯文本文档：分镜稿给人读，每个生成段的提示词放在独立代码块里——用户整段复制进视频模型即可生成，无需二次加工（版式见 `assets/templates/output-text.md`）。仅当入参 `output_format=json` 时才按 `schema/output.schema.json` 返回结构化 JSON，供 Agent 程序集成。

---

## 一、什么时候用我

用户提到以下任意一类意图即触发：

- **动作**：打斗、对决、PK、比武、切磋、交手、拆招、过招、厮杀、搏斗
- **题材**：仙侠斗法、武侠、江湖、冷兵器、刀剑、枪戟、巨兽、妖兽、怪兽、玄幻战斗、拳脚格斗、机甲对战、影视化枪战
- **产出**：分镜脚本、镜头脚本、视频提示词、AI 视频片段、打斗特效、运镜设计
- **风格**：水墨特效、冲击帧、抽帧、负片、鱼眼畸变、雾山五行式手绘飞白

**不触发**：纯剧情剧本、无动作的叙事短片、真人拍摄的分镜头表（非 AI 生成）。

---

## 二、先读这三个文件

按顺序读，缺哪个补哪个：

| 顺序 | 文件 | 作用 |
|---|---|---|
| 1 | `config.yaml` | 全部默认值与模型硬上限。**入参优先级高于它** |
| 2 | `references/00-skeleton.md` | 四段骨架与三层架构定义 |
| 3 | `references/03-collision-system.md` | 三级碰撞配方表（查表，不许自由发挥） |

按需再读：`04-camera-library.md`（运镜）、`05-move-library.md`（招式）、`08-banned-patterns.md`（禁止项与黑白名单）、`09-negative-prompts.md`（负面词）。

目标模型确定后，读 `models/` 下对应方言文件。

---

## 三、三层架构（本 skill 的核心概念）

```
章节 sequence   28-30s 完整打斗（对应用户想要的一场戏）
  └─ 生成段 clip   4-15s，真正投喂视频模型的单元
       └─ 分镜镜 shot  1.0-3.0s，脚本层，保留四段骨架
```

**为什么必须三层**：视频模型单段下限是 3-4 秒（MiniMax H3 最低 4s）。而分镜语言的镜头是 1.5-2 秒一个刀光。直接把 1.5s 的镜喂给模型，要么动作做不完，要么模型自己乱补。

**所以**：分镜镜是人读/审片用的导演语言；生成段是模型能消化的物理单元。中间必须做重组（见 `references/07-timeline-rules.md`）。

---

## 四、工作流（六步）

### 第 1 步：意图分流

判断模式：

- `MODE=create` —— 用户给角色/场景/对手，要新做一场打斗
- `MODE=rewrite` —— 用户给了旧提示词或草稿，要套标准骨架改写

分流依据：输入里是否已有成形的分镜或提示词文本。**判断结果写进 `meta.mode`**。

### 第 2 步：收参数并校验

按 `schema/input.schema.json` 校验入参。

- 必填缺项（`fight_type` / `subjects` / `scene`）→ **追问一次**，不静默补全
- 可选缺项 → 用 `config.yaml` 默认值，并在 `meta.defaults_applied` 回显
- 命中黑名单 → 直接返回 `E_CONTENT_BLOCKED`，**不组装提示词**

### 第 3 步：选型

三选一，**必须给一句话理由**：

- **shot_style**（分镜结构）：A 累计时间轴 / B 单片时长 / C 内联紧凑
  - 有台词对白 → A；纯动作高频拆招 → B；要求压缩篇幅 → C
- **target_model**：默认 `seedance-2.5`（中文样本可不改写直投）
- **violence_level**：默认 `cinematic`

### 第 4 步：编排节奏

按 `references/07-timeline-rules.md` 的节奏曲线排分镜镜，套四段骨架写内容。

**这一段是质量主体**，招式从 `05-move-library.md` 取，运镜从 `04-camera-library.md` 取，碰撞等级查 `03-collision-system.md`。

### 第 5 步：重组为生成段

用 `scripts/build_clips.py` 或按 `07-timeline-rules.md` 的规则手工合并：2-4 个相邻分镜镜 → 1 个生成段，向上取整到模型支持的整数秒，结尾落可切点。

### 第 6 步：自检并输出

先跑 `scripts/lint_prompt.py`（或按 `references/00-skeleton.md` 末尾的自检清单人工过一遍），修复所有 FAIL。

**任何降级都必须显式写入标题区 `> ⚠️` 注释行**，不许静默。

然后按 `output_format` 交付：

- **`text`（默认）** —— 按 `assets/templates/output-text.md` 输出纯文本文档：
  - 标题区：`>` 注释行写 meta（版本、MODE、选型、节奏曲线、降级警告）
  - 分镜稿全文（四段骨架，人读/审片/存档）
  - 每个生成段：首帧/尾帧描述 + 独立代码块装正向提示词 + 单独一行负面词
  - 投喂清单表 + 续接方式
  - **铁律：代码块内不得出现 Markdown 标记、镜头编号、时长标注**——复制即所得
- **`json`** —— 按 `schema/output.schema.json` 返回结构化 JSON（Agent 程序集成用）

---

## 五、八条铁律（违反任意一条即为不合格输出）

1. **触发源铁律** —— 特效必须有物理触发源（剑格、指节、枪尖、衣摆），死死贴附并跳跃/爬行/缠绕。**禁止悬浮无源特效**
2. **结果铁律** —— 每一击必须有命中、格挡、闪避、拆招、反击之一。**禁止打空气**
3. **有来有回铁律** —— 对手不能全程挨打。主角必须至少被压制一次
4. **零站桩铁律** —— 无蓄力静止，每 0.3 秒完成一次换位，打必横向移动、击必错步绕身
5. **碰撞配方铁律** —— 轻/重/大招三级碰撞，配方字符串必须**精确匹配**查表，不许改写数值
6. **时长铁律** —— 单镜 1.0-3.0s，单生成段 4-15s，总时长 23.5-30s
7. **纯画面铁律（可配）** —— 默认 `sfx_only`：无 BGM、无字幕、无水印，保留环境音与打斗音效；`audio_mode=none` 时才完全无声
8. **四段齐全铁律** —— 每个分镜镜必须含【复合运镜】【极速动势与拆招】【锚定特效与碰撞】【环境反馈】四段，顺序固定；【受击反馈】仅在反派有反击时加

---

## 六、降级三原则

**不静默拒绝、不静默降级、不静默截断。**

任何降级必须同时满足：`status` 置为 `degraded` + `warnings` 写明原因 + 给出替代方案。

常见降级：

| 触发 | 降级动作 |
|---|---|
| 连续翻转 ≥3 次 | 减至 2 次，warnings 说明 |
| 同一场景同框主体 ≥3 | 强制拆段，每段 ≤2 主体（群战逐对拆打，用环境反应暗示规模） |
| 双长兵对绞 | 简化为"碰撞-分开"两拍 |
| 超长一镜到底 | 拆段 + 尾帧接首帧 |
| 枪战要求中弹伤口/爆头特写 | 按 08 黑白名单改写为护具崩裂/装备脱手，warnings 说明 |

---

## 七、错误码

| 错误码 | 含义 | Agent 该做什么 |
|---|---|---|
| `E_MISSING_REQUIRED` | 缺 `fight_type`/`subjects`/`scene` | 追问用户 |
| `E_SPEC_OVERFLOW` | 超模型硬上限 | 引导降规格或换模型 |
| `E_CONTENT_BLOCKED` | 命中风控黑名单 | 拒绝并说明边界 |
| `E_MODEL_UNSUPPORTED` | 请求能力模型/版本不支持 | 建议替代模型或升级路径 |
| `E_DEGRADED` | 已自动简化（非致命） | 提示用户确认降级方案 |

---

## 八、参考库怎么用

`reference_style` 三种取值：

- `auto`（默认）—— 抽取 10 份样本的**镜头语言、运镜组合、特效句式**作为知识库，不复制具体情节
- `1-10` —— 指定套用第 N 份样本的**结构**（不是内容）
- `off` —— 关闭参考库，纯原生生成

**字段分级**：
- ✅ 可复用：四段骨架、三级碰撞配方、运镜词库、触发源句式、禁止项
- ⚠️ 仅示范：角色名（沈青梧/顾停云/裴砚…）、具体场景、招式名
- ❌ 禁止复用：样例中的集数编号、作者署名、第三方 IP 关联描述

---

## 九、输出

严格按 `schema/output.schema.json` 返回。两个关键字段：

- `storyboard` —— 中文分镜稿，人读、审片、存档、rewrite 模式用
- `clips[]` —— 生成段数组，Agent 逐条投喂模型；每段含正向提示词、负面词、参数、时长、关键帧、warnings

`meta` 必须回写：`mode`、`model`、`shot_style`、`selection_reason`、`defaults_applied`、`template_version`、`violence_level`、`audio_mode`。

---

## 十、示例调用

**一句话**
> 帮我做一个白衣剑客和巨兽在瀑布边对决的分镜

**带参数**
> fight_type=仙侠武侠，A=白衣剑客(唐刀,墨金特效)，B=噬峦巨兽(三十丈,暗紫妖气)，scene=巨型瀑布深潭，total_duration=30s，target_model=seedance-2.5

**带续镜**
> 接着上一段，沈青梧已被压制单膝跪地，从这里开始写他起身反击到第一次大招爆发，continuation 已附尾帧描述
