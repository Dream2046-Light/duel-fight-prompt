# 01 · 画质风格头

章节开头的风格描述。**注意：`8K` 与 `60帧` 是渲染风格词，不是输出参数**，实际输出分辨率由 `output_resolution` 控制，不要写进正文误导模型。

---

## 一、标准风格头（中文 / Seedance）

```text
8K 3D CG 写实，超精致3D建模人物，PBR 物理材质，电影级色彩分级，
UE5 Path Tracing，Lumen 全局光照，Nanite 几何精度，
35mm Kodak 5219 胶片颗粒，色彩空间 Rec.2020，
人物皮肤纹理、发丝动态、汗渍/血渍附着超写实，
布料动力学真实，金属兵刃带使用划痕与旧化质感
```

### 各条款作用

| 条款 | 作用 |
|---|---|
| 8K 3D CG 写实 | 整体质感定位（风格词，非分辨率） |
| 超精致3D建模人物 | 人物精度 |
| PBR 物理材质 | 材质响应真实光照 |
| 电影级色彩分级 | 调色风格 |
| UE5 Path Tracing | 光线追踪质感 |
| Lumen 全局光照 | 间接光真实 |
| Nanite 几何精度 | 几何细节 |
| 35mm Kodak 5219 胶片颗粒 | 胶片感颗粒 |
| 色彩空间 Rec.2020 | 广色域 |
| 皮肤纹理/发丝动态/汗渍血渍附着 | 生物细节 |
| 布料动力学真实 | 衣物物理 |
| 金属兵刃使用划痕与旧化质感 | 武器做旧，避免"全新塑料感" |

> **"使用划痕与旧化质感"这条很关键** —— 不写的话，模型容易给出崭新发亮的武器，立刻出戏。

---

## 二、英文版（Kling / H3）

```text
Photorealistic 3D CG, ultra-detailed 3D character modeling, PBR physical
materials, cinematic color grading, UE5 Path Tracing, Lumen global
illumination, Nanite geometric precision, 35mm Kodak 5219 film grain,
Rec.2020 color space, hyper-realistic skin texture, dynamic hair strands,
sweat and blood adhesion, realistic cloth dynamics, metal weapons with
usage scratches and aged patina
```

---

## 三、镜头参数补充（可选）

需要更明确的镜头语言时追加：

**中文**：
```text
广角等效24mm，F5.6光圈，1/125秒快门，照片级CGI，电影感景深
```

**英文**：
```text
Wide-angle equivalent 24mm, F5.6 aperture, 1/125s shutter, photorealistic
CGI, cinematic depth of field
```

---

## 四、关于"60帧"

样本原文写 `60帧`。**不要写进提示词**：

- MiniMax H3 固定 24fps，写 60 帧无效
- Kling 4.0 / Seedance 帧率由平台参数控制，不由提示词决定
- 写了反而可能让模型产生错误预期

**替代做法**：用 `全程强动态模糊+水墨速度线+TimeRamp快慢结合` 表达"高速运动感"，这是帧率无关的写法。

---

## 五、关于"8K"

同理。**保留但降格为风格词**：

- ✅ 可以写：`8K 3D CG 写实`（作为质感定位）
- ❌ 不要写：`输出 8K 分辨率`（模型做不到，三模型最高 4K 且仅 Kling 4.0）

`output_resolution` 是独立参数，在 `params` 里传给 API，不进提示词正文。
