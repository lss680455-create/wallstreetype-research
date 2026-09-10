# Wall Street Research Skill — Independent Critical Verification Report

- **Verifier:** independent subagent (critical review — tasked to find faults, not confirm)
- **Date:** 2026-09-10 (CST)
- **Scope:** 10 verification domains (A–J) over `<repo-root>\`
- **Method:** live command execution, file parsing, magic-byte checks, network spot-checks. Every PASS below was demonstrated with tool output, not assumed from file existence.

---

## Summary Table

| # | Check item | Result | Evidence | Problems found |
|---|---|---|---|---|
| A1 | Root files present: README.md / SKILL.md / requirements.txt | PASS | All exist (README 6,757 B; SKILL 3,776 B; requirements 613 B) | none |
| A2 | methodology/ complete: report_list_100.md + digests/ (10 files) | PASS | report_list_100.md (32 KB) + digests/group1..10.md all present (+ seed_30_reports.md) | none |
| A3 | pipeline/ 2 docs present | PASS | pipeline_orchestration.md (33.5 KB), agent_prompts.md (44.7 KB) | none |
| A4 | scripts/{data,charts,layout} present | PASS | data: 5 .py + README; charts: 2 .py + README + sample_pngs/ (5 PNG); layout: README.md | scripts/layout/ contains only a README (layout code lives in templates/ — documented, consistent) |
| A5 | templates/ + examples/layout_demo/ present | PASS | templates/{md_to_docx.py, report_template.md}; examples/layout_demo/{example_report.md, assets/, output/} | none |
| A6 | Every path referenced in README.md / SKILL.md exists on disk | PASS | 19/19 referenced paths verified `os.path.exists` = True (incl. sample_pngs/, output/example_report.docx/pdf) | none |
| A7 | Internal tree diagrams match real structure | WARN | — | `scripts/layout/README.md` (lines 10–23) self-describes as living at `design/layout/README.md` with example at `design/layout/example/` — stale `design/` path contradicts actual `scripts/layout/` + `examples/layout_demo/`. README.md tree also uses two `└──` at same level under methodology/ (cosmetic) |
| B1 | requirements.txt covers data-layer imports | PASS | imports = requests, certifi (+pysocks runtime via socks5:// scheme; not directly imported — correct usage); all in requirements.txt | none |
| B2 | requirements.txt covers charts-layer imports | PASS | matplotlib, mplfinance, pandas, numpy — all imported by scripts/charts/*.py and all listed | none |
| B3 | requirements.txt covers layout-layer imports | PASS | python-docx (docx), markdown, docx2pdf (conditional `--pdf` import at md_to_docx.py:1016) — all listed | none |
| C1 | All 5 data .py pass py_compile | PASS | `python -m py_compile common.py data_fetcher.py get_financials.py get_history.py get_quote.py` → COMPILE_OK, exit 0 | none |
| C2 | `python data_fetcher.py us NVDA quote` runs & returns sane values | PASS | NVIDIA price=**224.225 USD**, mktCap=**5,414,360,973,312** (5.41T), PE=**28.38**, PB=23.64 — inside NVDA 150–300 range, PE > 0 | none |
| C3 | `python data_fetcher.py cn 600519 quote` runs & returns sane values | PASS | 贵州茅台 price=**1290.88 CNY**, PE(TTM)=**19.82**, PB=6.42, MV=16,137亿 — inside 800–2000 range, PE > 0 | none |
| C4 | common.py proxy/GBK/cookie/rate-limit logic sound | PASS | SOCKS5 default `socks5h://127.0.0.1:10808` + `YAHOO_PROXY` env override; `trust_env=False` (Windows registry-proxy trap documented); certifi CA bundle; crumb via fc.yahoo.com 404-cookie pattern; 429/"Too Many Requests" retry w/ backoff; 1.2 s rate-limit sleep; Tencent GBK decode (`decode('gbk','replace')`); CN symbol normalization sh/sz/bj | none found |
| D1 | 5 sample PNGs exist, PNG magic, >100 KB | PASS | 01..05 all `89 50 4E 47 0D 0A 1A 0A`; sizes 263,270–779,636 B (all >100 KB) | none |
| D2 | report_charts.py actually runs & generates charts | PASS | Ran live: regenerated all 5 charts ("wrote … 01..05 .png"), exit 0, ~7 s | none |
| D3 | chart_style.py CJK font detection (SimHei/Microsoft YaHei fallback) exists | PASS | `detect_cjk_font()`: priority Microsoft YaHei > SimHei > DengXian > SimSun > KaiTi; direct system-font file scan + matplotlib registry fallback + DejaVu Sans final fallback; `axes.unicode_minus=False`. Runtime confirmed: "[chart_style] CJK font -> Microsoft YaHei" | none |
| E1 | example_report.docx / .pdf exist and >30 KB | PASS | docx=84,098 B; pdf=464,839 B; valid magic (PK\x03\x04 / %PDF-) | none |
| E2 | templates/md_to_docx.py actually converts example_report.md → docx | PASS | Ran: `md_to_docx.py examples/layout_demo/example_report.md -o …` → "[ok] docx written (84,098 bytes)", exit 0 (test artifact removed after check) | none |
| E3 | report_template.md {{PLACEHOLDER}} convention exists | PASS | 91 `{{` occurrences ({{FIRM_NAME}}, {{TICKER}}, {{TARGET_PRICE}}, {{ANALYST_1_NAME}}…); body `{{FIELD}}` auto-substitution implemented in md_to_docx.py | none |
| F1 | report_list_100.md = exactly 100 data rows | PASS | Programmatic parse: **100** rows | none |
| F2 | 10 groups × 10 reports each | PASS | G1..G10 each = 10 rows; 10 `## Gx` headers | none |
| F3 | Each row = exactly 7 fields (组号\|标题\|机构\|分析师\|年份\|URL\|可学点) | PASS | 0 rows with ≠7 fields; 0 non-http URLs; 0 duplicate URLs | none |
| F4 | URL spot-check (≥6 URLs, different groups) | WARN | 13 URLs sampled, 1 per group (G1–G10) + 3 extra in G7; 12 return real content matching their titles (Fortune, Goldman ×2, Morgan Stanley ×2, CNN, NYT PDF, CNBC, Wikipedia, Hindenburg ×3, SevenPillars, Bloomberg) | **1 dead URL: G7 `https://stansberryresearch.com/the-100-data-set` → HTTP 404** (confirmed twice: web_extract + direct requests). Dead rate in sample ≈ 7.7% |
| G1 | 10 digests × 10 '### ' entries | PASS | group1..10 each have exactly 10 `### ` entries (100 total) | none |
| G2 | Every entry has 5 dimensions + 可执行规则 line | PASS | 100/100 entries verified (lenient keyword check): 5 dims + rule present in every entry | none |
| G3 | Dimension label standardization | WARN | — | 3 naming schemes across groups: CN+EN ("研究方法 Method") in g1; CN-only in g2/4/5/8/9; EN-only ("Research method", "Writing paradigm", "Chart style", "Reusable moves", "Lessons/red flags") in g6/10; 教训 label also varies ("教训或红旗" vs "教训/红旗"); rule-line prefix varies (`- **可执行规则**` vs `**可执行规则 (Executable Rules)**`). Content complete; labels not uniform |
| H1 | pipeline_orchestration.md: 8 stages, chained start-to-finish | PASS | S2 Input&Envelope → S3 Master Brief → S4 Parallel Research → S5 Red Team → S6 Editorial Adjudication → S7 Charting → S8 Layout → S9 Final Review & Delivery; each has Who/Input/Output/quality gate (G0..G6) with fail-loops; S2 output (envelope.json) consumed by S3 … S8 output consumed by S9 | none |
| H2 | agent_prompts.md: ≥6 roles × bilingual briefs | PASS | 6 roles (Data Engineer, Industry Analyst, Valuation Analyst, Red Team, Chart Specialist, Layout Specialist) × EN+ZH = 12 substantive brief sections (role/task/input/output/steps/quality checklist) | none |
| H3 | No stale paths in the 2 pipeline docs | PASS | Zero occurrences of `src/data`, `src/charts`, `src/layout`, `design/` in either doc | (stale `design/` only found in scripts/layout/README.md — outside pipeline docs, flagged at A7) |
| I1 | Script names consistent across docs & disk | PASS | data_fetcher.py / report_charts.py / md_to_docx.py referenced correctly in README, SKILL, both pipeline docs and layer READMEs; all names match on-disk files; helper names (get_quote.py, get_history.py, get_financials.py, chart_style.py, common.py) also consistent | none |
| J1 | NVDA market cap ~$5T-scale | PASS | 5.41T USD (live fetch + nvda_demo/data/nvda_quote.json identical) | none |
| J2 | NVDA PE 25–35 | PASS | trailingPE 28.38 (forward 14.4) | none |
| J3 | Moutai PE 15–25 | PASS | PE(TTM) 19.82 | none |
| J4 | Quote data traceable to live API (not hand-typed) | PASS | Live fetches returned identical values to committed nvda_demo JSON; values consistent between quote and history runs (close 1290.88 both) | none |
| X1 | wallstreet_paradigm_manual.md status | NOTE | **File EXISTS** (62,835 chars; chapters 1–7 confirmed) — the "paradigm-manual subagent" deliverable has landed. Per task instruction, if missing we would skip; since present, light structure check passed. Deep content review is outside the 10 domains and deferred | none checked beyond structure |

