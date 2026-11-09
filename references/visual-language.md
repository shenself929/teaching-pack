# Visual Language

> 图不是装饰。每张图都要回答一个具体问题；答不上来就别画。

---

## 1. 先选图型

| 要讲的东西 | 图型 | 工具 |
|---|---|---|
| 数据流/流水线 | 横向块图，箭头从左到右 | TikZ / drawio |
| 模型/系统架构 | 分层块图 + 局部放大 | TikZ / drawio |
| A vs B | 左右对照，共用坐标/尺度 | TikZ |
| 设计空间 | 2×2 矩阵，四角各一个策略 | TikZ |
| 时间/版本演化 | 纵向或横向时间线 | TikZ |
| 动态/迭代过程 | 可交互动画，有播放/暂停 | 单文件 HTML + SVG/JS |
| 定量结果 | 真实数据图，坐标轴/单位/图例 | matplotlib |
| 概念关系 | 有向图，边表示依赖 | TikZ / drawio |

---

## 2. 正式图的硬规则

- 正式讲义插图用 **TikZ 或 drawio**，不手绘 SVG，不用 AI 生成的结构图。
- 每张图必须有：
  - `.tex` 或 `.drawio` 源
  - `.pdf`（矢量）
  - `.png`（220 dpi 左右，供 Markdown 嵌入）
  - 中文图注
  - 一句“看什么”
- 图内文字不能溢出、重叠、被裁。
- 图注要自包含：不看正文也能知道图在讲什么。
- 图必须插入至少一篇文档；不能只躺在 `动画与图/` 里。
- 图片用 `[![alt](img)](img)` 包一层，点击打开原图。

---

## 3. TikZ 约定

从 `assets/tikz-preamble.tex` 复制：

```latex
\documentclass[border=2pt]{standalone}
\usepackage[UTF8]{ctex}
\setCJKmainfont{Microsoft YaHei}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,positioning,fit,backgrounds,shapes.geometric}
\usepackage{amsmath,amssymb}
```

颜色：

```latex
navy     #17324D
blue     #2F5597
midblue  #4A6FA5
paleblue #EDF3FB
orange   #B26A00
paleorange #FFF3E2
green    #2E7D32
palegreen  #ECF7ED
purple   #6D28D9
palepurple #F3E8FF
graytext #586575
panelborder #D8E0E9
```

规则：

- 用 `\useasboundingbox` 固定画布，避免裁剪。
- 节点文字用 `align=center`，长文本给 `minimum width`。
- 不要用 `step`、`out`、`cap` 等 TikZ 保留样式名。
- 中文文本里的 `%` 写成 `\%`，否则会当注释。
- 公式用 `$...$`，不要在 TikZ 节点里写 `\(...\)`。
- 编译后必须导出 PNG 检查。

---

## 4. drawio 约定

- 架构图/系统图优先 drawio；保留 `.drawio` 源。
- 导出 PNG（2x）和 PDF。
- 画布不要太大；图内字号 ≥ 12pt（导出后仍可读）。
- 箭头不要穿过文字；交叉线用跳线或分层。
- 图注写“这张图回答什么问题”，不是“系统架构图”。

---

## 5. HTML 动画约定

适用：滑窗、迭代、梯度流、状态机、时间推进、参数扫描。

必须：

- 单文件 HTML，无 CDN、无外部依赖，离线可打开。
- 有播放/暂停/重置；必要时有滑块。
- 一个动画只讲一个概念。
- 画面有标题、图例、当前数值。
- 中文标签；公式用 HTML/Unicode，不依赖 MathJax。
- 代码通过 `node --check`；用无头浏览器截图检查版面。
- 动画不是必须；没有动态概念就不做。

建议结构：

```text
标题
一句解释
[Svg 画布]
[播放/暂停] [滑块]
[当前数值/读数]
[一段“怎么读”]
```

---

## 6. 图注模板

```markdown
![图 2-1 小波 vs 傅里叶](../动画与图/TikZ/fig_wavelet_vs_fourier.png)

*图 2-1：傅里叶基是全局正弦，小波基是局部小波。看跳变附近：傅里叶出现全局振铃，小波只需少数局部系数。*
```

图注三件事：

1. 这张图是什么
2. 看哪里
3. 说明什么

---

## 7. 视觉验收

- [ ] 所有 `.tex` 编译通过
- [ ] 所有 `.png` 已重新导出
- [ ] 图内无文字重叠/出框/被裁
- [ ] 中文无乱码/缺字
- [ ] 图注与图内容一致
- [ ] 图已插入文档，路径正确
- [ ] 图片可点击
- [ ] 同一套图配色一致

渲染检查：

```bash
python scripts/compile_tikz.py --dir 动画与图/TikZ --dpi 220
```

然后逐张看 PNG；不要只看编译日志。
