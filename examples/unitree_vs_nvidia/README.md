# Case study — Unitree Robotics vs NVIDIA

This folder is the **end-to-end walk-through** of the pipeline: it shows what comes out when you point the toolkit at a real question and let it run start to finish.

> It is a **deliverable demo**, not documentation. For features, architecture and usage, see the [project README](../../README.md).

## The question

> Could Unitree Robotics (宇树科技, `688836.SH`) ever surpass NVIDIA?

Picked because it forces every layer of the toolkit to work at once: a freshly listed A-share with a short trading history, a US mega-cap, two currencies, and a comparison that is genuinely uncomfortable for both sides.

## Spec (what was handed to the pipeline)

| Item | Value |
|---|---|
| Coverage | 宇树科技 `688836.SH` (SSE STAR Market) vs NVIDIA `NVDA` (NASDAQ) |
| A-share data | Tencent Finance + East Money — quotes, daily bars, F10 main indicators |
| US data | Yahoo Finance — quote, daily bars, financialData module |
| FX | USD/CNY from Yahoo |
| Hard constraint | **Every number in the report and in the charts is computed from the fetched JSON — nothing is hand-typed** |
| Layout | `goldman_hardline` |
| Output depth | Standard single-company tier (≈7 pages) |

## Reproduce it

```bash
cd <repo root>

# 1. fetch (A-share direct; set the proxy for the US side if needed)
export YAHOO_PROXY=socks5h://127.0.0.1:10808
python scripts/data/data_fetcher.py cn 688836 all --json > examples/unitree_vs_nvidia/data/unitree_all.json
python scripts/data/data_fetcher.py us NVDA  all --json > examples/unitree_vs_nvidia/data/nvda_all.json

# 2. every number the report uses
python examples/unitree_vs_nvidia/compute_numbers.py      # -> data/numbers.json

# 3. the six exhibits
python examples/unitree_vs_nvidia/make_case_charts.py     # -> figures/*.png

# 4. the document
python templates/md_to_docx.py examples/unitree_vs_nvidia/unitree_vs_nvidia.md \
       --style goldman_hardline --pdf

# 5. S9 proof renders (page-by-page visual QC)
python -c "import pymupdf;d=pymupdf.open('examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf');[d[i].get_pixmap(dpi=110).save(f'examples/unitree_vs_nvidia/proof/page{i+1:02d}.png') for i in range(d.page_count)]"
```

Measured runtime on the author's machine (Windows, direct domestic network): fetch **1.7 s** · compute **0.2 s** · charts **6.8 s** · Word/PDF export **10.3 s**.

## What's in here

| Path | Contents |
|---|---|
| `unitree_vs_nvidia.md` | Source report, with the YAML front matter that drives the cover and rating box |
| `unitree_vs_nvidia.docx` | Exported Word document (editable) |
| `unitree_vs_nvidia.pdf` | Exported PDF, 7 pages |
| `compute_numbers.py` | Raw JSON → every figure used in the text and charts |
| `make_case_charts.py` | Builds the six exhibits (five reuse the repo's chart families) |
| `data/` | `unitree_all.json`, `nvda_all.json`, `numbers.json` |
| `figures/` | The six exhibits as standalone PNGs |
| `proof/` | Page-by-page renders used for the S9 visual gate |

## Notes for anyone reusing this

- The A-share side is fetched live, so numbers will drift from the copy committed here — that is expected; the scripts recompute everything.
- Two chart-family bugs were fixed while building this case (scenario-bar colour/order mapping for non-English scenario names, and short-series K-line axis handling). The fixes live in `scripts/charts/report_charts.py`, not in this folder.
- The report is a **methodology demonstration**. It is not investment advice.
