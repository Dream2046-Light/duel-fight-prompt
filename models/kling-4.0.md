# Kling 4.0 方言（复杂运镜 / 4K / 关键帧精控）

**什么时候切到它**：
- 需要 **4K** 输出（三个模型中唯一支持）
- 需要**灵活关键帧**精控（最多 10 张，Seedance/H3 只有首尾帧）
- 打斗含**大幅度动态与复杂运镜**（官方这一代明确强化的能力，最贴打斗场景）
- 需要**续拍**长打斗（累计最长 2 分钟）

---

## 一、硬约束

| 项 | Kling 4.0 | Kling 4.0 Flash |
|---|---|---|
| 生成段时长 | 3-30s | 3-20s |
| 分辨率 | 720p / 1080p / **4K** | 720p |
| 画幅 | 21:9 / 16:9 / 1:1 / 9:16 / auto | 同左 |
| 提示词长度 | 8000 tokens（API 26000 英文字符），按 7000 字符保守 | 同左 |
| 参考素材 | 合计最多 15 项：图 10 / 视频 5（总 30s）/ 主体 7 | 较少 |
| 关键帧 | **最多 10 张** | — |
| 音频 | 双通道立体声 + 口型匹配 | 同左 |
| 内容过滤 | 平台侧审核 | 同左 |

> ⚠️ 10-bit HDR 标注"即将上线"，不要当作当前可用能力。

---

## 二、提示词语法（英文）

Kling 4.0 用**英文**写提示词。推荐结构：

```
{Style}: photorealistic 3D CG, PBR materials, cinematic color grading,
UE5 Path Tracing, Lumen global illumination, 35mm Kodak 5219 film grain

{Scene}: location, light direction, terrain, weather, atmosphere

{Subject A}: appearance, costume, weapon. VFX description with trigger sources.
{Subject B}: same

{Action}: chronological, who does what to whom, clear results

{Camera}: camera movement description

{Environment feedback}

{Audio (if audio_mode != none)}
```

### 运镜术语（英文原词，不要翻译）

| 中文 | 英文 |
|---|---|
| 高速跟拍 | High-speed tracking shot |
| 极速甩摇 | Whip pan |
| 螺旋环绕 | Orbit / Spiral orbit |
| 贴地仰拍 | Low-angle ground shot |
| 越肩视角 | Over-the-shoulder |
| 虫视仰拍 | Worm's-eye view |
| 大远景升降 | Crane shot (high angle pull-back) |
| 卫星级超广角 | Satellite ultra-wide |
| 推拉 | Dolly in / Dolly out |
| 时间流速骤降 | Time ramp slowdown |

### 运镜写法：类型 + 幅度 + 速度

Kling 4.0 对运镜的描述建议三段式：

```
A high-speed tracking shot (motion type) follows the blade closely (amplitude),
accelerating through the final strike (speed).
```

---

## 三、关键帧用法（Kling 独有优势）

最多 10 张关键帧，用于锁定打斗中的关键时刻：

```
Keyframe 1 (0.0s): 两人远距离对峙，瀑布深潭全景
Keyframe 2 (3.0s): 沈青梧拔剑，墨金特效从剑鞘缝隙喷涌
Keyframe 3 (6.0s): 五连斩最后一击，兵刃碰撞瞬间
Keyframe 4 (9.0s): 顾停云被震退，青白风刃散乱
...
```

**打斗场景建议**：把每次**重碰撞**和**大招爆发**设为关键帧，轻碰撞不必。10 张关键帧大约够覆盖 30s 打斗的 5-6 个重击点。

---

## 四、音频写法

Kling 4.0 默认双通道立体声，会自己配环境音，但**主动描述能显著提质**：

| audio_mode | 写法 |
|---|---|
| `none` | `No background music, no on-screen text, no watermark. Silent ambience.` |
| `sfx_only`（默认） | `No background music. Ambient and SFX only: waterfall roar, blade clash, sword whoosh, water burst, energy detonation. Stereo.` |
| `full` | 另加 `Dialogue: Ling Mo says "Come." Feng Che replies "Wind, rise." Lip-sync accurate.` |

---

## 五、负面词（英文）

```
deformed limbs, extra fingers, broken joints, body clipping, weapon clipping,
distorted face, broken anatomy, motion stutter, frame skipping, teleporting,
scene flicker, text, subtitles, watermark, logo, low quality, over-blurred,
modern architecture, modern clothing
```

按 `violence_level` 追加：

| 级别 | 追加 |
|---|---|
| `none` | blood, wound, gore |
| `cinematic` | severed limb, internal organs, realistic gore |
| `stylized_blood` | severed limb, internal organs, exposed bone |

---

## 六、示例（生成段 prompt）

```
Photorealistic 3D CG, PBR materials, cinematic color grading, UE5 Path Tracing,
Lumen global illumination, 35mm Kodak 5219 film grain.

Giant waterfall deep pool. Hard cold-white light beams cut through the water
curtain from upper left. Black mossy rocks surround the pool. Mist never lifts.

Subject A (Ling Mo): three-foot straight sword, fine usage scratches on the blade,
aged bronze guard. Ink-gold flying-white VFX clings tightly to the blade, guard,
knuckles and robe edge, jumping, crawling and coiling, radiating from the guard
as the trigger source, with motion blur and particle trails.
Subject B (Feng Che): narrow straight sword, wind-pattern guard. Cyan-white wind
blades cling to the blade, bracer and shoulder armor, wind threads spraying from
bracer and guard.

Ling Mo strikes diagonally upward; Feng Che blocks with the guard. Ling Mo follows
with a horizontal slash; Feng Che sidesteps. Ling Mo thrusts; Feng Che counters
with a forward step-slash. A high-speed tracking shot follows the blade path,
whip pan in the middle, spiral orbit around both fighters at the end. Ink-gold
and cyan-white particles burst at each impact point. Light collision: ink black-
white impact frame + 0.05s frame extraction + local negative + axial micro-shake
+ attribute particle spray.

The pool surface bursts into rings, mist surges, the waterfall curtain is cut open
by sword energy, white petals shatter.

No background music. Ambient and SFX only: waterfall roar, blade clash, sword
whoosh, water burst. Stereo.
```
