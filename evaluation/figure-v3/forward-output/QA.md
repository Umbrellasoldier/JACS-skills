# 成图 QA

本次检查由绘图代理执行，未声称经过人工审稿。记录对应最终 `figure.pdf` 的 SHA-256：

`fe855c8bb6bfec7fcb493bfe73416127cf4a94335565e450f56ec56ac56ad7cf`

| 检查 | 实际结果 |
|---|---|
| 输入与配对 | 108 条误差、36 个共同反应 ID；反应/方法键无重复；无删除或非有限数值 |
| 学习统计 | 120 条原始 MAE，15 组，每组 8 次运行；均值与 `ddof=1` 的 SD；没有把 SD 写成 CI |
| 电荷矩阵 | 5 个观测值、1 个未评估单元格；保留 null 语义；色标 0–3 覆盖全部值 |
| 成图尺寸 | PDF 和 SVG 均为 504 × 360 pt；PNG 为 2100 × 1500 px，约 300 dpi |
| PDF 字体 | 最小可提取文字 7.3 pt；DejaVu Sans 和 DejaVu Sans Bold 的字体流均嵌入 |
| 矢量对象 | 最终 PDF 图像对象数为 0；SVG `<image>` 数为 0，保留 51 个文字元素 |
| 机械布局 | 文本边界检查无裁切或文本重叠；`MECHANICAL_PASS`，无 `UNKNOWN` 项 |
| 实际视觉检查 | 查看 PDF 的 144 dpi 渲染、96 dpi 尺寸预览、SVG 的独立 CairoSVG 渲染以及交付 PNG；未见标签裁切、单位缺字或跨面板遮挡 |
| 色觉检查 | 查看最终 PDF 渲染的灰度、protan、deutan、tritan 模拟；方法由形状/线型/位置辅助识别，热图有数值和缺失文字 |

相关证据在 [qa/mechanical.json](qa/mechanical.json)、[qa/data_checks.json](qa/data_checks.json)、[qa/artifact_hashes.json](qa/artifact_hashes.json)、[qa/final-size-96dpi.png](qa/final-size-96dpi.png)、[qa/svg-render-144dpi.png](qa/svg-render-144dpi.png) 和 [qa/color-contact-sheet.png](qa/color-contact-sheet.png)。

实际视觉复查发现首版 SVG 的 3 × 2 热图通过极小嵌入位图导出后出现平滑色阶。已改为离散矢量色块，色标也使用矢量条带并消除条带接缝；修复后重新生成和检查全部格式。最终 SVG 和 PDF 的类别色块均保持均匀，不在类别之间插值。

配对连接线在误差接近零的区域较密，但作为浅色背景仍可看见箱体与原始符号；所有尾部观测均在轴范围内。学习曲线的运行点在相同训练规模上有覆盖，这是保留真实坐标的结果；每组 8 次运行和汇总定义已显式注明。a/b 上沿、a/c 下沿按实际绘图区对齐；面板的量和用途不同，没有要求等高。

机械审计仅覆盖其支持的尺寸、文字和布局检查；本记录另补实际渲染查看及字体/矢量对象检查。色觉模拟是模型预览，不是全面可访问性认证。研究条件、误差减法方向、类别样本量等未给出的科学信息仍为未知。图件使用技能中提供的 JACS 尺寸快照作版式参考；图和最终排版图注的总高度没有组版验证，未把本次演示交付当作投稿包认证。