---

## Per-Domain Rollup

| Domain | PASS | FAIL | WARN |
|---|---|---|---|
| A — Directory structure & path consistency | 6 | 0 | 1 |
| B — requirements.txt coverage | 3 | 0 | 0 |
| C — Data layer | 4 | 0 | 0 |
| D — Charts layer | 3 | 0 | 0 |
| E — Layout layer | 3 | 0 | 0 |
| F — 100-report list | 3 | 0 | 1 |
| G — 10 digests | 2 | 0 | 1 |
| H — Pipeline docs | 3 | 0 | 0 |
| I — Script-name consistency | 1 | 0 | 0 |
| J — Data plausibility | 4 | 0 | 0 |
| **Total** | **32** | **0** | **3** |

---

## Fix-Recommendation List (all WARN-level; no FAIL found)

1. **Replace the dead URL in G7 (must-fix before GitHub publish):**
   `methodology/report_list_100.md` row G7 "The Subprime Short: The 100 Data Set" → `https://stansberryresearch.com/the-100-data-set` returns **404**.
   Suggested: swap to an authoritative source for Michael Burry / the subprime short thesis (e.g. a stable profile/article — Fortune/Wikipedia "Michael Burry" or a documented Scion Capital write-up), or verify the correct current Stansberry path. Re-run the URL check afterward.
