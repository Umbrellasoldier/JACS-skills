# v0.3 绘图升级与验证

本轮完成淡亮配色、图型词汇、标签／图例／字号／尺度／排版规则及可执行模板升级。
以下分别记录文献学习、程序检查和真实使用测试；没有把其中一种验证当作另一种。

## 文献图像学习

| 范围 | 论文 | 实看唯一图号 |
|---|---:|---:|
| v0.2 已有证据 | 14 | 49 |
| v0.3 新开发集 | 30 | 127 |
| v0.3 新留出集 | 6 | 23 |
| 累计 | **50** | **199** |

本轮新增 36 篇／150 幅，均验证 JACS DOI、JATS Article 身份和 PMC publisher version。
六个主题检索形成候选框，按题目选样并先冻结分组；规则在留出图像查看前冻结。
[协议](PROTOCOL.md)、[冻结哈希](rule-freeze.json)、[覆盖计数](coverage.json)、
[逐图留出观察](heldout-observations.jsonl)与[留出检查](heldout-review.json)可复核。
150 幅新图和 49 幅旧图的本地字节均核对了公开记录中的 SHA-256。

这是偏向近期开放获取论文的有目的样本，不是期刊随机样本。开发与留出作者的规范化姓名有一处重合
（Huse Nils），课题组独立性未验证。条形、曲线等家族允许重叠；“31 项目录”不是 31 个互斥统计类别。
阅读整幅多面板图不等于测量了每个面板的全部字体和线宽。

[六篇 PDF 实测](pdf-audit.json)记录图像对象尺寸与来源哈希，所选图内字均已栅格化，字号与字体未知。
新版 7–9 pt 等建议是项目起始值，不是伪造的论文平均值。完整题录与设计发现见
[学习记录](../../skills/jacs-shared/references/figure-study-v3.md)。旧版的冻结文件和评测保持原样。

## 程序与成图验证

- 59 项单元／集成测试通过，包括实际导出。新增测试核对离群点保留、真实箱须端点、ECDF 重复值、
  直方边界归属和排除拒绝、区间定义、混合单位、曲线 x 次序／误差带／对数域、缺失与零，以及热图矢量输出。
- 12/12 机械验收任务通过，含错误输入拒绝；这不是审美通过率。
- 仓库引用、论文身份、分组、冻结哈希、来源文件、Ruff 检查与格式检查通过。
- 17 幅图库示例均实际渲染并查看 PDF 页面和 PNG；15 幅 `MECHANICAL_PASS`，
  `structures` 与 `showcase` 的对象级布局仍报告 `REVIEW_REQUIRED`，另行实际查看未发现遮挡。
  图件尺寸、文件哈希和审计结果见 [gallery-checks.json](gallery-checks.json)及
  [图库清单](../../examples/figures/manifest.json)。不把未实现的化学结构／碰撞检查改写成自动通过。
- 修复了 SVG 组图中单位上标负号显示不清，改用数学排版；确认最终单位可见。
  热图采用离散矢量色块和矢量色标，避免小位图的查看器插值。

所有示例为确定性合成数据，图内均明确标注。默认导出 PDF/SVG/PNG，TOC 附 TIFF；可重跑规格、
图注、源哈希和统计定义随本地完整 bundle 保存。绘图库中的小矩阵缺失格为灰色破折号，数值 0 与缺失不同。
学习曲线的带是八次合成运行的均值 ± 样本 SD；区间例子是给定示意上下界，没有宣称它们是 CI。

复核命令：

```bash
uv run --locked --group dev --group figures --group chemistry python -m unittest discover -s tests -v
uv run --locked --group figures --group chemistry python scripts/evaluate_figures.py --output-dir local/figure-v3/acceptance
uv run --locked --group dev python scripts/validate_repository.py --figure-sources local/figures/sources --figure-v3-sources local/figure-v3/sources
uv run --locked --group dev ruff check .
uv run --locked --group dev ruff format --check .
```

CI 另在 Python 3.10／3.11 执行相同核心检查；以相应 GitHub Actions 运行结果为准。

## 配色与视觉边界

采用浅蓝、杏、青绿、淡紫、玫瑰和米金填色，配相应较深轮廓和深灰文字。并非每张图都使用六色。
[亮度对比测量](color-contrast.json)：深灰正文对白底约 11.21；对六种填色约 6.37–8.13；
轮廓对白底约 3.18–4.13。这些是 sRGB 亮度比，不是完整可访问性认证。

实际查看了 showcase、agreement、energy、ECDF、workflow、stages 的灰度及三类 severity=100
色觉模型预览；[示意组图](color-review/showcase-contact.png)和逐图源哈希保存在 color-review。
灰度中不同浅色会接近；蓝与青绿在 tritan 模型下也会接近。类别位置、圆／方／三角、虚实线、
阶段填充纹理和明确标签因此是必要信息。能量路径使用不同连接线型；示意连接仍不代表真实 IRC。

高密度 parity 点在灰度中逐个识别方法仍费力，真实大样本应按问题考虑分面或密度显示。
叠加直方填色会混合，ECDF 提供了不依赖重叠面积的替代。色觉模拟和代理目视检查不证明所有人
都觉得舒适；没有进行受试者偏好实验，也没有宣称 v0.3 的审美一定优于所有其他方案。

## 独立真实使用测试

按 skill-creator 的复杂技能验证流程，向独立代理提供[新请求及原始合成数据](forward-output/data/request.md)、
当前技能和依赖环境，不提供目标答案或缺陷提示。它自行选择箱线／配对原始点、运行散点＋均值 SD、
显式缺失矩阵，在自定义 Matplotlib 画布排成三面板，并使用技能的审计和色觉工具。

另一个代理从原始数据独立重算、核对 SVG 坐标、查看实际格式并在临时目录重跑。
[独立复核](independent-review.md)未发现数据或统计错误：108 个误差点、120 个运行值和一处缺失均保留，
PDF/SVG/PNG 可逐字节复现。该检查发现 b 面板的小 SD 棒会受到较大均值标记和运行点影响，
这是需要注意的可读性限制。原输出和报告保持不变；通用指导补充了比较误差棒长度与标记直径的建议，
其后续改善效果没有重新用此任务冒充独立验证。

[输出归档](forward-output/ARCHIVE.md)保留脚本、数据、摘要、图注、技能哈希和 QA。
一次使用测试只验证这条工作流；它没有直接调用全部模板，不构成对 v0.2 的盲法审美对照。
[v0.2 原有不利盲评](../figures/REPORT.md)没有被删除或改写。

## Data 设计模式

参考用户明确指定的 Data 1.0.8 中 visualize-data、validate-data 和 analysis-quality：按分析关系选图，
明确独立单位与总体，保留数字结构，规范缺失／不确定性，检查实际导出。
[适配说明](../../skills/jacs-figure/references/data-design-patterns.md)区分 Data 工作流、文献观察、
ACS 规则和本项目偏好；没有把仪表板品牌布局当作期刊惯例。
