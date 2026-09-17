# JACS-skills

[![Validate](https://github.com/Umbrellasoldier/JACS-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/Umbrellasoldier/JACS-skills/actions/workflows/validate.yml)

面向计算反应化学、化学机器学习和生物正交反应的论文写作与科研绘图技能包。
从作者事实起草、润色文字、制作可复现图表，并从可定位的 JACS 全文与实际图像中提炼规律。

**v0.2.0 新增 `jacs-figure`；语料结论仍限定在小规模试点。** 写作语料包含 34 篇候选题录、
8 篇开发组全文的结构化处理、35 条来源标注及 5 条条件式文风规则。
原始全文不随包分发；公开内容是题录、来源位置、哈希、原创观察和统计。
另有一篇留出论文用于写作评测，其内容未用于规则提炼。
绘图语料另行分组：14 篇论文、49 张已查看图像；其中 40 张用于开发／Communication 校准，
9 张用于规则冻结后的留出检查。提供六类化学绘图模板、SVG 组图及单独的 TOC 导出规格。

## 技能

| 技能 | 适用任务 |
|---|---|
| [`jacs-writing`](skills/jacs-writing/SKILL.md) | 根据作者事实、图表和中英文笔记起草或重构章节。 |
| [`jacs-polishing`](skills/jacs-polishing/SKILL.md) | 润色、翻译和精简已有文字，保持化学含义和证据范围。 |
| [`jacs-figure`](skills/jacs-figure/SKILL.md) | 设计、绘制、修改、检查和导出科研图；保持数据与化学身份。 |
| [`jacs-style-distill`](skills/jacs-style-distill/SKILL.md) | 获取／导入全文和图像，记录来源，提炼写作与绘图规律。 |
| [`jacs-shared`](skills/jacs-shared/SKILL.md) | 其他技能共用的期刊要求、化学语义、项目事实及语料参考。 |

要求、观察与事实分开管理：JACS 官方要求按文章类型和投稿阶段应用；样本文风规律作为
条件式建议；项目数据只来自作者材料。尤其检查能垒定义、候选生成与路径验证的区别、
参考答案后选与部署评估的区别，以及成功率分母和适用范围。

## 安装

需要 Python 3.10 或更新版本。安装器、语料获取和写作工具使用标准库；实际绘图另需下述可选依赖。

```bash
git clone https://github.com/Umbrellasoldier/JACS-skills.git
cd JACS-skills
python3 scripts/install_skills.py --destination "$HOME/.codex/skills"
```

安装器一起复制五个相邻技能目录并检查共享引用。遇到同名目录时默认停止；确认需要更新
这五个技能后可加 `--replace`。其他技能目录不受影响。也可以把五个目录整体复制到兼容
`SKILL.md` 的工具所使用的技能目录。新任务中按名称使用所需技能。

用法示例：

```text
使用 $jacs-writing，根据我的事实表和 Figure 2 起草 Results 段落。
保留已完成验证的范围，缺少的数据不要补写。

使用 $jacs-polishing，压缩以下段落，仅返回英文正文。

使用 $jacs-figure，根据这份预测表绘制 parity 和 residual 图，保留所有反应。
另外绘制分阶段成功率，明确每阶段分母，导出 PDF、SVG、PNG 和检查记录。

使用 $jacs-style-distill，从这些全文中分析引言末段和机理讨论的写法。
记录每条观察对应的 DOI 和段落位置。
```

项目配置从 [`examples/project-profile.json`](examples/project-profile.json) 开始。
模板没有研究结果；将作者确认的术语、事实和来源存入项目本地配置。

## 绘图

新建绘图默认使用 Python；已有 R 或化学绘图工程按原工作流处理。内置工具可直接运行：

```bash
uv sync --locked --group dev --group figures --group chemistry
uv run --locked --group figures --group chemistry python skills/jacs-figure/scripts/plot_figures.py skills/jacs-figure/assets/examples/energy.json --output local/energy
```

`figures` 提供 Matplotlib、PDF 检查和 SVG 组图依赖；`chemistry` 增加 RDKit。
安装器复制技能文件，不会替其他项目安装依赖。查看、规划或使用既有绘图环境不必重建环境。

| 模板 | 科学信息检查 |
|---|---|
| 能量剖面 | E/H/G、单位、参考态和条件；不自动换零点或混用单位 |
| Parity 与残差 | 同一反应集合、同一参考值、全部观测与描述性误差 |
| 分阶段统计 | 通过／失败／待完成守恒、条件分母与初始总体分母 |
| 方法比较 | 配对观测、明确总体；不凭空添加置信区间或显著性 |
| 流程／概念图 | 作者提供的过程与证据边界 |
| 化学结构 | 保留 SMILES、映射、立体化学；支持已有 SVG 结构资产 |

另支持 SVG 多面板组图，以及独立的 TOC 尺寸、字体和 TIFF 分辨率设置。
输出含 PDF、SVG、PNG、可重跑规格、图注和实际 QA JSON；TOC 自动附 TIFF。
结构模板生成二维图，三维 TS 面板需要真实结构和对应渲染器。
机械检查通过后仍须查看成图，`UNKNOWN` 项不视为通过。

见[原创合成示例](examples/figures/README.md)、[数据规格](skills/jacs-figure/references/figure-contract.md)、
[官方图形要求](skills/jacs-shared/references/graphics-policy.md)和[绘图评测](evaluation/figures/REPORT.md)。

## 语料与可追溯性

- [候选题录与获取状态](skills/jacs-shared/references/corpus-manifest.jsonl)：25 篇 Article、
  5 篇 Communication、4 篇 Perspective/Review。
- [试点观察和局限](skills/jacs-shared/references/pilot-findings.md)、
  [规则卡](skills/jacs-shared/references/style-rules.jsonl)、
  [来源标注](skills/jacs-shared/references/pilot-annotations.jsonl)、
  [描述统计](skills/jacs-shared/references/pilot-statistics.json)。
- [固定分组](evaluation/split.json)：18 篇 Article 开发候选、7 篇 Article 留出。
  Communication 和背景文章单列。
- [章节映射修正](corpus/section-overrides.json)：保留原始标题，修正 C03 的机器章节标签。

全文试点包含 A07、A10、B06、C03、C05、C06、C08、C10，其中三篇输入为作者稿。
研究年代为 2008–2023，主题与作者群分布不均；不据此宣称覆盖 JACS 全刊或确定当代统一用词。
Communication 的格式支持来自[官方要求快照](skills/jacs-shared/references/journal-policy.md)，
其文风尚无独立实证校准。

绘图的[论文清单](skills/jacs-shared/references/figure-corpus.jsonl)、
[40 条开发标注](skills/jacs-shared/references/figure-annotations.jsonl)、
[6 条条件式规则](skills/jacs-shared/references/figure-rules.jsonl)和
[覆盖范围与局限](skills/jacs-shared/references/figure-findings.md)独立管理，避免影响写作评测的固定分组。
图像只在本地查看，仓库不分发论文原图；公开示例全部为原创合成数据。

绘图来源使用当前 PMC Article Dataset 的版本化公开对象，记录 DOI、版本、文件哈希和实际查看状态。
旧 `oa.fcgi` 服务于 2026 年 8 月退役；获取命令见[图像语料流程](skills/jacs-style-distill/references/figure-workflow.md)。

结构化语料工具：

```bash
python3 skills/jacs-style-distill/scripts/corpus.py --help
python3 skills/jacs-style-distill/scripts/corpus.py fetch --manifest skills/jacs-shared/references/corpus-manifest.jsonl --paper-id C03 --output-dir local/C03
python3 skills/jacs-style-distill/scripts/corpus.py ingest --manifest skills/jacs-shared/references/corpus-manifest.jsonl --paper-id C03 --input local/C03/source.json --format bioc --source-url https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC3368396/unicode --output local/C03/blocks.jsonl
```

BioC JSON、JATS XML 和明确分节的 JSONL 均可导入；PDF 需先用可用工具提取并核验结构。
若需复现 C03 的试点分节，向 `--section-map` 提供该论文的标题映射对象；
完整试点重建由下列脚本自动应用仓库中的映射。

```bash
python3 scripts/rebuild_pilot.py --raw-dir local/corpus --output-dir local/rebuilt
```

重建需要匹配已记录哈希的八个 `PAPER_ID.bioc.json` 源文件；在线接口内容可能更新，
哈希不一致会要求核对版本。原始快照及私有项目事实保存在忽略的 `local/` 目录。

## 验证与开发

使用 [uv](https://docs.astral.sh/uv/) 和提交的锁文件运行开发检查：

```bash
uv sync --locked --group dev --group figures --group chemistry
uv run --locked --group dev --group figures --group chemistry python -m unittest discover -s tests -v
uv run --locked --group dev python scripts/validate_repository.py
uv run --locked --group figures --group chemistry python scripts/evaluate_figures.py --output-dir local/figure-evaluation
uv run --locked --group dev ruff check .
uv run --locked --group dev ruff format --check .
```

有本地标准化段落时可额外运行 `python scripts/validate_repository.py --source-blocks local/normalized`，
检查公开标注与实际文本的哈希及位置。测试使用合成数据和网络 mock，不需要 GPU 或私有文件。
有原图缓存时增加 `--figure-sources local/figures/sources` 可逐张核对开发标注的图像哈希。
未安装绘图可选依赖时，相应测试会跳过；CI 安装完整依赖并实际渲染。

[行为评测报告](evaluation/REPORT.md)区分工具测试、隔离上下文试写与有限样本的质量比较。
公开[任务输入](evaluation/requests.json)和实际输出支持复核；未验证的能力不计为已通过。

## 来源与许可

架构参考 [nature-skills](https://github.com/Yuan1z0825/nature-skills/tree/2375e0abdf42158ef149256f2c64b1f759a0d274)
的技能分工、按需读取、图形任务路由、实测 QA 和固定语料分组设计。
这里的化学工作流、规则、脚本和合成评测案例为独立编写。
来源说明见 [NOTICE](NOTICE)，代码与技能说明使用 [Apache-2.0](LICENSE)。
论文保留各自的来源与许可；本项目不是 ACS 官方产品。
