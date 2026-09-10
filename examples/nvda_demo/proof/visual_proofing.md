# S10 Vision Proofing Record — NVDA Demo Report

- **Artifact:** `examples/nvda_demo/nvda_report.pdf` (9 pages) + `nvda_report.docx`
- **Method:** PDF rendered page-by-page to `pages/page_01..09.png` (pymupdf, dpi=144), then every page
  inspected by a **vision-capable model** (this is the S10 gate — layout is never judged from text alone).
- **Number cross-check:** every core number on the pages verified against `data/numbers.json` (数字引用表).
- **Date:** 2026-09-10

## Per-page results

| Page | Content | Result | Notes |
|---|---|---|---|
| 1 | Cover (rating box / target / price / analyst block) | PASS | all cover elements rendered |
| 2 | Executive Summary + Financial highlights table | PASS | table header (navy/white) visible |
| 3 | Evidence chain + Exhibit 1 (K-line) | PASS | chart within margins |
| 4 | Links 2–4 + Exhibit 2 + Comparable companies table | PASS | table header visible |
| 5 | Peer table (continued) + Exhibit 3 + Exhibit 4 | PASS | repeated header row visible (after fix, see below) |
| 6 | Bear case + Scenarios table | PASS | table header visible |
| 7 | Exhibit 5 (scenario tree) + Risk & Exit + Post-Mortem Hook | PASS | orphaned heading fixed (see below) |
| 8 | Catalyst calendar table + Recommendation + Disclosures | PASS | spelling fixed (see below) |
| 9 | Rating distribution + Appendix (glossary, data sources) | PASS | rounding footnote rendered |

## Defects found by vision proofing and fixed

| # | Page | Defect | Fix |
|---|---|---|---|
| 1 | 5 | Stale render: `pages/*.png` had been rendered from an older PDF — repeated table header showed pale shading + white text (invisible). Current PDF renders it navy/white correctly. | Re-rendered all 9 pages from the final PDF; pipeline rule: **re-render after ANY artifact change**. |
| 2 | 7 | Orphaned lead-in: `Catalyst calendar:` heading sat at the page bottom with its table pushed to page 8. | `md_to_docx.py::_render_table` now sets `keep_with_next` on a short lead-in paragraph (≤150 chars) so it stays with the table. |
| 3 | 8 | Typo: "point target" → should read "price target". | Corrected in `nvda_report.md`; re-converted and re-verified visually. |

## Gate G7 status: **GREEN** (9/9 pages PASS, numbers match the reference table)
