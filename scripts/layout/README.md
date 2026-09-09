# Layout Layer — Wall Street Report Formatting & Conversion Pipeline

This directory defines the **presentation layer** of the research skill: the
sell-side report conventions it follows, the Markdown → Word/PDF conversion
pipeline, and the templates that implement it. It is deliberately
agent-agnostic: the source of truth is a plain Markdown file, and every
conversion step is a standalone Python script with no runtime dependencies
beyond the packages listed below.

```
wallstreet-research/
├── templates/
│   ├── report_template.md      ← Markdown MASTER template ({{PLACEHOLDER}}-based)
│   └── md_to_docx.py           ← standalone converter: .md → .docx (→ .pdf)
├── scripts/
│   └── layout/
│       └── README.md           ← this file (layout engineering notes)
└── examples/
    └── layout_demo/            ← worked example (template filled in + outputs)
        ├── example_report.md
        ├── assets/…png         ← placeholder charts
        └── output/…docx/pdf    ← verified conversion outputs
```

---

## 1. Wall Street report conventions (research basis)

Findings synthesized from public Goldman Sachs, Morgan Stanley and
J.P. Morgan research reports and sell-side formatting guides (sources listed
at the end). The template implements these directly.

### 1.1 Cover page (Page 1)

| Element | Convention | Where in template |
| --- | --- | --- |
| Firm line + date | Firm name top-left, report date top-right, thin rule | auto-generated from `firm` / `date` |
| Report-type banner | `EQUITY RESEARCH` (small caps) over `INITIATION OF COVERAGE` / `COMPANY UPDATE` / `SECTOR REPORT` | auto from `report_type` |
| Company identity | Company name (large), ticker · exchange · sector line | auto from `company` / `ticker` / `exchange` / `sector` |
| Headline title | The analyst's sentence-long title ("Updating estimates…", "Riding the margin-inflection wave…") | auto from `title` |
| Rating / Key-data box | Shaded 4-column box: **Rating · Target Price · Current Price · Upside/(Downside)**; GS also prints Market Cap, EV, 12-mo target, upside % | auto from `rating`, `target_price`, `current_price`, `upside` |
| Price-performance chart | 12-month price chart with relative index, under the key-data box | `price_chart` frontmatter path |
| Analyst block | Name + title + phone + email + firm entity ("Goldman Sachs International") | `analysts` frontmatter list |
| Conflict-of-interest line | "…does and seeks to do business with companies covered in its research reports… consider this report as only a single factor…" | `disclosure_conflict` frontmatter |
| Fine-print footer | © year + "See important disclosures on the final pages" | auto |

### 1.2 Executive Summary (Page 2)

- Opens with rating + target price + implied upside/downside in one sentence.
- GS-style bold lead-ins: **What's changed.** / **Implications** / **Valuation** / **Key risks.**
- Thesis in 3 numbered pillars; top-3 risks in one line.
- Small financial-highlights table (A/E columns: revenue, EBITDA margin, EPS, FCF yield, leverage).
- "Source: …" line directly under every table/figure (small gray type).

### 1.3 Body hierarchy (H1 → H4)

- H1 = numbered major sections (auto-numbered `1.`, `2.`, …): Company Overview, Financial Analysis, Valuation, Investment Thesis, Catalysts, Risk Factors, Recommendation, Analyst Certification, Disclosures, Appendix.
- H2/H3/H4 = sub-sections; H3/H4 used for segment detail, methodology sub-parts.
- Rating scales: GS = Buy/Neutral/Sell + Conviction List; MS & JPM = Overweight/Equal-weight/Underweight (+ Not-Rated). **Pick one scale and state it** — the template's Rating Definitions section shows the relative-scale wording.

### 1.4 Tables

- Compact grid: ~8.5 pt type, navy header row with white bold text, light zebra striping, thin light-gray rules.
- Numeric columns right-aligned automatically (≥60% of cells parse as numbers).
- Caption line directly above a table (`Exhibit N: …` / `Table N: …`) → styled caption; a `Source:` line directly below → small gray source note.

### 1.5 Figures

- Numbered **"Exhibit N: <caption>"** above each chart (Wall Street numbering convention), image centered, optional `Source:` line below. Numbering is automatic and document-wide.

### 1.6 Risks & disclosures (back matter)

- Risk Factors: categorized bullets (business/operational, financial, regulatory/macro, market).
- Recommendation: rating definition, key assumptions to monitor, next catalyst date.
- Analyst Certification (Reg AC-style): "…views accurately reflect my personal views, not influenced by firm business/client relationships…".
- Disclosures & Disclaimer: analyst interests, nature of report (not investment advice), forward-looking statements, no-warranty, distribution/copyright.
- Appendix: FINRA-style rating-distribution table (% of universe, % of investment-banking clients), glossary, data sources.

### 1.7 Header / footer

- Header (body pages): company (TICKER) left, date right, thin rule.
- Footer: firm name left, **"Page X of Y"** right (live Word fields).
- Cover page carries no header/footer.

---

## 2. Pipeline design

```
                source of truth            editing/submission         distribution
  report.md ───────────────────►  report.docx ──────────────────►  report.pdf
  (Markdown master,             (python-docx renderer,           (docx2pdf via MS Word,
   git/GitHub friendly)          Wall Street styles)               or pandoc / typst)
```

