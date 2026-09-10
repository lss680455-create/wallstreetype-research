# Layout Templates — Catalogue & Schema / 版式模板目录与规范

Six **style-only** layout presets for the report renderer. Each `*.json` file is a plain style sheet
(fonts / colours / spacing / table treatment / masthead) that `templates/md_to_docx.py --style <id>`
turns into a Word/PDF report. Nothing here contains institution logos, wordmarks or text marks —
see the [disclaimer](#disclaimer--免责声明).

> Six presets: `goldman_hardline` · `morganstanley_restrained` · `jpmorgan_heavyset` ·
> `barclays_cyanline` · `bernstein_monochrome` · `ubs_swissminimal`
> List them from the CLI: `python scripts/intake/intake.py --list`
> Provenance of the visual characteristics: [`SOURCES.md`](SOURCES.md).

---

## 1. Catalogue / 模板目录

| id | Display name / 显示名 | Style characteristics / 风格特征 | Best for / 适用场景 |
|---|---|---|---|
| `goldman_hardline` | 高盛（硬朗风） / Hardline | Open grid, no boxes; serif masthead + sans body; navy (`#0B2545`); hairline rules; high density. 开放式无框；衬线大标题+无衬线正文；深蓝强调；细线分区；高信息密度。 | Institutional deep-dives, data-dense reports, an authoritative "hard" look. 机构级深度报告、数据密集型。 |
| `morganstanley_restrained` | 摩根士丹利（克制风） / Restrained | Airy single column; light-weight sans masthead; one blue accent (`#0072CE`); wide margins; low density. 大留白单栏；轻字重大标题；单一蓝点缀；宽边距。 | Thesis-driven narratives, readability-first notes, short/medium length. 论点驱动的叙事型长文。 |
| `jpmorgan_heavyset` | 摩根大通（厚重风） / Heavyset | Dense two-column; bold sans headings over serif body; slate-blue (`#1A4C6E`); tight leading. 高密度双栏；粗无衬线标题+衬线正文；灰蓝强调；紧凑行距。 | Full-chain reports with many tables/appendices; maximum information per page. 信息量最大的全链条报告。 |
| `barclays_cyanline` | 巴克莱（青蓝风） / Cyan Line | Cyan header band (`#00AEEF`); tinted right-hand side rail; cyan table header with white text; medium-high density. 青色页眉带；右侧浅蓝信息栏；青底白字表头。 | Bullet-plus-sidebar layouts, chart-heavy notes, a modern accent. 要点+侧栏数据、图表多。 |
| `bernstein_monochrome` | 伯恩斯坦（学术黑白风） / Monochrome | Strict black-and-white; black masthead bar; serif body; dense grid; no colour. 纯黑白；黑顶栏；衬线正文；紧凑网格。 | Academic/quantitative research, B/W printing, deliberately un-marketed. 学术/量化研究、黑白打印。 |
| `ubs_swissminimal` | 瑞银（瑞士极简风） / Swiss Minimal | Two-tier title bands; deep navy (`#001E62`) + pale blue; right info rail; generous margins. 双层标题色带；深海军蓝+浅蓝；右侧信息栏；宽边距。 | Restrained high-end institutional style at medium density. 高端克制的机构风格。 |

---

## 2. Selection guide / 选择指南

| If you want… / 如果你想要… | Pick / 选 |
|---|---|
| Maximum information density, authoritative | `goldman_hardline` or `jpmorgan_heavyset` |
| Maximum readability, narrative flow | `morganstanley_restrained` |
| A coloured, modern accent + sidebar | `barclays_cyanline` |
| Neutral academic look, safe for B/W print | `bernstein_monochrome` |
| Quiet, premium, generous whitespace | `ubs_swissminimal` |
| Many tables / appendices | `jpmorgan_heavyset` |
| Many charts | `barclays_cyanline` (side rail) or `goldman_hardline` (hairline rules) |

Mix & match is allowed: pick a base id and describe overrides in the intake `special_requests`
(e.g. `"base ubs_swissminimal + barclays_cyanline table header"`). The pipeline records the base id
in `brief/intake.json → template_id`.

**Usage / 用法:**

```bash
# list the presets (no files written)
python scripts/intake/intake.py --list

# render a report in a chosen style (S8/S9 of the pipeline)
python templates/md_to_docx.py final/report.md -o final/report.docx --pdf --style goldman_hardline
```

---

## 3. How to add a template / 如何新增模板

1. Copy an existing file (e.g. `goldman_hardline.json` → `mytheme.json`) — the **filename must equal the
   `id`** (`mytheme.json` ↔ `"id": "mytheme"`), lowercase snake_case.
2. Adjust the fields below. Keep every field (no omissions) so the renderer never needs fallbacks.
3. Run a smoke test: `python templates/md_to_docx.py examples/layout_demo/example_report.md -o /tmp/mytheme.docx --style mytheme`
   and check the docx (fonts, colours, margins, tables, rating box).
4. Add a row to §1 and to [`SOURCES.md`](SOURCES.md) if the style was derived from reference material.
5. **Never** add an institution logo, wordmark, watermark, analyst name or other identifier — style
   parameters only (see §4).

### JSON schema / 字段逐项说明

| Field | Type | Meaning / 说明 |
|---|---|---|
| `id` | string | Template id, lowercase snake_case; must equal the filename stem. Used by `--style <id>` and `intake.py --template <id>`. |
| `display_name` | string | Human label: `中文名（风格） / English Style`. Shown by `intake.py --list`. |
| `style_en` | string | One-line English style summary (shown by `intake.py --list`). |
| `style_zh` | string | One-line Chinese style summary (shown by `intake.py --list`). |
| `fonts` | object | `{ "body": …, "heading": …, "mono": … }` — font family names. Use widely available faces (Arial, Georgia, Calibri, Consolas); `layout.h1_font` references one of these keys. |
| `colors` | object | Hex colours **without `#`** (6 uppercase hex digits): `navy` (headings/title), `accent` (links/subheads), `text` (body), `midgray` / `lightgray` (secondary notes), `rule` (hairlines), `table_header_fill` + `table_header_text`, `table_zebra` (fill or `null` = no striping), `rating_box_fill`. |
| `layout` | object | Page geometry & type scale: `margin_lr` / `margin_tb` (inches), `body_size` / `h1_size` / `h2_size` / `h3_size` (pt), `h1_font` (key into `fonts`), `line_spacing` (multiple, e.g. `1.12`). |
| `tables` | object | Booleans: `vertical_rules` (vertical grid lines), `zebra` (alternating row fill), `rule_above_header`, `rule_below_header`. |
| `rating_box` | object | Cover rating/key-data box: `style` (`"open"` = borderless tint, `"rail"` = side rail, `"band"` = full band), `fill` (hex), `border` (bool). |
| `masthead` | object | Cover masthead: `rule_under` (hairline under the masthead), `uppercase_meta` (uppercase the meta line). |
| `_disclaimer` | string | Keep the standard style-only disclaimer verbatim (see §4). |

Minimal skeleton / 最小骨架:

```json
{
  "id": "mytheme",
  "display_name": "我的风格 / My Style",
  "style_en": "One-line English style summary",
  "style_zh": "一句话中文风格说明",
  "fonts": { "body": "Arial", "heading": "Georgia", "mono": "Consolas" },
  "colors": {
    "navy": "0B2545", "accent": "1F4E8C", "text": "333333",
    "midgray": "595959", "lightgray": "8A8A8A", "rule": "CCCCCC",
    "table_header_fill": "E6E6E6", "table_header_text": "000000",
    "table_zebra": null, "rating_box_fill": "F2F4F8"
  },
  "layout": {
    "margin_lr": 0.95, "margin_tb": 0.85, "body_size": 10.0,
    "h1_size": 20, "h2_size": 13, "h3_size": 11.5,
    "h1_font": "heading", "line_spacing": 1.12
  },
  "tables": { "vertical_rules": false, "zebra": false, "rule_above_header": true, "rule_below_header": true },
  "rating_box": { "style": "open", "fill": "F2F4F8", "border": false },
  "masthead": { "rule_under": true, "uppercase_meta": true },
  "_disclaimer": "Layout-style reference only. Visual characteristics were extracted from publicly available research reports; all institution names, logos and text marks are removed. Not affiliated with or endorsed by any institution."
}
```

---

## 4. Disclaimer / 免责声明

**English.** These templates are **layout-style references only**. Their visual characteristics
(typography class, colour palette, grid, table treatment, masthead structure) were extracted from
**publicly available research reports** (provenance in [`SOURCES.md`](SOURCES.md)), then reduced to
plain JSON style parameters. **All institution names, logos, watermarks and text marks have been
removed** — nothing in this folder or in any rendered output reproduces an institution's identity.
The templates are **not affiliated with, endorsed by, or sponsored by any institution**; style names
reference the source institution purely as a descriptive label. Anyone adding a template must follow
the same rule: extract style facts, never copy text, logos or identifiers.

**中文.** 本目录模板仅为**版式风格参考**：其视觉特征（字体类别、配色、网格、表格处理、页眉结构）
提取自**公开可获取的研报**（来源见 [`SOURCES.md`](SOURCES.md)），并抽象为纯 JSON 样式参数。
**所有机构名称、logo、水印与文字标识均已删除**——本目录及任何渲染产物均不含机构身份信息。
模板与任何机构**无关联、未获其背书或赞助**；风格名称仅作描述性标签使用。新增模板必须遵守同一规则：
只提取风格事实，绝不复制文字、logo 或标识。
