# Layout Theme Proofing — Vision Model Record

**Date:** 2026-09-10 · **Method:** every theme rendered the same NVDA demo
(`examples/nvda_demo/nvda_report.md`) through `templates/md_to_docx.py --style <id> --pdf`,
pages rendered at **150 DPI** and inspected page-by-page by a **vision-capable model**
(no programmatic layout judgement — per the S10 rule). Suspected defects were re-checked on
≥2x cropped zooms before being recorded.

## Per-theme result (cover + body pages)

| # | Theme (id) | Cover | Body page | Table style | Defects found |
|---|------------|-------|-----------|-------------|---------------|
| 1 | Goldman-style / hardline (`goldman_hardline`) | PASS | PASS | grey header, horizontal rules only | none |
| 2 | MS-style / restrained (`morganstanley_restrained`) | PASS | PASS | minimal, airy, single accent | none |
| 3 | JPM-style / heavyset (`jpmorgan_heavyset`) | PASS | PASS | grey-blue header, dense | none |
| 4 | Barclays-style / cyanline (`barclays_cyanline`) | PASS | PASS | cyan header, white text | none |
| 5 | Bernstein-style / monochrome (`bernstein_monochrome`) | PASS | PASS | black header, white text | none |
| 6 | UBS-style / swiss minimal (`ubs_swissminimal`) | PASS | PASS | navy header + pale zebra | none |

Cross-checks: six themes visibly distinct (fonts, palette, density, table style);
no overlap / overflow / clipping / misalignment; **no logo, watermark or institution
identifier of any kind**; default theme (no `--style`) unchanged at 9 pages.

## False findings caught by zoom (and why the zoom rule exists)

| Thumbnail claim | Zoomed truth | Root cause |
|---|---|---|
| Bernstein header "white background" | black header, white text (`#000000` fill, pymupdf-verified) | low-res thumbnail |
| UBS "pale blue zebra missing" | zebra present (`#F2F5FA`, rows 2 & 4) | fill too pale at thumbnail scale |
| JPM table header "Fical year" | `Fiscal year` (docx + PDF text layer both correct) | serif glyph misread at low res |

All three were **excluded** after zoom re-check. Rule added to
`pipeline/pipeline_orchestration.md` (S10) and `pipeline/agent_prompts.md`:
*render ≥144 DPI, zoom ≥2x before recording a finding.*

## Real defects found and fixed in this pass

| Defect | Fix |
|---|---|
| Heading `2. Stance — …` wrapped with the last word alone on line 2 (4 themes) | shortened heading text in `examples/nvda_demo/nvda_report.md`; verified single-line via PDF word coordinates in all themes |
| `md_to_docx.py --pdf` reported success while leaving a **stale PDF** (Word COM silent failure, hit 2× on one theme) | added freshness check (`PDF mtime ≥ docx mtime`) + 3-attempt retry in `templates/md_to_docx.py` |

## Reproduce

```bash
for t in goldman_hardline morganstanley_restrained jpmorgan_heavyset \
         barclays_cyanline bernstein_monochrome ubs_swissminimal; do
  python templates/md_to_docx.py examples/nvda_demo/nvda_report.md \
    -o "out/nvda_$t.docx" --style "$t" --pdf
done
# then render page 1 of each PDF to PNG (≥144 DPI) and inspect with a vision model
```
