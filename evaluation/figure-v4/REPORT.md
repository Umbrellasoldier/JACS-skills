# v0.4 绘图修复与验证

本轮把 v0.3 图库批评落实到技能指引、可执行模板和 17 张示例：补齐交付图注，
减少重叠与无效色块面积，让组图围绕同一批反应回答一个问题。
可浏览[新版图库](../../examples/figures/README.md)和[绘图技能](../../skills/jacs-figure/SKILL.md)。
所有示例及独立测试均使用合成数据。

## 修改与证据

| 已发现的问题 | 本轮修复 | 可复核对象 |
|---|---|---|
| 统计定义只存在 JSON 中，导出的图注不完整 | 将已提供的样本量、观察单位、区间、参考态、归一化和误差摘要带入图注；保留作者原文 | [图注生成器](../../skills/jacs-figure/scripts/figure_caption.py)、[学习曲线图注](../../examples/figures/learning.caption.txt) |
| 组图拼接后丢失子图含义，面板缺少共同问题 | 新增原生 `panel_grid`，逐面板保留定义；示例使用同一批 72 个反应的有符号误差与绝对误差 ECDF | [组图规格](../../skills/jacs-figure/assets/examples/showcase.json)、[组图图注](../../examples/figures/showcase.caption.txt) |
| 配对观测中的相同值互相遮住 | 按反应 ID 使用跨方法一致的类别轴错位，保留真实数值和配对关系 | [配对图](../../examples/figures/comparison.png) |
| 密集一致性散点相互遮挡，残差难比较 | 按方法分面；共享数值范围，配合形状编码和误差摘要；对齐上下两行绘图区 | [一致性图](../../examples/figures/agreement.png) |
| 填色面积和点密度仍显厚重 | 降低支持填色强度、缩小空心点；半小提琴与原始点分置两侧；直方图改为轮廓 | [小提琴图](../../examples/figures/violin.png)、[直方图](../../examples/figures/histogram.png) |
| 小矩阵占据过多面积，缺失值表达不够明确 | 热图高度由 185 降至 128 pt；四个色标刻度；缺失使用斜线加 NA，即使关闭数值标注仍可识别 | [热图](../../examples/figures/heatmap.png)、[图注](../../examples/figures/heatmap.caption.txt) |
| ECDF 所回答的问题不明确，密度形状可能过度解读 | 显式选择绝对误差变换、保留原值和共同尾部；小提琴记录原带宽与加倍带宽下的模态敏感性 | [统计模板](../../skills/jacs-figure/scripts/statistical_figures.py)、[选图指引](../../skills/jacs-figure/references/chart-catalog.md) |
| 归一化、刻度和统计带缺少充分说明 | 光谱按各序列采样最大值显式归一化并保留 `raw_y`；学习曲线保留重复值、说明均值 ± SD，按真实对数位置标刻度 | [光谱规格](../../skills/jacs-figure/assets/examples/spectra.json)、[学习曲线](../../examples/figures/learning.png) |
| TOC 过于泛化，结构与化学问题关联弱 | 加入丁二烯与乙烯环加成的具体连接关系和两条新 C–C 键；保留清楚的示意边界 | [TOC](../../examples/figures/toc.png)、[化学图指引](../../skills/jacs-figure/references/chemistry-figures.md) |

[数值保留核对](data-preservation.json)比较了 v0.3.0 的 12 个数值示例。
原有能量、预测值、配对误差、分布观测、区间、热图和学习曲线统计量均保留。
光谱保留归一化前值；ECDF 的绝对值是明确声明的显示变换。新组图从一致性示例的
72 × 3 组预测／参考对派生。修复没有靠删除异常值或捏造样本量改善外观。

## 程序检查与实际看图

| 检查 | 结果与范围 |
|---|---|
| 回归测试 | 71 项通过；包括导出图注、再次渲染、外置 SVG 图注随包保留、相同配对值、ECDF 重复值与尾部、缺失标识、共享坐标范围和归一化 |
| 机械验收 | 12/12 通过，包括无效输入拒绝；[结果](acceptance-results.json) |
| 仓库检查 | 技能引用、语料身份及分组、冻结哈希、Ruff 和格式检查通过；依赖版本未变化 |
| 图库机械审计 | 15 张 `MECHANICAL_PASS`；结构图与 TOC 保留 `REVIEW_REQUIRED`，其对象级碰撞需要实际查看 |
| 实际导出审阅 | 主代理查看全部 17 张最终 PDF 的页面渲染与 96 dpi 缩放预览；另看组图、一致性图、学习曲线和区间图的 SVG 渲染 |
| 颜色预览 | 主代理查看组图、一致性图、热图、小提琴图和流程图的灰度及三类色觉模拟，共 20 张；[方法与源哈希](color-checks.json) |

