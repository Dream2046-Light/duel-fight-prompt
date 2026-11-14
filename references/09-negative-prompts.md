# 09 · 负面提示词库

**固定全局负面词强制追加，不可关闭。** `include_negative=false` 只关动态部分，全局部分永远保留。

---

## 一、全局固定负面词（必加）

### 中文（Seedance）

```text
畸形肢体，多余手指，关节反折，身体穿模，武器穿模，面部崩坏，
动作卡顿，帧间跳变，人物瞬移，场景闪烁，肢体断裂(非剧情)，
文字，字幕，水印，logo，低画质，过度模糊，现代建筑，现代服装
```

### 英文（Kling / H3）

```text
deformed limbs, extra fingers, broken joints, body clipping, weapon clipping,
distorted face, broken anatomy, motion stutter, frame skipping, teleporting,
scene flicker, text, subtitles, watermark, logo, low quality, over-blurred,
modern architecture, modern clothing
```

### 为什么这几条必须加

打斗视频的高频崩坏点，按实证发生率排序：

| 问题 | 表现 | 负面词 |
|---|---|---|
| 肢体崩坏 | 多手指、关节反向、断肢 | 畸形肢体 / 多余手指 / 关节反折 |
| 穿模 | 武器穿过身体、手臂穿过躯干 | 身体穿模 / 武器穿模 |
| 动作断裂 | 卡顿、跳帧、人物闪现 | 动作卡顿 / 帧间跳变 / 人物瞬移 |
| 场景漂移 | 背景突然变化、闪烁 | 场景闪烁 |
| 出戏元素 | 现代建筑混入古装场景 | 现代建筑 / 现代服装 |
| 版权痕迹 | 水印、logo、字幕 | 水印 / logo / 字幕 / 文字 |

---

## 二、动态负面词（按题材与分级追加）

### 按 fight_type

| 类型 | 中文追加 | 英文追加 |
|---|---|---|
| 仙侠武侠 | 现代元素，枪械，机械 | modern elements, firearms, machinery |
| 冷兵器 | 现代建筑，现代服装，枪械 | modern architecture, modern clothing, firearms |
| 巨兽搏斗 | 卡通风格，Q版，可爱化 | cartoon style, chibi, cute stylization |

### 按 violence_level

| 级别 | 中文追加 | 英文追加 |
|---|---|---|
| `none` | 血迹，伤口，血雾 | blood, wound, gore |
| `cinematic`（默认） | 断肢，内脏，写实血腥 | severed limb, internal organs, realistic gore |
| `stylized_blood` | 断肢，内脏，骨骼外露 | severed limb, internal organs, exposed bone |

### 按 motion_intensity

| 强度 | 追加 |
|---|---|
| `low` | 快速剪辑，剧烈抖动 |
| `medium` | （不加） |
| `high` | 动作模糊过度，画面晃动过度 |

---

## 三、模型方言差异

| 模型 | 负面词位置 | 语言 |
|---|---|---|
| Seedance 2.5 | 独立负面词字段 | 中文 |
| Kling 4.0 | 独立负面词字段 | 英文 |
| MiniMax H3 | **无独立负面词字段**，写在描述里用 `avoid: ...` | 英文 |

### H3 的特殊写法

```text
integrated_multimodal_description: [Shot 1] ... Avoid deformed limbs,
extra fingers, body clipping, weapon clipping, motion stutter, scene
flicker, text, subtitles, watermark.
```

---

## 四、组装示例

### Seedance（中文，仙侠武侠 + cinematic）

```text
畸形肢体，多余手指，关节反折，身体穿模，武器穿模，面部崩坏，
动作卡顿，帧间跳变，人物瞬移，场景闪烁，文字，字幕，水印，logo，
低画质，过度模糊，现代建筑，现代服装，现代元素，枪械，机械，
断肢，内脏，写实血腥
```

### Kling（英文，冷兵器 + cinematic）

```text
deformed limbs, extra fingers, broken joints, body clipping, weapon clipping,
distorted face, motion stutter, frame skipping, teleporting, scene flicker,
text, subtitles, watermark, logo, low quality, over-blurred, modern
architecture, modern clothing, firearms, severed limb, internal organs,
realistic gore
```

---

## 五、不要过度堆负面词

**负面词不是越多越好。** 超过 30 条会稀释权重，模型抓不到重点。

**建议上限**：全局 18 条 + 动态追加 ≤10 条 = 总计 ≤28 条。

**优先级**：全局固定 > 按分级 > 按题材 > 按运动强度。超限时从后往前砍。