- **Master format = Markdown.** Version control, diffs, and GitHub rendering all work on the `.md`; docx/PDF are generated artifacts, never hand-edited.
- **docx = python-docx renderer** (`md_to_docx.py`). Chosen over pandoc because Wall Street styling (cover layout, shaded rating box, navy table headers, header/footer with live page fields, Exhibit numbering) needs programmatic control that pandoc's default docx writer does not give. Pure Python, no C toolchain.
- **PDF**: default path is `docx2pdf` (drives Microsoft Word — best fidelity). Alternatives if Word is unavailable: **pandoc + LaTeX/wkhtmltopdf** (one install), **typst** (single binary), or Edge/Chrome headless print-to-PDF from HTML. All are documented in §5.

## 3. Installation

```bash
# core (required)
pip install python-docx markdown

# PDF via Microsoft Word (optional, Windows/macOS with Word installed)
pip install docx2pdf

# PDF alternatives (optional, pick one)
winget install JohnMacFarlane.Pandoc      # Windows: pandoc (+ LaTeX engine for PDF)
# or: choco install pandoc
# or: install typst from https://typst.app (single binary)
```

Python ≥ 3.9. No other runtime dependencies.

## 4. Usage

```bash
# create a report from the template
cp templates/report_template.md my_report.md
#   → replace every {{PLACEHOLDER}} (see §6)

# convert to Word
python templates/md_to_docx.py my_report.md

# convert to Word + PDF
python templates/md_to_docx.py my_report.md --pdf

# options
python templates/md_to_docx.py my_report.md -o out/report.docx   # custom output path
python templates/md_to_docx.py my_report.md --toc                # insert a Table of Contents field
python templates/md_to_docx.py my_report.md --no-numbering       # unnumbered H1 sections
```

The script is a single self-contained file; copy it into any project or CI
step. It reads only the input `.md` (images are resolved relative to the `.md`
location).

## 5. PDF paths — decision matrix

| Path | Command | Pros | Cons |
| --- | --- | --- | --- |
| **docx2pdf** (default) | `--pdf` flag | Pixel-faithful to the docx; uses installed Word | Requires MS Word (Windows/macOS) |
| pandoc → PDF | `pandoc my.md -o my.pdf` | Cross-platform, no Word | Needs a PDF engine (LaTeX/wkhtmltopdf); loses the WS cover/rating-box styling unless you add a reference-doc + CSS |
| typst | `typst compile my.typ` | Single binary, fast, beautiful | Requires re-authoring the template in Typst markup |
| Browser print | Edge/Chrome `--headless --print-to-pdf` | No installs | Requires an HTML renderer for the markdown |

Recommendation: ship `docx2pdf` as the default; keep the `.docx` as the
always-available artifact, since Word's own *Save As PDF* is the universal
fallback.

## 6. Placeholder convention

Every variable is an uppercase name in double braces: `{{TICKER}}`, `{{TARGET_PRICE}}`, `{{ANALYST_1_NAME}}`, … 

- **Frontmatter** (YAML between the first two `---` lines) drives the cover, rating box, analyst block, header/footer and disclosure line. Replace each `{{…}}` value there.
- **Body text**: any `{{FIELD}}` matching a frontmatter key is auto-substituted at conversion time (e.g. `{{target_price}}` prints the value of `target_price`). Lowercase keys in body refer to the same frontmatter fields.
- Optional fields may be deleted or left empty; the renderer skips them gracefully.
- A worked, fully-filled example lives in `examples/layout_demo/example_report.md` — the fastest way to learn the convention is to diff it against the template.

## 7. Styling reference (what the renderer applies)

| Item | Specification |
| --- | --- |
| Page | US Letter, margins 0.95" sides / 0.85" top-bottom |
| Body font | Calibri 10 pt, 1.08 line spacing (East-Asian face 等线/DengXian for Chinese) |
| H1 / H2 / H3 / H4 | Calibri 14 / 12 / 11 / 10.5 pt, navy (#0B2545) → dark gray, H1 with rule |
| Company name (cover) | 25 pt bold navy |
| Rating box | Navy header row (white caps labels), light-blue-gray data row, navy border; rating value color-coded (OW=green, EW=amber, UW=red) |
| Tables | 8.5 pt, navy header fill (#1F3864, white bold), zebra #F2F4F8, grid #C9CFD8, numeric columns right-aligned |
| Exhibits | Caption "Exhibit N: …" above chart, centered, ≤5.8" wide |
| Source lines | 7.5 pt gray italic |
| Blockquotes | 9.5 pt gray italic with navy left bar |
| Header / footer | 8 pt; footer "Page X of Y" via live PAGE/NUMPAGES fields |

Colors are defined as constants at the top of `md_to_docx.py` (`NAVY`,
`ACCENT`, `SHADE_HEAD`, …) — retheme by editing six lines.

## 8. Known limitations

- Nested markdown lists are not supported (flat lists only).
- Table of Contents is a Word field: select it in Word and press F9 / *Update Field* to populate.
- Table column widths are distributed equally; for heavily unequal tables, split or restructure the table.
- Image paths are relative to the `.md` file; missing images render as a visible `[missing image: …]` note instead of failing.

## 9. Sources (conventions research)

- Goldman Sachs — "Ryanair (RYA.I): Updating estimates post 1Q17 results; remain Neutral" (public PDF): cover anatomy, What's-changed/Implications/Valuation/Key-risks summary, key-data box, analyst block, conflict line, disclosure appendix.
- Morgan Stanley — General Research Disclosures (morganstanley.com/eqr/disclosures): Overweight/Equal-weight/Not-Rated/Underweight definitions, 12–18-month horizon, ratings-distribution table, analyst compensation disclosure.
- J.P. Morgan Global Research — rating system Overweight/Neutral/Underweight.
- Mergers & Inquisitions — "What's in an Equity Research Report?"; FanRuan — "Equity Research Report: Format, Template and AI Automation": typical section order and page-1 update conventions.
