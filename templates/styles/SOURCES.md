# Template Sources & Provenance

The six layout themes in this folder are **style-only reconstructions**. Their visual
characteristics (typography class, colour palette, grid, table treatment, masthead structure)
were extracted from **publicly accessible research reports** listed below, then reduced to a
plain JSON style sheet. No text, logos, watermarks, analyst names, disclaimers or any other
institution identifier is reproduced. The themes are **not affiliated with, endorsed by, or
sponsored by any institution**.

| Theme id | Display name | Reference report (public URL) | Extracted characteristics |
|---|---|---|---|
| `goldman_hardline` | 高盛（硬朗风） | Goldman Sachs — Ryanair equity research, 2016-07-27 · https://investor.ryanair.com/wp-content/uploads/2016/09/Goldman-Sachs-2016-07-27.pdf | open grid, serif masthead, navy accent, hairline rules, high density |
| `morganstanley_restrained` | 摩根士丹利（克制风） | Morgan Stanley Research — "Mapping AI's Rate of Change" · https://www.morganstanley.com/content/dam/msdotcom/en/assets/pdfs/Research_AI-Rate-of-Change.pdf | airy single column, light-weight masthead, single blue accent, wide margins |
| `jpmorgan_heavyset` | 摩根大通（厚重风） | J.P. Morgan — Ryanair equity research, 2016-05-26 · https://investor.ryanair.com/wp-content/uploads/2016/06/J.P.-Morgan-2016-05-26.pdf | dense two-column, bold sans headers over serif body, slate-blue accent |
| `barclays_cyanline` | 巴克莱（青蓝风） | Barclays — Ryanair equity research, 2016-07-26 · https://investor.ryanair.com/wp-content/uploads/2016/09/Barclays-2016-07-26.pdf | cyan masthead band, tinted side rail, cyan header row on white text |
| `bernstein_monochrome` | 伯恩斯坦（学术黑白风） | Bernstein Research — Global Pharma, R&D Productivity Trends, 2015-09-22 · https://kmrgroup.com/wp-content/uploads/2015/09/Bernstein-Global-Pharma_22Sept2015_RnD-Productivity-Trends.pdf | strict black-and-white, black masthead bar, serif body, dense grid |
| `ubs_swissminimal` | 瑞银（瑞士极简风） | UBS Investment Research — Global Equity Strategy · http://www.kinsale-capital.com/clientdata/E13-26.pdf | two-tier title bands, deep navy + pale blue, right info rail, generous margins |

## How the extraction was done

1. The reference PDFs were fetched from their public URLs and the cover/first pages were
   rendered to images.
2. A vision-capable model inspected each rendered page and reported **layout facts only**
   (font class, approximate hex palette, column count, margins, table treatment, masthead
   element order, density).
3. Those facts were distilled into the JSON schema documented in `README.md`
   (`fonts` / `colors` / `layout` / `tables` / `rating_box` / `masthead`).
4. All institution names, logos, watermarks and text marks were **removed**; only the style
   parameters remain. Theme names reference the source institution purely as a style label.

## Notes on use

- The themes are layout presets for the report generator (`templates/md_to_docx.py --style <id>`).
- Anyone adding a theme must follow the same rule: extract style facts, never copy text,
  logos or identifiers.
