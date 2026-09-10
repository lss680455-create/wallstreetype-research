<div align="center">

# wallstreetype-research

**Treating equity research like a software pipeline.**

### *You can work for Wall Street.*

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![API keys](https://img.shields.io/badge/API%20keys-none-brightgreen)
![Markets](https://img.shields.io/badge/markets-US%20%7C%20A--share-orange)
![Styles](https://img.shields.io/badge/layout%20styles-6-9cf)
![Charts](https://img.shields.io/badge/chart%20families-5-purple)
![Pipeline](https://img.shields.io/badge/pipeline-S0--S9-black)
![Agent](https://img.shields.io/badge/works%20with-any%20AI%20agent%20%7C%20human-lightgrey)

[English](README_EN.md) · [**中文**](README.md) · [Quick start](#quick-start-four-steps-to-a-finished-report) · [Architecture](#architecture) · [Showcase](#showcase-what-the-output-looks-like)

</div>

---

## What this is

An open-source toolkit that turns **sell-side research production into engineering**: an input contract, role separation, quality gates, and delivery specs — all as runnable scripts and documents.

It doesn't teach you how to read a balance sheet. It hands you a **pipeline** — fetch real data, compute the metrics, draw institutional-grade charts, apply an anonymised sell-side layout, export a Word / PDF with cover page and rating box. Every number in a report traces back to a real data fetch.

> **One line**: other people hand you a research report. This hands you a research-report machine. Install it, run it, ship it.

---

## Features

Five layers, organised as *where the research comes from → what it looks like → who does what → how it ships*. Each works standalone; together they run end to end.

| # | Module | Path / entry point | What you get |
|---|---|---|---|
| 1 | **Methodology library** | `methodology/` | A teardown list of 100 real sell-side reports + 10 thematic digests + a 550-line *Wall Street Paradigm Manual* — research logic, evidence discipline, red flags |
| 2 | **Dual-market data layer** | `scripts/data/data_fetcher.py` | US + A-share quotes / daily bars / financials in one command, **no API key** |
| 3 | **Institutional chart layer** | `scripts/charts/report_charts.py` | 5 report-ready chart families: K-line + volume, valuation band, financial trend, scenario bars, peer comparison |
| 4 | **Layout & delivery layer** | `templates/` | 6 anonymised sell-side layouts + a Markdown → Word / PDF engine (cover, rating box, Key Data, numbering, TOC, embedded charts) |
| 5 | **Research pipeline** | `pipeline/` | 10 stages (S0–S9), 8 roles, quality gates, structured hand-off artifacts — writing a report becomes a reproducible line |

**Plus one more**: `VERIFICATION.md` — a verifiable action for every claim, including the final gate: render the finished document and let a vision model nitpick it page by page.

---

## Quick start: four steps to a finished report

```bash
# 0. Dependencies (pandas / matplotlib / python-docx / mplfinance, ...)
pip install -r requirements.txt

# 1. Fetch: A-share / US, quote / history / financials
python scripts/data/data_fetcher.py cn 600519 all --json        # Kweichow Moutai, full set
python scripts/data/data_fetcher.py us NVDA financials --json   # NVIDIA, financials
export YAHOO_PROXY=socks5h://127.0.0.1:10808                    # proxy for US data if needed

# 2. Write: copy the skeleton, fill in your content (YAML front matter drives
#    the cover page and the rating box)
cp templates/report_template.md my_report.md

# 3. Chart: five families, one call
python scripts/charts/report_charts.py          # writes every sample to scripts/charts/sample_pngs/

# 4. Ship: Markdown → Word (+ PDF), pick a layout
python templates/md_to_docx.py my_report.md --style goldman_hardline --pdf --toc
```

**Switching layout is a single flag:**

```bash
python templates/md_to_docx.py my_report.md --style barclays_cyanline    --pdf
python templates/md_to_docx.py my_report.md --style bernstein_monochrome --pdf
python templates/md_to_docx.py my_report.md --style ubs_swissminimal     --pdf
python templates/md_to_docx.py my_report.md --style /path/to/your_own.json --pdf
```

Layouts aren't hard-coded: `templates/styles/*.json` defines fonts, colours, layout, tables, rating box and masthead. Copy one, edit it, and you have a new template.

**Want the whole pipeline autonomous?** Hand it to any AI agent (or to yourself):

```text
Read pipeline/pipeline_orchestration.md and produce a deep-dive research
report on <company> following stages S0–S9. Use the ubs_swissminimal layout
and scripts/data/ for dual-market data. Write every stage artifact into the
workspace; redo the stage if a gate fails.
```

---

## Architecture

### The ten-stage pipeline (S0–S9)

```text
  S0 Intake               topic + layout questionnaire   ── editor ──▶ brief/intake.json
  S1 Input & Envelope     freeze the input contract      ── editor ──▶ envelope.json
  S2 Master Brief         write the master brief         ── editor ──▶ briefs/master_brief.md
  S3 Parallel Research    three parallel workstreams     ── 3 children ──▶ data / industry / valuation
  S4 Red Team Challenge   attack your own thesis         ── 1 child ──▶ review/redteam.md
  S5 Adjudication         editor rules on the dispute    ── editor ──▶ decisions/decision.json
  S6 Charting             build the exhibits             ── 1 child ──▶ charts/manifest.json
  S7 Layout & Assembly    assemble the document          ── 1 child ──▶ draft/report_draft.md
  S8 Final Review         sign-off                       ── editor ──▶ final/report.md
  S9 Proofing & QC        proofread + visual QC          ── editor + vision model ──▶ proof/visual_proofing.md

  Gates G0 · G0b · G0c · G1 · G2 · G3 · G4 · G5 · G7    ← fail the gate, redo the stage
```

Three depth tiers (quick note / standard single-company / deep thematic) trim the same pipeline — you don't run all of it every time.

### The eight roles

| Role | Lens | Appears |
|---|---|---|
| **Editor-in-Chief** | Contract, adjudication, sign-off | throughout |
| **Data Engineer** | Where numbers come from, can they be recomputed | S3 · S6 |
| **Industry Analyst** | Value-chain position, supply/demand, competition | S3 |
| **Valuation Analyst** | Multiples, DCF, comparables | S3 |
| **Red Team** | Paid to dismantle your own thesis | S4 |
| **Charting** | One chart, one message | S6 |
| **Layout** | Grid, hierarchy, whitespace | S7 |
| **Proofreader** | Page-by-page visual nitpicking (plus zoomed re-checks) | S9 |

Roles are **lens boundaries**, not job titles — one agent can wear several hats, but no hat gets to be both long and short on the same name.

### Repository layout

```text
wallstreetype-research/
├── methodology/                 library: 100-report list + 10 digests + paradigm manual
│   ├── report_list_100.md
│   ├── digests/                 group1.md … group10.md
│   └── wallstreet_paradigm_manual.md
├── pipeline/                    agent-agnostic pipeline definition
│   ├── pipeline_orchestration.md  stage specs / gates / artifact schemas
│   ├── agent_prompts.md           8 role briefs (EN + ZH)
│   └── intake.md                  topic & layout questionnaire
├── scripts/
│   ├── data/                    live dual-market fetching (zero credentials)
│   ├── charts/                  5 institutional chart families
│   ├── layout/                  layout engine
│   └── intake/                  questionnaire & brief generation
├── templates/
│   ├── report_template.md       report skeleton (YAML front matter)
│   ├── md_to_docx.py            Markdown → Word / PDF (cover, rating box, TOC)
│   └── styles/*.json            6 sell-side layout definitions
├── examples/
│   ├── nvda_demo/               NVIDIA sample (9 pages)
│   ├── layout_demo/             layout comparison sample
│   └── unitree_vs_nvidia/       end-to-end case: fetch → PDF
├── docs/assets/                 images used by this README
├── VERIFICATION.md              acceptance checklist
└── README.md / README_EN.md
```

---

## The six layout templates

Their visual DNA comes from publicly available research reports, with **every institution name and mark removed** — only the typographic language is kept. They are not stickers: each is a complete definition of fonts, colours, layout, tables, rating box and masthead.

<table>
<tr>
<td width="33%" align="center"><img src="docs/assets/styles/goldman_hardline_cover.png" width="100%"><br><b>Hardline</b><br><sub>Open, frameless grid; serif display headings; navy accents; hairline rules; high density</sub><br><a href="docs/assets/styles/goldman_hardline_page.png">inner page →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/morganstanley_restrained_cover.png" width="100%"><br><b>Restrained</b><br><sub>Generous whitespace, single column; light display type; one blue accent; wide margins</sub><br><a href="docs/assets/styles/morganstanley_restrained_page.png">inner page →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/jpmorgan_heavyset_cover.png" width="100%"><br><b>Heavyset</b><br><sub>Dense two-column grid; heavy sans headings + serif body; grey table headers</sub><br><a href="docs/assets/styles/jpmorgan_heavyset_page.png">inner page →</a></td>
</tr>
<tr>
<td align="center"><img src="docs/assets/styles/barclays_cyanline_cover.png" width="100%"><br><b>Cyan Line</b><br><sub>Cyan masthead band; pale-blue sidebar; cyan table headers; light-weight display type</sub><br><a href="docs/assets/styles/barclays_cyanline_page.png">inner page →</a></td>
<td align="center"><img src="docs/assets/styles/bernstein_monochrome_cover.png" width="100%"><br><b>Monochrome</b><br><sub>Pure black &amp; white; black top bar; serif body; tight grid; zero colour</sub><br><a href="docs/assets/styles/bernstein_monochrome_page.png">inner page →</a></td>
<td align="center"><img src="docs/assets/styles/ubs_swissminimal_cover.png" width="100%"><br><b>Swiss Minimal</b><br><sub>Double title band; deep navy + pale blue; right-hand sidebar; wide margins</sub><br><a href="docs/assets/styles/ubs_swissminimal_page.png">inner page →</a></td>
</tr>
</table>

> Those twelve images are **the same report** rendered through all six layouts — cover and inner page. Click through for full resolution.

---

## Showcase: what the output looks like

**Input** (`examples/unitree_vs_nvidia/`) — a spec, not a script:

| Item | Value |
|---|---|
| Coverage | Unitree Robotics `688836.SH` (STAR Market) vs NVIDIA `NVDA` (NASDAQ) |
| Data | A-share: Tencent Finance + East Money; US: Yahoo Finance; USD/CNY FX |
| Hard constraint | **Every number comes from a real fetch — nothing is hand-typed in the scripts** |
| Layout | `goldman_hardline` |
| Deliverables | Markdown source + Word + PDF + 6 charts + raw JSON + per-page proof renders |

**Output** (all in this repo — click any of it):

| File | What it is |
|---|---|
| [`unitree_vs_nvidia.pdf`](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf) | Finished report, 7 pages, with cover / rating box / Key Data / 6 exhibits |
| [`unitree_vs_nvidia.docx`](examples/unitree_vs_nvidia/unitree_vs_nvidia.docx) | Editable Word version (2.3 MB) |
| [`unitree_vs_nvidia.md`](examples/unitree_vs_nvidia/unitree_vs_nvidia.md) | Source, including YAML front matter |
| [`compute_numbers.py`](examples/unitree_vs_nvidia/compute_numbers.py) | Turns raw JSON into every number the report uses |
| [`make_case_charts.py`](examples/unitree_vs_nvidia/make_case_charts.py) | The six exhibits (five reuse existing chart families) |
| [`data/`](examples/unitree_vs_nvidia/data) | Raw fetched JSON + `numbers.json` |
| [`proof/`](examples/unitree_vs_nvidia/proof) | S9 page-by-page proof renders |

<table>
<tr>
<td width="50%"><img src="docs/assets/case/case_page01.png" width="100%"></td>
<td width="50%"><img src="docs/assets/case/case_page03.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Cover: rating box + Key Data + price panel, filled in by script</sub></td>
<td align="center"><sub>Inner page: numbered sections, tables and exhibits, all automatic</sub></td>
</tr>
</table>

<table>
<tr>
<td width="33%"><img src="docs/assets/case/exhibit1_gap.png" width="100%"></td>
<td width="33%"><img src="docs/assets/case/exhibit2_kline.png" width="100%"></td>
<td width="33%"><img src="docs/assets/case/exhibit4_financials.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Peer comparison (log axis)</sub></td>
<td align="center"><sub>K-line + volume</sub></td>
<td align="center"><sub>Financial trend (dual axis)</sub></td>
</tr>
</table>

**Cost of one run** (measured on this machine, Windows, direct domestic network): fetch **1.7 s** · compute **0.2 s** · charts **6.8 s** · Word/PDF export **10.3 s**.

> The case's actual analysis lives inside the report ([open the PDF](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf)). This README answers exactly one question: **what does the thing produce?**

---

## Engineering discipline

Research reports rarely break on the argument; they break on the numbers. The house rules here:

- **Live data, never synthesised**: there is no mock branch in `data_fetcher.py` — if a fetch fails, it raises, it doesn't guess.
- **Numbers are computed, not typed**: in the case study every figure is derived from raw JSON by `compute_numbers.py`; the report and the charts only read that output.
- **Zero credentials**: public market endpoints only — no API keys, no brokerage accounts.
- **De-institutionalised layouts**: the six templates keep the typography and drop every name and mark (see `_disclaimer` in `templates/styles/*.json`).
- **A visual gate before delivery**: S9 renders the document at ≥144 DPI and nitpicks it page by page, zooming 2× into anything suspicious.
- **Claims are checkable**: every statement in `VERIFICATION.md` maps to a reproducible action.

---

## You can work for Wall Street

| Question | Answer |
|---|---|
| I have no finance background. Can I use this? | Yes. The whole premise is that the craft decomposes into steps. The methodology library documents the logic, the evidence bar and the red flags for each report type; the rest is execution. |
| Is this the process real research desks use? | The structure, gates, role boundaries and delivery specs follow sell-side practice; the typographic language comes from public report samples. Whether the conclusions are worth anything is for the market to decide. |
| Do I need a frontier model? | No. `pipeline/` is model-agnostic: any agent that can read/write files and run scripts can drive it — a fully manual run works too. |
| Can I make it look like my own house style? | Copy a `templates/styles/*.json`, change fonts/colours/layout — that's a new template. Point `md_to_docx.py --style /path/to/your.json` at it. |
| Are the numbers fabricated? | In the case study even a drawdown like −53% is computed. A failed fetch raises an error instead of degrading into placeholders. |

---

## Disclaimer

This project is a **methodology and document-engineering demonstration**. It is not investment advice. Data comes from public endpoints, is indicative only, and the exchange and company filings prevail. Layout templates reference typographic style only: no institution names or marks are included, and there is no affiliation or endorsement.

## License

[MIT](LICENSE)
