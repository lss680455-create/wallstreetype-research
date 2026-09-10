<div align="center">

<img src="docs/assets/hero.png" width="100%" alt="wallstreetype-research">

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![API keys](https://img.shields.io/badge/API%20keys-none-brightgreen)
![Markets](https://img.shields.io/badge/markets-US%20%7C%20A--share-orange)
![Layouts](https://img.shields.io/badge/layout%20styles-6-9cf)
![Charts](https://img.shields.io/badge/chart%20families-5-purple)
![Agent](https://img.shields.io/badge/works%20with-any%20AI%20agent%20%7C%20human-lightgrey)

[中文](README.md) · [**English**](README_EN.md) · [Features](#what-it-does) · [Quick start](#quick-start) · [Usage](#usage) · [Architecture](#architecture) · [Layouts](#the-six-layout-templates) · [Showcase](#showcase) · [Docs](#documentation)

</div>

---

## What it does

**wallstreetype-research** is an open-source toolkit that turns sell-side research production into an engineering workflow: hand it a ticker, get back a report you could actually deliver — cover page, rating box, key-data table, numbered sections, institutional-grade charts, exported to Word and PDF.

The methodology, market data, charting, page layout and quality gates are all shipped as **runnable scripts and specs** rather than prose. The pipeline is model-agnostic: any AI agent that can read files and run scripts can drive it, and a human following the docs works just as well.

---

## Features

- 📚 **Methodology library** — a 124-line breakdown of 100 sell-side reports, 10 thematic digests, and a 550-line Wall Street paradigm manual covering research logic, evidence discipline and red-flag checklists. → [`methodology/`](methodology)
- 📈 **Dual-market data layer** — US and A-share quotes, price history and financials behind one command, with **zero API keys**. → [`scripts/data/`](scripts/data)
- 📊 **Five chart families** — price + volume candles, valuation band, dual-axis financial trend, scenario bars, peer comparison, all sharing one house style. → [`scripts/charts/`](scripts/charts)
- 🔀 **Ten-stage pipeline (S0–S9)** — 10 stages, 8 role lenses, 8 quality gates, structured hand-off artifacts. → [`pipeline/`](pipeline)
- 📄 **Markdown → Word / PDF engine** — generates the cover, rating box, key-data table, table of contents, numbered sections and embedded figures, with CJK-aware fonts. → [`templates/md_to_docx.py`](templates/md_to_docx.py)
- 🎨 **Six institutional layouts** — each one a complete JSON definition of fonts, palette, layout, tables and rating box; tweak a copy and you have a new template. All firm names and marks removed. → [`templates/styles/`](templates/styles)
- ✅ **Verifiable output** — every claim maps to a reproducible action, and the final gate renders the finished document to images for page-by-page visual review. → [`VERIFICATION.md`](VERIFICATION.md)

---

## Quick start

```bash
# 0. Dependencies (pandas / matplotlib / python-docx / mplfinance, ...)
pip install -r requirements.txt

# 1. Write: copy the report skeleton and fill in your content
#    (the YAML front matter drives the cover page and rating box)
cp templates/report_template.md my_report.md

# 2. Export: Markdown → Word (+ PDF) in any of the six layouts
python templates/md_to_docx.py my_report.md --style goldman_hardline --pdf --toc
```

That produces `my_report.docx` and `my_report.pdf`. Switching layout is a one-parameter change:

```bash
python templates/md_to_docx.py my_report.md --style barclays_cyanline    --pdf
python templates/md_to_docx.py my_report.md --style bernstein_monochrome --pdf
python templates/md_to_docx.py my_report.md --style ubs_swissminimal     --pdf
python templates/md_to_docx.py my_report.md --style /path/to/your_own.json --pdf
```

---

## Usage

**Market data** (US / A-share; `quote`, `history`, `financials`, `all`)

```bash
python scripts/data/data_fetcher.py cn 600519 all --json        # Kweichow Moutai, everything
python scripts/data/data_fetcher.py us NVDA financials --json   # NVIDIA, financials
export YAHOO_PROXY=socks5h://127.0.0.1:10808                    # proxy for US data behind the GFW
```

**Charts** (runnable samples for all five families)

```bash
python scripts/charts/report_charts.py       # → scripts/charts/sample_pngs/
```

**Run the whole pipeline** — hand this to any AI agent, or follow it yourself:

```text
Read pipeline/pipeline_orchestration.md and produce an in-depth research report
on <COMPANY> by following the S0–S9 process, using the ubs_swissminimal layout
and scripts/data/ for dual-market data. Write every stage artifact to the
workspace, and send a stage back whenever its gate fails.
```

---

## Architecture

<img src="docs/assets/architecture.png" width="100%" alt="Ten-stage research pipeline">

`pipeline/pipeline_orchestration.md` (636 lines) defines the inputs, outputs, owning role and gate checklist for every stage; `pipeline/agent_prompts.md` (829 lines) holds bilingual briefs for all eight roles. Three depth tiers (quick brief / standard single-company / deep thematic) trim the same flow — you don't run the full thing every time.

**Eight roles** (lens boundaries, not job titles — one agent can wear several hats, but a single hat can't argue both sides of the trade)

| Role | Lens |
|---|---|
| Editor-in-Chief | Global view, contracts, adjudication, sign-off |
| Data Engineer | Where numbers come from, whether they recompute |
| Industry Analyst | Value-chain position, supply/demand, competition |
| Valuation Analyst | Multiples, DCF, comparables |
| Red Team | Exists only to tear the thesis down |
| Chart Specialist | One chart, one message |
| Layout Artist | Pagination, hierarchy, whitespace |
| Proofreader | Page-by-page visual review |

**Repository layout**

```text
wallstreetype-research/
├── methodology/                 research logic: 100-report list, digests, paradigm manual
├── pipeline/                    pipeline specs (model-agnostic)
│   ├── pipeline_orchestration.md  stage specs / gates / artifacts
│   ├── agent_prompts.md           8 role briefs (EN + ZH)
│   └── intake.md                  topic + layout questionnaire
├── scripts/
│   ├── data/                    dual-market fetching (no keys)
│   ├── charts/                  5 chart families
│   ├── layout/                  layout layer documentation
│   └── intake/                  questionnaire → brief
├── templates/
│   ├── report_template.md       report skeleton (YAML front matter)
│   ├── md_to_docx.py            Markdown → Word / PDF
│   └── styles/*.json            6 institutional layout definitions
├── examples/                    three reproducible examples (incl. end-to-end case)
├── docs/assets/                 README artwork (covers / architecture / case output)
├── VERIFICATION.md              acceptance checklist
└── README.md · README_EN.md
```

---

## The six layout templates

The visual language is drawn from publicly available research notes with **all firm names and marks removed** — only the typesetting survives. Below: the same report rendered as a cover in each of the six layouts; click through for an interior page.

<table>
<tr>
<td width="33%" align="center"><img src="docs/assets/styles/goldman_hardline_cover.png" width="100%"><br><b>Hardline</b><br><sub>Open, frameless; large serif display type; navy accents; hairline rules; high density</sub><br><a href="docs/assets/styles/goldman_hardline_page.png">Interior →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/morganstanley_restrained_cover.png" width="100%"><br><b>Restrained</b><br><sub>Airy single column; light display type; one blue accent; wide margins</sub><br><a href="docs/assets/styles/morganstanley_restrained_page.png">Interior →</a></td>
<td width="33%" align="center"><img src="docs/assets/styles/jpmorgan_heavyset_cover.png" width="100%"><br><b>Heavyset</b><br><sub>Dense two-column; heavy sans headings + serif body; grey table headers; tight leading</sub><br><a href="docs/assets/styles/jpmorgan_heavyset_page.png">Interior →</a></td>
</tr>
<tr>
<td align="center"><img src="docs/assets/styles/barclays_cyanline_cover.png" width="100%"><br><b>Cyan Line</b><br><sub>Cyan header band; pale-blue side rail; cyan table headers; light display type</sub><br><a href="docs/assets/styles/barclays_cyanline_page.png">Interior →</a></td>
<td align="center"><img src="docs/assets/styles/bernstein_monochrome_cover.png" width="100%"><br><b>Monochrome</b><br><sub>Strict black and white; black top bar; serif body; tight grid</sub><br><a href="docs/assets/styles/bernstein_monochrome_page.png">Interior →</a></td>
<td align="center"><img src="docs/assets/styles/ubs_swissminimal_cover.png" width="100%"><br><b>Swiss Minimal</b><br><sub>Double title bands; navy + light blue; right-hand info rail; wide margins</sub><br><a href="docs/assets/styles/ubs_swissminimal_page.png">Interior →</a></td>
</tr>
</table>

---

## Showcase

[`examples/unitree_vs_nvidia/`](examples/unitree_vs_nvidia) is one complete run: **can Unitree Robotics `688836.SH` (STAR Market) ever surpass NVIDIA `NVDA` (NASDAQ)?** — from raw data to a laid-out document in the `goldman_hardline` layout.

[PDF (7 pages)](examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf) · [Word](examples/unitree_vs_nvidia/unitree_vs_nvidia.docx) · [Markdown source](examples/unitree_vs_nvidia/unitree_vs_nvidia.md) · [six figures](examples/unitree_vs_nvidia/figures) · [raw data](examples/unitree_vs_nvidia/data) · [proofing renders](examples/unitree_vs_nvidia/proof) · [reproduction scripts](examples/unitree_vs_nvidia/README.md)

<table>
<tr>
<td width="50%"><img src="docs/assets/case/case_page01.png" width="100%"></td>
<td width="50%"><img src="docs/assets/case/case_page03.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Page 1 · cover</sub></td>
<td align="center"><sub>Page 3 · interior</sub></td>
</tr>
</table>

<table>
<tr>
<td width="33%"><img src="docs/assets/case/exhibit1_gap.png" width="100%"></td>
<td width="33%"><img src="docs/assets/case/exhibit2_kline.png" width="100%"></td>
<td width="33%"><img src="docs/assets/case/exhibit4_financials.png" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Peer comparison (log scale)</sub></td>
<td align="center"><sub>Price + volume</sub></td>
<td align="center"><sub>Financial trend (dual axis)</sub></td>
</tr>
</table>

---

## Documentation

| Document | Contents |
|---|---|
| [`pipeline/pipeline_orchestration.md`](pipeline/pipeline_orchestration.md) | Ten-stage flow, gate checklists, artifact formats |
| [`pipeline/agent_prompts.md`](pipeline/agent_prompts.md) | Bilingual brief templates for the eight roles |
| [`methodology/wallstreet_paradigm_manual.md`](methodology/wallstreet_paradigm_manual.md) | Paradigm manual: research logic, evidence discipline, red flags |
| [`templates/styles/README.md`](templates/styles/README.md) | Layout fields and how to author your own |
| [`scripts/data/README.md`](scripts/data/README.md) · [`scripts/charts/README.md`](scripts/charts/README.md) | Data interfaces and chart functions |
| [`VERIFICATION.md`](VERIFICATION.md) | Acceptance action for every deliverable |

---

## Disclaimer

This project is a **methodology and document-engineering demonstration**. Nothing here is investment advice. Data comes from public interfaces and is provided for reference only — always defer to exchange filings and company disclosures. The layout templates are typesetting references containing no firm names or marks, and are not affiliated with or endorsed by any institution.

## License

[MIT](LICENSE) · *You can work for Wall Street.*
