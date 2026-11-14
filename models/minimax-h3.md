# MiniMax H3 方言（英文短段 · 指令式编辑）

**什么时候切到它**：
- 需要**局部修改不重跑**（In-Context Regeneration 指令式编辑，独有）
- 提示词习惯用英文写
- 单段 ≤15s 的短平快片段

**什么时候不要用**：需要 4K（H3 最高 2K）、需要超过 15s 的单段。

---

## 一、硬约束

| 项 | 值 |
|---|---|
| 生成段时长 | **4-15s，整数秒**（下限比 Kling 高，上限最严） |
| 分辨率 | 768p（基座）/ 2K（H3+2 模块，仅 API） |
| 帧率 | 固定 24fps |
| 画幅 | 16:9 / 9:16 / 1:1 / 4:3 / 21:9 / 3:4 |
| 提示词长度 | **7000 字符**（官方 API 上限） |
| 参考素材 | 合计最多 12 项：图 9 / 视频 3 / 音频 3 |
| 关键帧 | 首尾帧 2 张 |
| 音频 | 32kHz 立体声，音画联合生成 |
| 内容过滤 | 平台侧审核 |

---

## 二、提示词结构（必须遵循）

> 本结构与 `h3-prompt-writing` skill 完全对齐。若两个 skill 同时安装，以该 skill 的
> `references/base-en.txt` 为准。

### 第一部分：指令行（仅图生视频模式需要）

**T2VA**（纯文本）：无指令行，直接进三字段。

**I2VA**（首帧生视频）：
```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

**FL2VA**（首尾帧）：
```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

**L2VA**（尾帧生视频）：
```text
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

> `S.SS` 必须是**恰好两位小数**的有效时长（如 `08.00`）。

指令行后空一行，再进三字段。

### 第二部分：三个核心字段

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

| 字段 | 内容 |
|---|---|
| `integrated_multimodal_description` | 视觉、动作、镜头、说话人、对白、**剧情内音效**，沿时间线展开 |
| `overall_soundscape` | 全片环境音、物理动作声、非语言人声 |
| `non_diegetic_music` | 角色听不到、只有观众能听到的背景音乐 |

---

## 三、打斗场景写法

### 1. 镜头标记与时间戳

```
[Shot 1] A low-angle ground shot frames the deep pool at the foot of the giant
waterfall. Ling Mo stands on a mossy rock, sword still sheathed. At 00:03.500,
the camera cuts to a high-speed tracking shot as he draws the blade.
```

- 镜头标记：`[Shot N]`（方括号 + Shot + 数字）
- 时间戳格式：`00:0X.XXX`（毫秒三位）
- **总时长必须与请求的时长匹配** —— 15s 的片，最后时间戳不能到 18s

### 2. 运镜三段式（类型 + 幅度 + 速度）

H3 官方推荐的运镜描述结构：

```text
A whip pan (motion type) sweeps across the full width of the frame (amplitude),
executed at extreme speed (speed).
```

### 3. 参考素材标签

用 `<Picture 1>`、`<Video 1>`、`<Audio 1>` 引用，**所有字段中标签必须一致**：

```text
integrated_multimodal_description: [Shot 1] <Picture 1> shows the white-robed
swordswoman. She draws the blade and the ink-gold VFX crawls along the edge...

overall_soundscape: <Audio 1> provides the waterfall ambience...
```

### 4. 碰撞配方写法

三级碰撞配方在英文稿中保留技术词，不要意译数值：

```text
Light collision: ink black-white impact frame + 0.05s frame extraction +
local negative + axial micro-shake + attribute particle spray.
```

---

## 四、音频（H3 的坑）

**H3 只写画面会出无声片。** 必须写 `overall_soundscape`。

| audio_mode | 写法 |
|---|---|
| `none` | `overall_soundscape: silence. No ambient sound, no SFX.` |
| `sfx_only`（默认） | `overall_soundscape: waterfall roar, blade clash ringing, sword whoosh, water burst, energy detonation, footsteps on wet rock.` |
| `full` | 另在 `integrated_multimodal_description` 中写对白：`Ling Mo says "Come." Feng Che replies "Wind, rise."` |

**`non_diegetic_music`**：
| audio_mode | 写法 |
|---|---|
| 任意 | `non_diegetic_music: none.`（打斗片通常无 BGM） |

---

## 五、负面词（英文）

H3 没有独立负面词字段，负面约束**写在描述里**（用 `no ...` / `avoid ...`），或走平台的负面提示词栏：

```
avoid: deformed limbs, extra fingers, broken joints, body clipping, weapon
clipping, distorted face, motion stutter, frame skipping, teleporting, scene
flicker, text, subtitles, watermark, logo, low quality, over-blurred
```

---

## 六、示例（生成段 prompt，8 秒）

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Photorealistic 3D CG, PBR materials, cinematic color grading, UE5 Path Tracing, Lumen global illumination, 35mm Kodak 5219 film grain. A low-angle ground shot frames the giant waterfall deep pool. Hard cold-white light beams cut through the water curtain from upper left. Black mossy rocks surround the pool, mist never lifts. <Picture 1> shows the white-robed swordswoman Ling Mo, three-foot straight sword, aged bronze guard. Ink-gold flying-white VFX clings tightly to the blade, guard, knuckles and robe edge, jumping, crawling and coiling, radiating from the guard as the trigger source. At 00:02.000, a high-speed tracking shot (motion type) follows the blade closely (amplitude), accelerating through the strike (speed). She slashes diagonally upward; the cyan-white wind blades of Feng Che meet hers at 00:04.500 with a light collision — ink black-white impact frame plus 0.05s frame extraction plus local negative plus axial micro-shake plus attribute particle spray. At 00:06.000, a whip pan sweeps across the full width of the frame at extreme speed, following her horizontal slash. The pool surface bursts into rings, mist surges, the waterfall curtain is cut open by sword energy, white petals shatter.

overall_soundscape: waterfall roar, blade clash ringing, sword whoosh, water burst, footsteps on wet rock, energy crackle. Stereo.

non_diegetic_music: none.
```

---

## 七、指令式编辑（失败兜底专用）

生成结果不理想时，H3 支持**不重跑**的局部修改：

```text
Replace the sword in Ling Mo's hand with a long spear. Keep everything else identical.
```

适合修正：武器变形、特效颜色错误、背景元素错误。
不适合修正：动作节奏错误（那需要重跑）。