2. **Fix stale `design/` tree in `scripts/layout/README.md` (lines 10–23):** the tree diagram says this README lives at `design/layout/README.md` and the example at `design/layout/example/`. Update to the real paths `scripts/layout/README.md` and `examples/layout_demo/` (+ `templates/` sibling layout already correct in the same tree).
3. **Standardize digest dimension labels (optional, cosmetic):** groups 6/10 use English-only labels, others CN-only or CN+EN; 教训 label differs ("或红旗" vs "/红旗"). If the repo promises a uniform 5-dimension convention (README: "each digested across 5 dimensions"), align labels to one scheme — e.g. `- **研究方法 Method**: … - **行文范式 Writing**: … - **图表特征 Charts**: … - **可复用标准动作 Reusable moves**: … - **教训或红旗 Lessons**: …` — or explicitly document the variants in the README. Content is complete in all 100 entries either way.
4. **Cosmetic:** README.md repository tree uses two `└──` at the same indentation under `methodology/` (digests + paradigm manual); change the first to `├──` for correct tree rendering.
5. **Optional hardening (not required):** a URL-liveness check for all 100 URLs before publishing (sample found 1/13 dead; a full sweep is cheap with the same requests approach used here). Also consider documenting that `scripts/layout/` intentionally holds only engineering notes while the renderer lives in `templates/` (currently only implied by comments).

