<div align="center">

# wallstreetype-research

**把写研报，当成做软件工程来做。**

### *You can work for Wall Street.*

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![API keys](https://img.shields.io/badge/API%20keys-none-brightgreen)
![Markets](https://img.shields.io/badge/markets-US%20%7C%20A--share-orange)
![Styles](https://img.shields.io/badge/layout%20styles-6-9cf)
![Charts](https://img.shields.io/badge/chart%20families-5-purple)
![Pipeline](https://img.shields.io/badge/pipeline-S0--S9-black)
![Agent](https://img.shields.io/badge/works%20with-any%20AI%20agent%20%7C%20human-lightgrey)

[**中文**](README.md) · [English](README_EN.md) · [快速开始](#快速开始四步拿到一份成品) · [架构](#架构) · [成果展示](#成果展示跑出来的东西长这样)

</div>

---

## 这是什么

一个**把卖方研报生产流程工程化**的开源工具箱：输入契约、角色分工、质量门禁、交付规范，全部写成了可执行的脚本和文档。

它不教你「怎么看财报」，它给你一套**流水线**——从抓数据、算指标、画机构级图表，到套用匿名机构版式、导出带封面和评级框的 Word / PDF。研报的每一个数字都能追溯到一次真实的取数。

> **一句话**：别人给你一份研报，这里给你一台研报机器。装完就能跑，跑完就能交。

---

## 功能

按「研报从哪来 → 长什么样 → 谁来做 → 怎么交付」分成五层，每层都是独立可用的模块，也能串起来全自动跑。

| # | 模块 | 目录 / 入口 | 你能拿到什么 |
|---|---|---|---|
| 1 | **方法论库** | `methodology/` | 100 篇真实卖方研报的拆解清单（124 行）+ 10 组主题凝练 + 550 行《华尔街范式手册》——研究思路、证据纪律、红旗清单 |
| 2 | **双市场数据层** | `scripts/data/data_fetcher.py` | 美股 + A 股的报价 / 日线 / 财务，一条命令取数，**零 API key** |
| 3 | **机构级图表层** | `scripts/charts/report_charts.py` | 5 类可直接进研报的图：K 线+成交量、估值带、财务趋势、情景柱、同业对标 |
| 4 | **版式交付层** | `templates/` | 6 套匿名机构版式 + Markdown → Word / PDF 引擎（封面、评级框、Key Data、编号、目录、图表嵌入） |
| 5 | **研究流水线** | `pipeline/` | S0–S9 十阶段、8 个角色、7 道门禁、结构化交接工件——把「写研报」变成一条可复现的产线 |

**再加一条**：`VERIFICATION.md` —— 每一条产出对应的验收动作，包括最后一关的视觉校对（把成品渲染成图，让视觉模型逐页挑刺）。

---

## 快速开始：四步拿到一份成品

```bash
# 0. 依赖（pandas / matplotlib / python-docx / mplfinance 等）
pip install -r requirements.txt

# 1. 取数：A 股 / 美股，报价 / 日线 / 财务
python scripts/data/data_fetcher.py cn 600519 all --json        # 贵州茅台，全量
python scripts/data/data_fetcher.py us NVDA financials --json   # 英伟达，财务
export YAHOO_PROXY=socks5h://127.0.0.1:10808                    # 美股走代理（国内环境）

# 2. 写作：复制模板，填你的内容（YAML front matter 决定封面与评级框）
cp templates/report_template.md my_report.md

# 3. 出图：五类图表，一行一个
python scripts/charts/report_charts.py          # 全部样图写入 scripts/charts/sample_pngs/

# 4. 交付：Markdown → Word（+ PDF），套一套机构版式
python templates/md_to_docx.py my_report.md --style goldman_hardline --pdf --toc
```

**换版式只改一个参数：**

```bash
python templates/md_to_docx.py my_report.md --style barclays_cyanline   --pdf
python templates/md_to_docx.py my_report.md --style bernstein_monochrome --pdf
python templates/md_to_docx.py my_report.md --style ubs_swissminimal     --pdf
python templates/md_to_docx.py my_report.md --style /path/to/your_own.json --pdf
```

版式不是硬编码的——`templates/styles/*.json` 里是字体、配色、布局、表格、评级框、页眉的完整定义，抄一份改成你自己的就是新模板。

**想全自动跑完整条流水线？** 交给任意 AI agent（或你自己）：

```text
读 pipeline/pipeline_orchestration.md，
按 S0–S9 流程产出一份 XX 公司的深度研报，
版式用 ubs_swissminimal，双市场数据用 scripts/data/。
每个阶段的产物落到工作区，门禁不通过就退回重做。
```

---

## 架构

### 十阶段流水线（S0–S9）

```text
  S0 Intake            选题 + 版式问卷          ── 主编 ──▶ brief/intake.json
  S1 Input & Envelope  输入契约封装              ── 主编 ──▶ envelope.json
  S2 Master Brief      总纲撰写                  ── 主编 ──▶ briefs/master_brief.md
  S3 Parallel Research 三路并行尽调              ── 3 子代理 ──▶ 数据 / 行业 / 估值
  S4 Red Team Challenge 红队质询                 ── 1 子代理 ──▶ review/redteam.md
  S5 Editorial Adjudication 主编裁决             ── 主编 ──▶ decisions/decision.json
  S6 Charting          图表制作                  ── 1 子代理 ──▶ charts/manifest.json
  S7 Layout & Assembly 排版总装                  ── 1 子代理 ──▶ draft/report_draft.md
  S8 Final Review      终审                      ── 主编 ──▶ final/report.md
  S9 Proofing & QC     校对与视觉质检            ── 主编 + 视觉模型 ──▶ proof/visual_proofing.md

  门禁 G0 · G0b · G0c · G1 · G2 · G3 · G4 · G5 · G7   ← 不过就退回上一阶段
```

三种深度档位（快速简报 / 标准单公司 / 深度专题），同一套流程按档位裁剪，不是每次都跑满。

### 八个角色

| 角色 | 透镜 | 出场 |
|---|---|---|
| **主编 / Editor-in-Chief** | 全局、契约、裁决、终审 | 全程 |
| **数据工程师** | 数字从哪来、能不能复算 | S3 · S6 |
| **行业研究员** | 产业链位置、供需、竞争格局 | S3 |
| **估值研究员** | 倍数、DCF、可比公司 | S3 |
| **红队** | 只负责拆自己的台 | S4 |
| **图表师** | 一张图说一件事 | S6 |
| **排版师** | 版面、层级、留白 | S7 |
| **校对 / Proofreader** | 逐页视觉挑刺（含渲染放大复核） | S9 |

角色是**透镜边界**，不是头衔——同一个 agent 可以换帽子，但同一顶帽子不能既做多又做空。

### 目录结构

```text
wallstreetype-research/
├── methodology/                 方法论库：100 篇清单 + 10 组凝练 + 范式手册
│   ├── report_list_100.md
│   ├── digests/                 group1.md … group10.md
│   └── wallstreet_paradigm_manual.md
├── pipeline/                    流水线定义（agent 无关，任何模型都能跑）
│   ├── pipeline_orchestration.md  阶段规格 / 门禁 / 工件 schema
│   ├── agent_prompts.md           8 角色简报（中英双语）
│   └── intake.md                  选题与版式问卷
├── scripts/
│   ├── data/                    双市场实时取数（零密钥）
│   ├── charts/                  5 类机构级图表
│   ├── layout/                  版式引擎
│   └── intake/                  问卷与 brief 生成
├── templates/
│   ├── report_template.md       报告骨架（YAML front matter）
│   ├── md_to_docx.py            Markdown → Word / PDF（含封面、评级框、目录）
│   └── styles/*.json            6 套机构版式定义
├── examples/
│   ├── nvda_demo/               英伟达样例（9 页）
│   ├── layout_demo/             版式对照样例
│   └── unitree_vs_nvidia/       端到端案例：从取数到 PDF 全链路
├── docs/assets/                 README 用图（版式封面 / 案例成品）
├── VERIFICATION.md              验收清单
└── README.md / README_EN.md
```

---

## 六个版式模板

六套版式的视觉特征来自公开研报样本，**已去除全部机构名称与标识**，只保留排版语言。它们不是贴纸——每一套都是一份完整的字体 / 配色 / 布局 / 表格 / 评级框定义。

<table>
<tr>
<td width="33%" align="center"><img src="docs/assets/styles/goldman_hardline_cover.png" width="100%"><br><b>高盛 · 硬朗风</b><br><sub>开放式无框；衬线大标题；深蓝强调；水平细线分区；高信息密度</sub><br><a href="docs/assets/styles/goldman_hardline_page.png">内页 →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/morganstanley_restrained_cover.png" width="100%"><br><b>大摩 · 克制风</b><br><sub>大留白单栏；轻字重大标题；单一蓝色点缀；宽边距；封面感</sub><br><a href="docs/assets/styles/morganstanley_restrained_page.png">内页 →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/jpmorgan_heavyset_cover.png" width="100%"><br><b>小摩 · 厚重风</b><br><sub>高密度双栏；无衬线粗标题 + 衬线正文；灰底表头；紧凑行距</sub><br><a href="docs/assets/styles/jpmorgan_heavyset_page.png">内页 →</a></td>
</tr>
<tr>
<td align="center"><img src="docs/assets/styles/barclays_cyanline_cover.png" width="100%"><br><b>巴克莱 · 青蓝风</b><br><sub>青色页眉带；右侧浅蓝信息栏；青色表头白字；细字重标题</sub><br><a href="docs/assets/styles/barclays_cyanline_page.png">内页 →</a></td>
<td align="center"><img src="docs/assets/styles/bernstein_monochrome_cover.png" width="100%"><br><b>伯恩斯坦 · 学术黑白</b><br><sub>纯黑白；黑色顶栏；衬线正文；紧凑网格；零彩色元素</sub><br><a href="docs/assets/styles/bernstein_monochrome_page.png">内页 →</a></td>
<td align="center"><img src="docs/assets/styles/ubs_swissminimal_cover.png" width="100%"><br><b>瑞银 · 瑞士极简</b><br><sub>双层标题色带；深海军蓝 + 浅蓝；右侧信息栏；宽边距</sub><br><a href="docs/assets/styles/ubs_swissminimal_page.png">内页 →</a></td>
</tr>
</table>

> 以上十二张图是**同一篇报告**分别按六套版式渲染出来的第 1 页与内页，可直接点击查看原图。

---

## 成果展示：跑出来的东西长这样

**输入**（`examples/unitree_vs_nvidia/`）——一条 prompt 级别的规格：

| 项目 | 取值 |
|---|---|
| 标的 | 宇树科技 `688836.SH`（科创板）/ 英伟达 `NVDA`（NASDAQ）对比 |
| 数据 | A 股：腾讯财经 + 东方财富；美股：Yahoo Finance；汇率 USD/CNY |
| 硬约束 | **报告里每一个数字都来自真实取数，脚本内无一处手写** |
| 版式 | `goldman_hardline` |
| 产出 | Markdown 源 + Word + PDF + 6 张图表 + 原始 JSON + 逐页校对图 |

**产出**（全部在本仓库内，可直接点开）：

| 文件 | 说明 |
|---|---|
| [`unitree_vs_nvidia.pdf`](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf) | 成品报告，7 页，带封面 / 评级框 / Key Data / 6 张图表 |
| [`unitree_vs_nvidia.docx`](examples/unitree_vs_nvidia/unitree_vs_nvidia.docx) | 可继续编辑的 Word 版（2.3 MB） |
| [`unitree_vs_nvidia.md`](examples/unitree_vs_nvidia/unitree_vs_nvidia.md) | 源文件，含 YAML front matter |
| [`compute_numbers.py`](examples/unitree_vs_nvidia/compute_numbers.py) | 把原始 JSON 算成报告里用到的每一个数字 |
| [`make_case_charts.py`](examples/unitree_vs_nvidia/make_case_charts.py) | 六张图表（五张复用仓库既有图型） |
| [`data/`](examples/unitree_vs_nvidia/data) | 原始抓取 JSON + `numbers.json` |
| [`proof/`](examples/unitree_vs_nvidia/proof) | S9 逐页渲染校对图 |

<table>
<tr>
<td width="50%"><img src="docs/assets/case/case_page01.png" width="100%"></td>
<td width="50%"><img src="docs/assets/case/case_page03.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>封面：评级框 + Key Data + 价格走势，数据由脚本填入</sub></td>
<td align="center"><sub>内页：编号章节 + 表格 + 图表，均为导出引擎自动排版</sub></td>
</tr>
</table>

<table>
<tr>
<td width="33%"><img src="docs/assets/case/exhibit1_gap.png" width="100%"></td>
<td width="33%"><img src="docs/assets/case/exhibit2_kline.png" width="100%"></td>
<td width="33%"><img src="docs/assets/case/exhibit4_financials.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>同业对标（对数轴）</sub></td>
<td align="center"><sub>K 线 + 成交量</sub></td>
<td align="center"><sub>财务趋势（双轴）</sub></td>
</tr>
</table>

**跑一次的成本**（本机实测，Windows + 国内网络直连）：取数 **1.7 s** · 算数 **0.2 s** · 出图 **6.8 s** · 导出 Word/PDF **10.3 s**。

> 这个案例本身的分析内容写在报告里（[打开 PDF](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf)）。README 只负责回答一件事：**这东西跑出来是什么样**。

---

## 工程纪律

研报最容易崩的地方不是观点，是数字。这个仓库的几条硬规矩：

- **数据实时抓取，不合成**：`data_fetcher.py` 里没有 mock 分支，取不到就报错，不猜。
- **数字脚本化**：案例里每一个数字都由 `compute_numbers.py` 从原始 JSON 算出并落盘，报告与图表只读它。
- **零凭据**：只用公开行情接口，不需要 API key、不需要券商账号。
- **版式去机构化**：六套模板只保留排版语言，机构名称与标识全部移除（见 `templates/styles/*.json` 的 `_disclaimer`）。
- **交付前过视觉关**：S9 把成品渲染成 ≥144 DPI 图片逐页挑刺，疑点再放大 2 倍复核。
- **验收可查**：`VERIFICATION.md` 里每一条声明都对应一个可复现的动作。

---

## You can work for Wall Street

| 问题 | 回答 |
|---|---|
| 我没有金融背景，能用吗？ | 能。它的设计前提就是：华尔街的手艺可以被拆成步骤。方法论文档里写了每一类研报的思路、证据要求和红旗；剩下的是执行。 |
| 这套流程是「真研报」的流程吗？ | 结构、门禁、角色边界、交付规范对齐卖方实践；版式语言来自公开研报样本。至于研究结论值几个钱——市场说了算。 |
| 需要高级模型吗？ | 不需要。`pipeline/` 与具体模型解耦：能读写文件、能执行脚本的 agent 都能跑，纯人工流水线也成立。 |
| 能改成我自己的风格吗？ | 抄一份 `templates/styles/*.json` 改字体配色布局就是新模板；`md_to_docx.py --style /path/to/your.json` 直接生效。 |
| 数字会不会是编的？ | 案例里连「−53%」这种跌幅都是脚本算的。取数失败会报错，不会退化成占位符。 |

---

## 免责声明

本项目用于**研究流程与文档工程的方法示范**，不构成任何投资建议。数据来自公开接口，仅供参考，请以交易所与公司公告为准。版式模板为排版语言参考，不含任何机构名称或标识，与相关机构无关联、无背书。

## 许可

[MIT](LICENSE)
