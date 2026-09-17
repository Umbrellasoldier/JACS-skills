# 淡亮风格的科研图示例 · v0.3

17 幅原创示例，全部是**合成演示，不是研究结果**。轻填色、清晰轮廓、深灰文字与形状／线型一起传达信息。
页面显示的是浏览器预览，实际出版尺寸由 JSON 规格控制。PDF、SVG、PNG、图注、数据规格和 QA 可用下方命令完整生成。

## 多面板示例

![分布、学习曲线、区间与矩阵的合成组图](showcase.png)

[SVG](showcase.svg) · 四个面板分别演示互补的分析关系；不暗示这些合成数据构成同一个真实化学实验。
图中一处灰色缺失格不是零；点和带的统计定义见相应规格及图注。组图生成步骤在
[复现脚本](../../scripts/build_figure_gallery.py)。

## 图库与数据规格

| 图型 | 可复现规格 | 矢量 | 预览 |
|---|---|---|---|
| 箱线图 + 原始点 | [JSON](../../skills/jacs-figure/assets/examples/boxplot.json) | [SVG](boxplot.svg) | [PNG](boxplot.png) |
| 小提琴 + 中位数 | [JSON](../../skills/jacs-figure/assets/examples/violin.json) | [SVG](violin.svg) | [PNG](violin.png) |
| 经验累积分布 | [JSON](../../skills/jacs-figure/assets/examples/ecdf.json) | [SVG](ecdf.svg) | [PNG](ecdf.png) |
| 共享分箱直方图 | [JSON](../../skills/jacs-figure/assets/examples/histogram.json) | [SVG](histogram.svg) | [PNG](histogram.png) |
| 点与区间 | [JSON](../../skills/jacs-figure/assets/examples/intervals.json) | [SVG](intervals.svg) | [PNG](intervals.png) |
| 学习曲线 + SD 带 | [JSON](../../skills/jacs-figure/assets/examples/learning.json) | [SVG](learning.svg) | [PNG](learning.png) |
| 逆向光谱坐标 | [JSON](../../skills/jacs-figure/assets/examples/spectra.json) | [SVG](spectra.svg) | [PNG](spectra.png) |
| 热图 + 显式缺失 | [JSON](../../skills/jacs-figure/assets/examples/heatmap.json) | [SVG](heatmap.svg) | [PNG](heatmap.png) |
| 一致性散点 + 残差 | [JSON](../../skills/jacs-figure/assets/examples/agreement.json) | [SVG](agreement.svg) | [PNG](agreement.png) |
| 能量剖面 | [JSON](../../skills/jacs-figure/assets/examples/energy.json) | [SVG](energy.svg) | [PNG](energy.png) |
| 小样本 parity | [JSON](../../skills/jacs-figure/assets/examples/parity.json) | [SVG](parity.svg) | [PNG](parity.png) |
| 分阶段去向 | [JSON](../../skills/jacs-figure/assets/examples/stages.json) | [SVG](stages.svg) | [PNG](stages.png) |
| 配对观测比较 | [JSON](../../skills/jacs-figure/assets/examples/comparison.json) | [SVG](comparison.svg) | [PNG](comparison.png) |
| 流程示意 | [JSON](../../skills/jacs-figure/assets/examples/workflow.json) | [SVG](workflow.svg) | [PNG](workflow.png) |
| 二维立体化学结构 | [JSON](../../skills/jacs-figure/assets/examples/structures.json) | [SVG](structures.svg) | [PNG](structures.png) |
| TOC 概念图 | [JSON](../../skills/jacs-figure/assets/examples/toc.json) | [SVG](toc.svg) | [PNG](toc.png) |

## 更多预览

![一致性散点与残差](agreement.png)

![小提琴与全部观测](violin.png)

![光谱和虚实线](spectra.png)

![阶段统计与分母](stages.png)

## 复现与使用

从仓库根目录运行：

```bash
uv sync --locked --group figures --group chemistry
uv run --locked --group figures --group chemistry python scripts/build_figure_gallery.py
```

完整输出在忽略的 `local/figure-v3/gallery/`。`--publish` 仅把原创 PNG/SVG 更新到本目录，
同时重置 visual_review 为待检查；图变更后必须重新看图，不能沿用旧验证结论。
单图可用技能中的 `plot_figures.py` 及 JSON；改变 `data_status` 不能把合成数据变成真实数据。

```bash
uv run --locked --group figures python skills/jacs-figure/scripts/plot_figures.py skills/jacs-figure/assets/examples/boxplot.json --output local/my-boxplot
uv run --locked --group figures python skills/jacs-figure/scripts/preview_color.py local/my-boxplot.png --output-dir local/color-review
```

TOC 同时导出 TIFF。结构例子只显示二维立体化学，不代表优化几何。
机械检查和实际视觉检查的边界见[新版验证记录](../../evaluation/figure-v3/REPORT.md)。
[图型选型](../../skills/jacs-figure/references/chart-catalog.md)、[淡亮配色](../../skills/jacs-figure/references/color-design.md)与
[标签／字号／尺度／排版](../../skills/jacs-figure/references/labels-layout-scale.md)给出选择依据。
