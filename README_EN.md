<div align="center">

# wallstreetype-research

**Turning a dinner-table joke into an auditable pipeline.**

### *You can work for Wall Street.*

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![API keys](https://img.shields.io/badge/API%20keys-none-brightgreen)
![Markets](https://img.shields.io/badge/markets-US%20%7C%20A--share-orange)
![Layout styles](https://img.shields.io/badge/layout%20styles-6-9cf)
![Agents](https://img.shields.io/badge/works%20with-any%20agent%20%7C%20a%20human-black)

[中文](README.md) · [English](README_EN.md) · [Paradigm manual](methodology/wallstreet_paradigm_manual.md) · [Case PDF](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf)

</div>

---

## 0. The 30-second version

`wallstreetype-research` is a **self-contained, agent-agnostic** equity-research pipeline.

> **Input**: ticker + market + language + depth + layout template
> **Output**: a sell-side-grade research report (Markdown → Word / PDF, 500-dpi charts)

The methodology comes from **100 real sell-side reports**, condensed five ways each
(10 groups × 10 reports → one 7-chapter paradigm manual).
The numbers come from **real dual-market endpoints** (Yahoo Finance for US, Tencent + Eastmoney for A-shares),
with **no API key required**.
The charts are **institutional-style** (5 families). The layout is **sell-side** (6 anonymised templates).

This is not "let an AI write a report." It is "**break research down into 10 stages and 8 roles, and make someone own every cell**."

```bash
git clone https://github.com/lss680455-create/wallstreetype-research.git
cd wallstreetype-research && pip install -r requirements.txt

# fetch real data → chart it → render Word/PDF
python scripts/data/data_fetcher.py cn 688836 all --json
python templates/md_to_docx.py examples/unitree_vs_nvidia/unitree_vs_nvidia.md --pdf --style goldman_hardline
```

---

## 1. Why this exists

Someone asked: **Can Unitree Robotics surpass NVIDIA?**

It is a question that genuinely gets asked at dinner tables, in group chats, and on some sell-side morning calls.
It sounds exciting. It is also **undefined** — like asking whether a robot dog that just learned a backflip can beat an army.

To answer it, you first have to say **which ruler you are using**.

And "deciding which ruler, finding the number for every ruler, and writing the conclusion in a format someone else can audit" — **that is the craft of Wall Street.**

So this project takes that craft apart, lays the pieces flat, and ships the tools. So anyone can run it. **Including you.**

---

## 2. Six layout templates

Six **style-only** presets (fonts / colours / spacing / table treatment / masthead), extracted from the visual
characteristics of public research reports. **No institution logos, wordmarks or text marks.**
Switch with `--style <id>`.

<table>
<tr>
<td width="50%" align="center"><img src="docs/assets/styles/goldman_hardline_cover.png" alt="goldman_hardline"><br><b>goldman_hardline</b><br>Hardline<br><sub>Open grid, no boxes; serif masthead + sans body; navy accents; hairline rules; high density.<br>Best for: institutional deep-dives, data-dense reports.</sub></td>
<td width="50%" align="center"><img src="docs/assets/styles/morganstanley_restrained_cover.png" alt="morganstanley_restrained"><br><b>morganstanley_restrained</b><br>Restrained<br><sub>Airy single column; light-weight sans masthead; one blue accent; wide margins.<br>Best for: thesis-driven narrative notes.</sub></td>
</tr>
<tr>
<td width="50%" align="center"><img src="docs/assets/styles/jpmorgan_heavyset_cover.png" alt="jpmorgan_heavyset"><br><b>jpmorgan_heavyset</b><br>Heavyset<br><sub>Dense two-column; bold sans headings over serif body; slate-blue; tight leading.<br>Best for: full-chain reports with many tables and appendices.</sub></td>
<td width="50%" align="center"><img src="docs/assets/styles/barclays_cyanline_cover.png" alt="barclays_cyanline"><br><b>barclays_cyanline</b><br>Cyan Line<br><sub>Cyan header band; tinted information rail; cyan table header with white text; medium-high density.<br>Best for: bullet-plus-sidebar layouts, chart-heavy notes.</sub></td>
</tr>
<tr>
<td width="50%" align="center"><img src="docs/assets/styles/bernstein_monochrome_cover.png" alt="bernstein_monochrome"><br><b>bernstein_monochrome</b><br>Monochrome<br><sub>Strict black-and-white; black masthead bar; serif body; dense grid.<br>Best for: academic/quantitative research, B/W printing.</sub></td>
<td width="50%" align="center"><img src="docs/assets/styles/ubs_swissminimal_cover.png" alt="ubs_swissminimal"><br><b>ubs_swissminimal</b><br>Swiss Minimal<br><sub>Two-tier title bands; deep navy + pale blue; generous margins.<br>Best for: restrained high-end institutional style.</sub></td>
</tr>
</table>

<sub>The covers above are the **same case report** (Unitree, §3) rendered through all six templates.
Each template also has a `_page.png` inner-page sample in [`docs/assets/styles/`](docs/assets/styles/).</sub>

```bash
python scripts/intake/intake.py --list          # list the six presets
python templates/md_to_docx.py my_report.md --pdf --style ubs_swissminimal
```

**Add your own:** copy any `templates/styles/*.json`, change `id` and the fields (filename must equal `id`),
and it works. Full field reference: [`templates/styles/README.md`](templates/styles/README.md).

---

## 3. Case study: Can Unitree Robotics surpass NVIDIA?

> A complete demo report: [`examples/unitree_vs_nvidia/`](examples/unitree_vs_nvidia/)
> ｜ [Markdown](examples/unitree_vs_nvidia/unitree_vs_nvidia.md)
> ｜ [Word](examples/unitree_vs_nvidia/unitree_vs_nvidia.docx)
> ｜ [PDF (7 pages)](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf)

**Verdict up front:** on the rulers of **market cap / revenue / profit**, **no — not in any short horizon.**
On the ruler of **narrative pricing**, **it did it on day one.**

### Four rulers

| Ruler | Unitree (688836.SH) | NVIDIA (NVDA) | Gap |
|---|---|---|---|
| Market cap | ¥207.9bn (US$31.0bn) | US$5.40tn (¥36.2tn) | **174×** |
| Revenue (TTM) | ¥2.08bn | ¥2.03tn | **978×** |
| Net income (TTM) | ¥0.58bn | ¥1.28tn | **2,187×** |
| Robot units shipped | tens of thousands | 0 (NVIDIA does not build robots) | **Unitree leads 1 : 0** |
| Valuation multiple (P/S) | 100.1× | 17.8× | **Unitree "wins"** |

> To match NVIDIA's market cap, Unitree's share price would need to reach **¥89,437** — about **174×** from ¥513.93.

### Six exhibits

| | |
|---|---|
| ![Gap](docs/assets/case/exhibit1_gap.png)<br><sub>**Exhibit 1** The three rulers, log scale</sub> | ![K-line](docs/assets/case/exhibit2_kline.png)<br><sub>**Exhibit 2** 16 sessions since IPO: −53%</sub> |
| ![Valuation band](docs/assets/case/exhibit3_pe_band.png)<br><sub>**Exhibit 3** NVIDIA's valuation corridor vs Unitree's "if"</sub> | ![Financials](docs/assets/case/exhibit4_financials.png)<br><sub>**Exhibit 4** Revenue and profit: a good company, an expensive stock</sub> |
| ![Scenarios](docs/assets/case/exhibit5_scenario.png)<br><sub>**Exhibit 5** Probability-weighted target ¥565</sub> | ![Catch-up](docs/assets/case/exhibit6_catchup.png)<br><sub>**Exhibit 6** How long to catch today's NVIDIA?</sub> |

**Catch-up timetable** (assuming NVIDIA stands still):

| Unitree growth | Scenario | Years to match NVIDIA's **current** revenue |
|---|---|---|
| 100% | Dream | 9.9 |
| 60% | Optimistic | 14.6 |
| 48% | 2026H1 actual | 17.4 |
| 30% | Mature phase | 26.2 |
| 20% | Manufacturing mainstream | 37.8 |

And if NVIDIA keeps growing — TTM revenue is **+105.9% YoY** — the table flips from "catch-up" to "never."

### Where the numbers come from

**Not a single hand-typed number** in the case study. Three automated steps:

```bash
python scripts/data/data_fetcher.py cn 688836 all --json   # 1. fetch real data
python examples/unitree_vs_nvidia/compute_numbers.py       # 2. compute every metric
python examples/unitree_vs_nvidia/make_case_charts.py      # 3. draw six exhibits + cover
```

Raw JSON (`data/*.json`), the computation script, the six exhibits, and the rendered Word/PDF all live in
[`examples/unitree_vs_nvidia/`](examples/unitree_vs_nvidia/) — auditable cell by cell.

---

## 4. Quick start

```bash
# 0. install
pip install -r requirements.txt

# 1. fetch data (Yahoo for US, Tencent + Eastmoney for A-shares; no API key)
python scripts/data/data_fetcher.py us NVDA all --json
python scripts/data/data_fetcher.py cn 688836 financials --json

# 2. pick a layout (one of six)
python scripts/intake/intake.py --list

# 3. render (Markdown → Word / PDF)
python templates/md_to_docx.py my_report.md -o out/report.docx --pdf --style jpmorgan_heavyset

# 4. regenerate all chart samples (5 families, 500 dpi)
python scripts/charts/report_charts.py
```

**One interface, two markets**: `cn 688836` / `us NVDA` — same fields on both sides.

**Network note**: US data may need a proxy from mainland China
(`export YAHOO_PROXY=socks5h://127.0.0.1:10808`). A-shares work directly.

---

## 5. Architecture: 10 stages, 8 roles

```
main agent ── S0 intake ── S1 envelope ── S2 briefs ─┬── [child] Data Engineer   ─┐
                                                     ├── [child] Industry Analyst ┼── parallel ── S5 main-agent adjudication
                                                     ├── [child] Valuation Analyst│
                                                     └── [child] Red Team ────────┘
                            S6 [child] Chart Specialist ─ S7 [child] Layout Specialist ─ S8 main-agent final QA ─ S9 Proofing & QC (vision gate) ─ deliver
```

| Stage | Owner | Output |
|---|---|---|
| **S0** Intake | main agent (**never delegated**) | `brief/intake.json`: layout template + research-focus questionnaire |
| **S1** Envelope | main agent | `envelope.json`: the task contract every brief references |
| **S2** Briefs | main agent | one bilingual brief per role |
| **S3–S4** Parallel research | Data Engineer / Industry / Valuation / Red Team | data, industry, valuation, challenge |
| **S5** Adjudication | main agent | resolves conflicts; **only the main agent may change a conclusion** |
| **S6–S7** Charts & layout | Chart / Layout Specialist | `charts/fig_*.png`, `final/report.*` |
| **S8–S9** Final QA | main agent | vision proofing gate: per-page renders + number-reference cross-check |

**The eight lenses are disjoint**: the Data Engineer writes no conclusions, the Industry Analyst touches no
valuation, the Red Team challenges without editing, the Proofreader verifies without rewriting.
**The main agent is the only orchestrator and the only adjudicator.**

Methodology assets:

| Asset | Location | Contents |
|---|---|---|
| Paradigm manual | [`methodology/wallstreet_paradigm_manual.md`](methodology/wallstreet_paradigm_manual.md) | 7 chapters: argument skeleton / method library / writing paradigm / chart standards / evidence discipline / red flags / red-team question bank |
| 100-report list | [`methodology/report_list_100.md`](methodology/report_list_100.md) | a traceable seed library of methodology |
| 10 group digests | [`methodology/digests/`](methodology/digests/) | five-dimension digest per report (method / prose / charts / action / lesson) |
| Stage orchestration | [`pipeline/pipeline_orchestration.md`](pipeline/pipeline_orchestration.md) | I/O per stage, single-writer rules, quality gates |
| Role briefs | [`pipeline/agent_prompts.md`](pipeline/agent_prompts.md) | 8 roles × bilingual brief templates |
| Intake | [`pipeline/intake.md`](pipeline/intake.md) | S0 questionnaire: template choice + research focus |

> **Agent-agnostic**: the pipeline is bound to no single AI. Use Codex, Claude Code, Cursor, Hermes —
> or **do it yourself**. Every artifact is a file. There is no black box.

---

## 6. Repository layout

```
wallstreetype-research/
├── README.md / README_EN.md      # bilingual docs
├── SKILL.md                      # skill definition (drop into any agent)
├── requirements.txt
├── methodology/                  # methodology assets
│   ├── wallstreet_paradigm_manual.md   # 7-chapter paradigm manual
│   ├── report_list_100.md              # 100-report seed library
│   └── digests/group1..10.md           # 10 five-dimension digests
├── pipeline/                     # orchestration
│   ├── pipeline_orchestration.md       # S0–S9
│   ├── agent_prompts.md                # 8 roles, bilingual briefs
│   └── intake.md                       # S0 intake
├── scripts/
│   ├── data/                     # data layer: Yahoo / Tencent / Eastmoney, no API key
│   ├── charts/                   # chart layer: 5 institutional families, 500 dpi
│   └── intake/                   # intake CLI
├── templates/
│   ├── md_to_docx.py             # Markdown → Word / PDF renderer
│   ├── report_template.md        # report skeleton (with frontmatter field docs)
│   └── styles/*.json             # six layout presets
├── examples/
│   ├── nvda_demo/                # US demo: NVIDIA
│   ├── unitree_vs_nvidia/        # bilingual case study (README §3)
│   └── layout_demo/              # minimal layout example
└── docs/assets/                  # README images (six template covers + case exhibits)
```

---

## 7. Three layers of tooling

| Layer | Location | Capability |
|---|---|---|
| **Data** | [`scripts/data/`](scripts/data/) | US (Yahoo) / A-share (Tencent + Eastmoney) quotes, history (front-adjusted), fundamentals; **free, keyless, traceable** |
| **Charts** | [`scripts/charts/`](scripts/charts/) | 5 families: K-line + volume, valuation band, financial trend, scenario bars, peer comparison; matplotlib + mplfinance, 500-dpi static PNG |
| **Layout** | [`templates/`](templates/) | Markdown → Word / PDF; six presets; cover rating box, key data, headers/footers, disclosures |

**Why not plotly / finplot?** Because the deliverable is a **500-dpi static PNG for Word/PDF embedding**,
not an interactive widget. The selection comparison is in [`scripts/charts/README.md`](scripts/charts/README.md).

---

## 8. "You can work for Wall Street"

The project is called `wallstreetype-research` — the **"-type"** is deliberate.
It is not Wall Street. It just **looks like** Wall Street.

| Common objection | Answer |
|---|---|
| "I have no finance background." | **Good.** That is precisely why this exists: the craft, broken into executable steps. |
| "I don't have a Bloomberg terminal." | You don't need one. The data layer uses free public endpoints. |
| "I can't code." | Three commands. And if you want to write it by hand, `report_template.md` is a fill-in-the-blank sheet. |
| "Can I trust an AI-written report?" | Not on its own. That is why there is a Red Team, a source registry, a vision proofing gate, and a hard rule: an unregistered number is a violation. |
| "Can I publish this directly?" | No. It is a **methodology demo**, not investment advice. |
| "So who actually gets to work on Wall Street?" | People who can ask the right question, find every number, and write conclusions others can audit. **Credentials not required.** |

---

## 9. Auditability

- **Data**: all from public endpoints; raw JSON persisted (`examples/*/data/*.json`); no synthesis, no extrapolation.
- **Numbers**: every case-study metric is computed by script from the raw JSON (`compute_numbers.py`) — **zero hand-typed numbers**.
- **Citations**: every chart carries a source footnote; every number in the prose must be registered in `sources.json`, or S9 fails the report.
- **QA**: S9 proofing is **vision-model only**, on per-page renders at ≥144 dpi, with 2× zoom re-checks on suspicious areas.
  The independent verification report is [`VERIFICATION.md`](VERIFICATION.md).

---

## 10. Disclaimer and licence

- **Not investment advice.** This is a methodology and engineering demo, not a recommendation to buy or sell any security.
- **Layout templates are style references only**: fonts, colours and spacing were extracted from publicly
  available research reports. **No institution logo, wordmark, watermark or analyst name is included**;
  this project is unaffiliated with, and not endorsed by, any institution.
- **Data sources**: Yahoo Finance (US), Tencent Finance / Eastmoney (A-shares). Data may be delayed or wrong — verify before use.
- **Licence**: MIT. See [`LICENSE`](LICENSE).

<div align="center">
<br>
<sub>Asking the right question is harder than giving a pretty answer.</sub><br>
<sub><b>— wallstreetype-research</b></sub>
</div>
