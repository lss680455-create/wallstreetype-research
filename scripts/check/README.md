# scripts/check — 质量门 / Quality Gates

The **J1 machine gate** for the pipeline. Runs on the final report Markdown plus its
data layer; used at stage **S9** (see `pipeline/pipeline_orchestration.md` §8) and
available standalone for any repo clone.

## build_check.py — usage

```bash
# from the repo root (report + numbers.json + data/ in the same run directory)
python scripts/check/build_check.py runs/ws_20260910_ab12/final/report.md

# quiet PASS-details / machine-readable JSON
python scripts/check/build_check.py final/report.md --verbose
python scripts/check/build_check.py final/report.md --json
```

Exit code: **0 = gate passed (no FAIL), 1 = at least one FAIL — never publish on 1.**

## Check families

| Family | What it verifies |
|---|---|
| J1-a placeholders | no `{{...}}` residue in the report body (the template file is exempt) |
| J1-b exhibits | every `![alt](path)` figure file exists; "Exhibit N" mentions stay in 1..K |
| J1-c numbers | every number in the **数字引用表** (`numbers.json`) reconciles data JSON → report text (tolerance-based; `data_match` / `derived_match` / `raw`) |
| J1-d frontmatter | required fields, analysts list, `upside ≈ target/current − 1` (1% tolerance) |
| J1-e tables | column-count consistency, non-empty headers, configured key rows/cells |
| J1-f registry | numbers.json exists to enable J1-c/J1-e |

## 数字引用表 — numbers.json (the number reference table)

Convention: `numbers.json` next to the report, or `--numbers <file>`. Each check:

```json
{"id": "current_price", "kind": "data_match",
 "file": "data/nvda_quote.json", "path": "quote.regularMarketPrice",
 "decimals": 2, "display_fmt": "$224.22"}
```

- `data_match` — data JSON value (with `scale`, `percent`, `suffix`, `agg: median`,
  `paths: [...]`) must appear in the report text within `tolerance` (default 0.1% rel).
- `derived_match` — compute from `num`/`den` sources (`["file", "dotted.path"]`,
  `["@frontmatter", "field"]`, `["@literal", value]`, or `num_expr` chains) with
  `op: ratio | ratio_minus_1 | one_minus_ratio`, then compare to the number captured
  by `regex` (or `expected`) within `tol_pp` (percentage points, percent unit) / `tol`.
- `raw` — a literal expected value must exist in the text.
- `scope: "frontmatter"` — the value is expected on the cover (frontmatter), not the body.

Table checks:

```json
"tables": {
  "required_rows": [{"table_contains": "Fiscal year", "label_col": 0,
                     "rows": ["FY2023", "FY2024"]}],
  "required_cells": [{"table_contains": "Fiscal year", "row": "FY2026",
                      "cells": [{"col": 1, "computed": {"op": "ratio",
                                 "num": ["data/f.json", "financials.modules.incomeStatementHistory.0.totalRevenue"],
                                 "den": ["@literal", 1e9], "decimals": 2}}]}]
}
```

**Rule: 数字未登记引用表 = 违规范** — any core number in a report that is not
registered here fails gate G7 at S9.

## Notes for other data layouts

- Default data dir = the report's directory (`--data-dir` to override); JSON paths
  are dotted (`modules.financialData.targetMeanPrice`). For `nvda_financials.json`
  the wrapper is `financials.modules...`.
- Unicode minus (`−`) and en-dash (`–`) are normalized to `-` before matching.
- Numbers in markdown-bold cells (`**NVIDIA**`) are cleaned before table checks.
