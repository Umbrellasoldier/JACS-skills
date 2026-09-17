# 本次技能使用与工具限制记录

按要求读取的是 `skills/jacs-figure/SKILL.md` 及其仓库内链接资源，没有使用 `<installed-skills>/` 的旧副本。读取内容覆盖 figure contract、chemistry figures、chart catalog、labels/layout/scale、color、visual rules、QA、chemistry semantics 和 graphics policy。确切文件哈希见 `source_index.json`；仓库工作区正处于开发评估，提交号不能单独代表所读技能版本。

1. 用户要同时保留反应配对、独立运行原始值和显式缺失矩阵。选择自定义 Matplotlib 组合图，以便在同一物理画布上直接排布三种证据并保留这些关系。没有把重复运行冒充独立反应，也没有删去重复 x 来适配 `curve` 输入。使用了技能提供的 `audit_figure.py` 与 `preview_color.py`，两者的实际副本保存在 `vendor/`。本次没有直接调用 `plot_figures.py` 的十种图型入口，因此本次行为验证不构成对全部模板接口的验证。
2. 首版使用 Matplotlib `imshow(interpolation='none')`；PDF 正常，但 CairoSVG 对 SVG 内极小嵌入矩阵的显示出现平滑。这是实际渲染后才发现的问题。已用 `pcolormesh` 输出矢量单元格；最终 PDF/SVG 无图像对象。对色标矢量条带设置同色边缘，消除了 SVG 渲染时可见的淡色接缝。
3. 内置审计没有全面检测文字与线条碰撞、语义正确性或所有字体嵌入。本次除了读取其结果，还检查 PDF/SVG 实际渲染与最终尺寸、导出的字体资源及图像对象数。没有把 `MECHANICAL_PASS` 写成全面科学认可，也没有声称人工审阅。
4. 编辑文本型 SVG 的字形与字重会受查看器和本机字体影响。CairoSVG 与 PDF 渲染的部分文字字宽略有差异，当前输出两者都清晰且无裁切；PDF 的字体嵌入已单独检查。若换字体或缩小版式，需再次核查。
5. 所给误差只有数值和单位，减法方向及被预测的能量量未说明。采用 “Signed error” 并在图注和契约记录未知项；不解释正负为过预测/欠预测。学习文件的 MAE 原样使用，不能从现有信息反推单次运行的测试集规模或误差分布。转移表无每类 n 或重复信息，因此没有构造不确定性或加权总体指标。
6. 三份数据的跨文件评价人群关系未知；只在 `prediction_errors` 内使用已明确的反应配对。所有统计均是合成输入的描述，未调用拟合、假设检验、引导法或外推。没有从图形模式推导实际科研机制或泛化结论。

没有缺失依赖或需要用户补充才能完成的绘图障碍。没有改变原始文件、技能文件或其他跟踪文件；输出都位于当前交付目录。