---

*Note: `examples/nvda_demo/` (real fetched NVDA data + 5 figures) exists as an extra asset; `make_nvda_charts.py` compiles. The paradigm manual exists and shows chapters 1–7; per instructions its deep content review is deferred to the manual subagent's own completion pass.*

---

## Addendum — S1 industry-logic ring & stage renumbering

- **Pass:** second, by the main agent (not the independent verifier above) — recorded separately so the original
  report is not retro-edited. **Date:** 2026-09-10 (CST).
- **Change under test:** a new ring **S1 — Industry Logic Mapping & Direction Check** (five-move industry map +
  six direction-confirmation questions, gate **G0b**) inserted between intake and the envelope; former S1–S9
  shifted to **S2–S10**; gates renamed to keep the pre-run family in sequence (G0 → G0b → G0c → G0d, then G1–G7).
- **Rows above superseded by this pass:** **A3** (`pipeline/` now holds four docs, not two), **H1** (the description
  "8 stages … G0..G6" is superseded: the pipeline is now 11 stages S0–S10 with gates G0, G0b, G0c, G0d, G1–G7),
  **H2** (six role briefs → seven, plus the main-agent protocol).

| # | Check item | Result | Evidence |
|---|---|---|---|
| K1 | Renumbering left no stray stage token | PASS | `python scripts/verify_consistency.py` check 1 — no `S` token > 10 anywhere in the tree |
| K2 | Stage list is contiguous and ordered | PASS | check 2 — `### Sx —` headings read S0 → S1 → … → S10 in `pipeline_orchestration.md` |
| K3 | Every stage owns exactly one gate, mapping is collision-free | PASS | check 3 — S0→G0, S1→**G0b**, S2→G0c, S3→G0d, S4→G1 … S10→G7 |
| K4 | The six questions exist on every surface that promises them | PASS | check 4 — `logic_mapping.md` 6/6, `README.md` 6/6, `README_EN.md` 6/6, `direction_check.py` 6/6 |
| K5 | Gate G0b is machine-enforced, not documentation | PASS | `direction_check.py --check` on the shipped sample → **29 checks, exit 0**; the same file with `answered_by="agent-default"` → **exit 1** (check 7 of `verify_consistency.py` runs both) |
| K6 | The new ring is demonstrated end-to-end, not promised | PASS | `examples/unitree_vs_nvidia/brief/`: `industry_logic.md` (written by `make_logic_brief.py`) + `direction_confirmed.json` (passes G0b). Sample is labelled a retro-fit in-file |
| K7 | No hand-typed figure entered the S1 sample | PASS | check 8 — every numeric token in `brief/industry_logic.md` resolves to a value in `data/numbers.json` |
| K8 | Downstream roles actually consume the ring | PASS | `agent_prompts.md`: industry brief 0-binding line + `industry_logic.md`/`direction_confirmed.json` inputs; valuation brief takes `view`/`assumption_anchor`; red team takes the user's `falsification` as its brief; protocol step 1 + two discipline rules |
| K9 | No depth tier can skip the direction check | PASS | `pipeline_orchestration.md` §12: `quick` row now includes S1; S0 + S1 are tier-exempt |
| K10 | Docs and artwork match the 11-stage reality | PASS | README/README_EN feature bullet, Quick-start block (six-question table + three CLI commands), architecture alt text, repo tree, docs nav; `docs/assets/architecture.png` regenerated from `STAGES` and re-checked visually (11 rows, all gate codes present, no clipping or overlap) |
| K11 | Links and anchors still resolve | PASS | `verify_consistency.py` check 5 — 0 broken across the three READMEs |
| K12 | Commands printed in the new docs actually run | PASS | `direction_check.py --questions / --skeleton / --check`, `make_logic_brief.py`, `verify_consistency.py` all executed from a clean shell with exit 0 |

**Addendum rollup: 12 PASS / 0 FAIL / 0 WARN.** Reproduce with one command:

```bash
python scripts/verify_consistency.py    # 8/8 checks passed
```