逐图尺寸、字体测量、审计结果、图注及输出哈希见 [gallery-checks.json](gallery-checks.json)。
抽取到的最小字形包含数学上标，不能当作正文／轴标题字号。预览未发现文字裁切；
一致性图上下行的左右边界已对齐；半小提琴的观测点不再埋在密度填色里。
三型色觉模拟中部分蓝绿颜色趋近，分面位置、点形和线型仍提供区分。
这些检查没有覆盖实体印刷、所有查看器或最终稿件中图与图注的联合排版。
色觉模拟也不等于用户可访问性研究。

## 独立使用测试

一个不带此前批评结论的独立代理读取冻结技能快照，根据
[任务](forward/input/request.md)、[48 个反应](forward/input/predictions.csv)和
[量的定义](forward/input/context.json)自行选图。它交付两个共享坐标的残差面板和一个
绝对误差 ECDF，使用全部 48 个匹配反应；低、中、高三个等数量分组各 16 个。

主代理从原 CSV 用十进制减法独立重算所有总体及分组统计、每个 ECDF 跳点与阈值计数，
均与输出一致。A、B 的 MAE 分别为 1.05625 和 0.57917 kcal mol⁻¹；
B 的高参考能垒组平均有符号误差为 +0.84375 kcal mol⁻¹。
这些只是合成数据的描述结果，分组不代表已确立的化学区间。

主代理另看了交付 PNG、PDF 的 96 dpi 预览和 SVG 渲染，并将完整输出复制到新目录，
从另一工作目录重新执行。PDF、SVG、PNG、图注均逐字节一致；
[独立核算与重跑记录](forward-checks.json)保留哈希。
[完整测试包](https://github.com/Umbrellasoldier/JACS-skills/releases/download/v0.4.0/figure-v4-forward.zip)
含冻结技能、输入、程序、图件和验证记录。

该案例检验了技能在新任务中的使用，使用的是自写 Matplotlib 程序与技能审计工具，
没有验证所有模板入口。冻结快照早于最后的一致性图行高、结构边检查和对数绝对值校验修正；
差异记录于 [snapshot-differences.json](forward/snapshot-differences.json)。最终模板另由回归测试和图库覆盖。
本轮没有进行有／无技能的盲审对照，不能据此报告审美胜率。

## 使用与兼容性

完整图库包：[jacs-figures-v0.4.0.zip](https://github.com/Umbrellasoldier/JACS-skills/releases/download/v0.4.0/jacs-figures-v0.4.0.zip)。
仓库内发布 PNG、可编辑 SVG 和 `.caption.txt`；包内另含 PDF、规格、审计和源码。

旧 `assembly` 规格的每个子面板现在必须提供 `caption` 或 `caption_file`；
已有内容可直接迁入。新 `panel_grid` 会带上子图定义，详见
[输入约定](../../skills/jacs-figure/references/figure-contract.md)。程序会保留已知定义，
不能判断作者给出的定义是否真实，也不会凭空补齐缺失的参考态、样本量或不确定性模型。
热图仍是没有逐反应样本量的合成汇总；能量图仍是能级表达教学例子。

文献基础仍是 v0.3 的 50 篇／199 幅；本轮没有新增文献阅读，也未重验全部本地原图哈希。
既有不利评测和文献来源保持原样。Data 的选图、数据完整性和交付验证原则继续按
[适配表](../../skills/jacs-figure/references/data-design-patterns.md)使用；配色与布局选择不冒充 ACS 强制政策。

复核命令（仓库根目录）：

```bash
uv sync --locked --group dev --group figures --group chemistry
uv run --locked --group dev --group figures --group chemistry python -m unittest discover -s tests -v
uv run --locked --group figures --group chemistry python scripts/evaluate_figures.py --output-dir local/figure-v4/acceptance
uv run --locked --group figures --group chemistry python scripts/build_figure_gallery.py
uv run --locked --group dev python scripts/validate_repository.py
uv run --locked --group dev ruff check .
uv run --locked --group dev ruff format --check .
```
