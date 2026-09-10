<div align="center">

<img src="docs/assets/hero.png" width="100%" alt="wallstreetype-research">

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![API keys](https://img.shields.io/badge/API%20keys-none-brightgreen)
![Markets](https://img.shields.io/badge/markets-US%20%7C%20A--share-orange)
![Layouts](https://img.shields.io/badge/layout%20styles-6-9cf)
![Charts](https://img.shields.io/badge/chart%20families-5-purple)
![Agent](https://img.shields.io/badge/works%20with-any%20AI%20agent%20%7C%20human-lightgrey)

[**中文**](README.md) · [English](README_EN.md) · [功能](#功能) · [快速开始](#快速开始) · [用法](#用法) · [架构](#架构) · [版式模板](#六套版式模板) · [成果展示](#成果展示) · [文档](#文档导航)

</div>

---

## 这是什么

**wallstreetype-research** 是一套把卖方研报生产流程工程化的开源工具箱：给它一个标的，它给你一份能直接交出去的研报——带封面、评级框、Key Data、编号章节、机构级图表，导出 Word 和 PDF。

方法论、取数、图表、版式、质量门禁都已经写成**可执行的脚本和文档**，而不是写在文章里。流程与模型解耦：任何能读写文件、能跑脚本的 AI agent 都能驱动它，人工照着文档走一遍同样成立。

---

## 功能

- 📚 **方法论库** — 100 篇卖方研报拆解清单（124 行）+ 10 组主题凝练 + 550 行《华尔街范式手册》：研究思路、证据纪律、红旗清单。 → [`methodology/`](methodology)
- 📈 **双市场数据层** — A 股 + 美股，报价 / 日线 / 财务，一条命令取数，**零 API key**。 → [`scripts/data/`](scripts/data)
- 📊 **五类机构级图表** — K 线+成交量、估值带、财务趋势（双轴）、情景柱、同业对标，统一样式与配色。 → [`scripts/charts/`](scripts/charts)
- 🔀 **S0–S9 研究流水线** — 10 个阶段 / 8 个角色透镜 / 8 道质量门禁 / 结构化交接工件。 → [`pipeline/`](pipeline)
- 📄 **Markdown → Word / PDF 引擎** — 自动生成封面、评级框、Key Data 表、目录、编号章节、图表嵌入，中英文字体自适应。 → [`templates/md_to_docx.py`](templates/md_to_docx.py)
- 🎨 **六套机构版式** — 每套都是字体 / 配色 / 布局 / 表格 / 评级框的完整 JSON 定义，改一份就是新模板；机构名称与标识已全部移除。 → [`templates/styles/`](templates/styles)
- ✅ **可验收** — 每条产出对应一个可复现动作，最后一关把成品渲染成图、逐页视觉挑刺。 → [`VERIFICATION.md`](VERIFICATION.md)

---

## 快速开始

```bash
# 0. 安装依赖（pandas / matplotlib / python-docx / mplfinance 等）
pip install -r requirements.txt

# 1. 写作：复制报告骨架，填你的内容（YAML front matter 决定封面与评级框）
cp templates/report_template.md my_report.md

# 2. 导出：Markdown → Word（+ PDF），套一套机构版式
python templates/md_to_docx.py my_report.md --style goldman_hardline --pdf --toc
```

输出 `my_report.docx` 与 `my_report.pdf`。换版式只改一个参数：

```bash
python templates/md_to_docx.py my_report.md --style barclays_cyanline    --pdf
python templates/md_to_docx.py my_report.md --style bernstein_monochrome --pdf
python templates/md_to_docx.py my_report.md --style ubs_swissminimal     --pdf
python templates/md_to_docx.py my_report.md --style /path/to/your_own.json --pdf
```

---

## 用法

**取数**（A 股 / 美股，`quote` / `history` / `financials` / `all`）

```bash
python scripts/data/data_fetcher.py cn 600519 all --json        # 贵州茅台，全量
python scripts/data/data_fetcher.py us NVDA financials --json   # 英伟达，财务
export YAHOO_PROXY=socks5h://127.0.0.1:10808                    # 国内环境取美股时走代理
```

**出图**（五类图表的可运行样图）

```bash
python scripts/charts/report_charts.py       # → scripts/charts/sample_pngs/
```

**全自动跑完整条流水线**——把下面这段交给任意 AI agent（或自己照着做）：

```text
读 pipeline/pipeline_orchestration.md，
按 S0–S9 流程产出一份 XX 公司的深度研报，
版式用 ubs_swissminimal，双市场数据用 scripts/data/。
每个阶段的产物落到工作区，门禁不通过就退回重做。
```

---

## 架构

<img src="docs/assets/architecture.png" width="100%" alt="Ten-stage research pipeline">

`pipeline/pipeline_orchestration.md`（636 行）定义每个阶段的输入、输出、责任角色与门禁检查项；`pipeline/agent_prompts.md`（829 行）是 8 个角色的中英双语工作简报。三种深度档位（快速简报 / 标准单公司 / 深度专题）按档裁剪，不是每次都跑满。

**八个角色**（透镜边界，不是头衔——同一个 agent 可以换帽子，但同一顶帽子不能既做多又做空）

| 角色 | 透镜 |
|---|---|
| 主编 / Editor-in-Chief | 全局、契约、裁决、终审 |
| 数据工程师 | 数字从哪来、能不能复算 |
| 行业研究员 | 产业链位置、供需、竞争格局 |
| 估值研究员 | 倍数、DCF、可比公司 |
| 红队 / Red Team | 只负责拆自己的台 |
| 图表师 | 一张图说一件事 |
| 排版师 | 版面、层级、留白 |
| 校对 / Proofreader | 逐页视觉挑刺 |

**仓库结构**

```text
wallstreetype-research/
├── methodology/                 方法论库：100 篇清单 + 10 组凝练 + 范式手册
├── pipeline/                    流水线定义（agent 无关，任何模型都能跑）
│   ├── pipeline_orchestration.md  阶段规格 / 门禁 / 工件
│   ├── agent_prompts.md           8 个角色简报（中英双语）
│   └── intake.md                  选题与版式问卷
├── scripts/
│   ├── data/                    双市场取数（零密钥）
│   ├── charts/                  5 类机构级图表
│   ├── layout/                  版式层说明
│   └── intake/                  问卷与 brief 生成
├── templates/
│   ├── report_template.md       报告骨架（YAML front matter）
│   ├── md_to_docx.py            Markdown → Word / PDF
│   └── styles/*.json            6 套机构版式定义
├── examples/                    三个可复现样例（含端到端案例）
├── docs/assets/                 README 用图（封面 / 架构 / 案例成品）
├── VERIFICATION.md              验收清单
└── README.md · README_EN.md
```

---

## 六套版式模板

版式的视觉语言取自公开研报样本，**已去除全部机构名称与标识**，只保留排版定义。下面是**同一篇报告**分别按六套版式渲染的封面，点开可看内页。

<table>
<tr>
<td width="33%" align="center"><img src="docs/assets/styles/goldman_hardline_cover.png" width="100%"><br><b>高盛 · 硬朗风</b><br><sub>开放式无框；衬线大标题；深蓝强调；细线分区；高信息密度</sub><br><a href="docs/assets/styles/goldman_hardline_page.png">内页 →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/morganstanley_restrained_cover.png" width="100%"><br><b>大摩 · 克制风</b><br><sub>大留白单栏；轻字重大标题；单一蓝色点缀；宽边距</sub><br><a href="docs/assets/styles/morganstanley_restrained_page.png">内页 →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/jpmorgan_heavyset_cover.png" width="100%"><br><b>小摩 · 厚重风</b><br><sub>高密度双栏；粗标题 + 衬线正文；灰底表头；紧凑行距</sub><br><a href="docs/assets/styles/jpmorgan_heavyset_page.png">内页 →</a></td>
</tr>
<tr>
<td align="center"><img src="docs/assets/styles/barclays_cyanline_cover.png" width="100%"><br><b>巴克莱 · 青蓝风</b><br><sub>青色页眉带；右侧浅蓝信息栏；青色表头白字</sub><br><a href="docs/assets/styles/barclays_cyanline_page.png">内页 →</a></td>
<td align="center"><img src="docs/assets/styles/bernstein_monochrome_cover.png" width="100%"><br><b>伯恩斯坦 · 学术黑白</b><br><sub>纯黑白；黑色顶栏；衬线正文；紧凑网格</sub><br><a href="docs/assets/styles/bernstein_monochrome_page.png">内页 →</a></td>
<td align="center"><img src="docs/assets/styles/ubs_swissminimal_cover.png" width="100%"><br><b>瑞银 · 瑞士极简</b><br><sub>双层标题色带；深海军蓝 + 浅蓝；右侧信息栏；宽边距</sub><br><a href="docs/assets/styles/ubs_swissminimal_page.png">内页 →</a></td>
</tr>
</table>

---

## 成果展示

[`examples/unitree_vs_nvidia/`](examples/unitree_vs_nvidia) 是一次完整跑通：**宇树科技 `688836.SH`（科创板）是否能超越英伟达 `NVDA`（NASDAQ）**——从取数到排版成书，版式 `goldman_hardline`。

[PDF（7 页）](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf) · [Word](examples/unitree_vs_nvidia/unitree_vs_nvidia.docx) · [Markdown 源](examples/unitree_vs_nvidia/unitree_vs_nvidia.md) · [六张图表](examples/unitree_vs_nvidia/figures) · [原始数据](examples/unitree_vs_nvidia/data) · [校对图](examples/unitree_vs_nvidia/proof) · [复现脚本](examples/unitree_vs_nvidia/README.md)

<table>
<tr>
<td width="50%"><img src="docs/assets/case/case_page01.png" width="100%"></td>
<td width="50%"><img src="docs/assets/case/case_page03.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>第 1 页 · 封面</sub></td>
<td align="center"><sub>第 3 页 · 内页</sub></td>
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

---

## 文档导航

| 文档 | 内容 |
|---|---|
| [`pipeline/pipeline_orchestration.md`](pipeline/pipeline_orchestration.md) | 十阶段流程、门禁检查项、工件格式 |
| [`pipeline/agent_prompts.md`](pipeline/agent_prompts.md) | 8 个角色的中英双语简报模板 |
| [`methodology/wallstreet_paradigm_manual.md`](methodology/wallstreet_paradigm_manual.md) | 华尔街范式手册：研究思路、证据纪律、红旗清单 |
| [`templates/styles/README.md`](templates/styles/README.md) | 六套版式的字段说明与自定义方法 |
| [`scripts/data/README.md`](scripts/data/README.md) · [`scripts/charts/README.md`](scripts/charts/README.md) | 取数接口与图表函数说明 |
| [`VERIFICATION.md`](VERIFICATION.md) | 每条产出的验收动作 |

---

## 免责声明

本项目用于**研究流程与文档工程的方法示范**，不构成任何投资建议。数据来自公开接口，仅供参考，请以交易所与公司公告为准。版式模板为排版语言参考，不含任何机构名称或标识，与相关机构无关联、无背书。

## 许可

[MIT](LICENSE) · *You can work for Wall Street.*
