# 合成方法评估图

本目录是可复现的三面板绘图交付包，全部输入均为合成演示。图件明确标记 **SYNTHETIC DEMONSTRATION · NOT RESEARCH RESULTS**，不作为课题研究结论。

| 文件 | 用途 |
|---|---|
| [figure.pdf](figure.pdf) | 504 × 360 pt、7 × 5 in 的双栏矢量图，已检查实际 PDF |
| [figure.svg](figure.svg) | 同尺寸矢量图，保留可编辑文字 |
| [figure.png](figure.png) | 2100 × 1500 px、300 dpi 彩色预览 |
| [caption.md](caption.md) | 自包含英文图注及统计定义 |
| [render.py](render.py) | 完整绘图、统计汇总、数据和机械 QA 脚本 |
| [figure.spec.json](figure.spec.json) | 图件契约、面板职责、配色、未知项和统计选择 |
| [source_index.json](source_index.json) | 原始输入、技能和工具来源，以及 SHA-256 |
| [error_summary.csv](error_summary.csv) / [learning_summary.csv](learning_summary.csv) | 未截断精度的描述统计 |
| [environment.json](environment.json) / [requirements.txt](requirements.txt) | Python 与包版本、脚本哈希 |
| [QA.md](QA.md) / [LIMITATIONS.md](LIMITATIONS.md) | 实际图件检查及工具限制 |

面板 a 保留同一批 36 个反应的配对关系与全部 108 个误差值。箱体、箱内中线和须分别表示 Q1–Q3、中位数、以及 1.5 IQR 范围内最远的观测值；四分位数采用 NumPy 的线性插值定义。类别方向的确定性抖动仅用于减少覆盖，同一反应在三种方法下使用相同偏移。原始误差的减法方向未知，因此仅标记为 signed error，没有据其正负解释过高或过低预测。Direct 的一个箱须外观测保留。

面板 b 使用全部 120 个原始运行 MAE，构成 3 种方法 × 5 个训练规模 × 8 次独立运行。小空心符号是原始运行；大实心符号是这 8 个已给出 MAE 的算术平均，误差棒为均值 ± 样本标准差 `s = sqrt(sum((x − mean)^2) / 7)`。同一 x 值上允许观测重叠；不对数值坐标添加抖动，也不把运行编号当作跨方法的配对。线段只连接均值用于引导视线；没有拟合或外推。

面板 c 原样使用 5 个已给出的类别 MAE。Calibrated/Charged 的 `null` 以灰色斜线及“Not evaluated”文字表示；没有把它填成 0，也没有推断该方法在带电类别上的表现。该表未给出样本量或重复运行，因此不生成误差条、不跨类别加权汇总。

`error_summary.csv` 额外提供可核查的描述量：`MAE = mean(abs(error))`，`RMSE = sqrt(mean(error²))`。它们基于面板 a 的 36 个误差，不能与另两份独立来源数据混合汇总。

| 方法 | 反应数 | 误差中位数 / kcal mol⁻¹ | MAE / kcal mol⁻¹ | RMSE / kcal mol⁻¹ |
|---|---:|---:|---:|---:|
| Direct | 36 | 0.038 | 1.689 | 2.256 |
| Adapted | 36 | −0.125 | 0.840 | 1.067 |
| Calibrated | 36 | 0.212 | 0.597 | 0.723 |

本表仅为合成输入的算术描述。没有显著性检验、置信区间、真实泛化能力结论或补造研究条件。

## 重现

在项目现有环境运行：

```bash
.venv/bin/python local/figure-v3/forward-output/render.py
```

复制整个目录后，也可在具有 `requirements.txt` 所列版本的 Python 环境中运行 `python render.py`。脚本只使用相对于自身目录的输入副本和工具，校验 `source_index.json` 中的输入/工具哈希，随后重新输出图件、数据摘要、机械 QA 和色觉预览。输入副本与原始输入逐字节一致。

复现会更新程序生成的检查文件；手工撰写的 `QA.md` 仅适用于其中记录的图件哈希。若改动脚本、字体、数据或布局，需要再次检查新成图。SVG 使用 DejaVu Sans，查看或编辑时需要可用的对应字体；PDF 已嵌入本次使用的两种字体。
