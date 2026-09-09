#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_to_docx.py — Wall Street-style Markdown → Word (.docx) converter.

Renders an equity research report written against templates/report_template.md
into a Word document that follows sell-side conventions (Goldman Sachs /
Morgan Stanley / J.P. Morgan style): cover page with rating & target-price
box, Executive Summary, numbered sections, compact financial tables,
Exhibit-numbered charts, analyst block, conflict-of-interest line, risk &
disclosure pages, and a "Page X of Y" footer.

  Usage:
    python md_to_docx.py report.md                    # report.docx next to it
    python md_to_docx.py report.md -o out/report.docx
    python md_to_docx.py report.md --pdf              # also export PDF (Word)
    python md_to_docx.py report.md --toc              # insert a TOC field
    python md_to_docx.py report.md --no-numbering     # sections unnumbered

  Dependencies (pip):
    python-docx            (required)
    markdown               (required, for md -> HTML)
    docx2pdf               (optional, only for --pdf; needs Microsoft Word)

  Design notes
  ------------
  * The Markdown file is the MASTER. docx is for editing/submission, PDF for
    distribution. GitHub renders the .md; the docx/PDF are build artifacts.
  * Frontmatter (YAML between the first two `---` lines) drives the cover,
    rating box, analyst block, header/footer and disclosure line.
  * Body conventions (see report_template.md): H1 = numbered major section,
    `![Caption](path)` = Exhibit-numbered chart, a line starting with
    "Source:" after a table/chart = small gray source note, a line directly
    above a table matching "Exhibit N:" / "Table N:" / "Chart N:" = caption.
  * English-first, Chinese-capable: body font Calibri with 等线 (DengXian)
    registered as the East-Asian face.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import markdown as md_lib
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ----------------------------------------------------------------------------
# Palette (Wall Street: navy + gray, restrained accent)
# ----------------------------------------------------------------------------
NAVY      = RGBColor(0x0B, 0x25, 0x45)   # headings, company name
ACCENT    = RGBColor(0x1F, 0x38, 0x64)   # sub-headings
DARKGRAY  = RGBColor(0x33, 0x33, 0x33)
MIDGRAY   = RGBColor(0x59, 0x59, 0x59)
LIGHTGRAY = RGBColor(0x8A, 0x8A, 0x8A)
RULEGRAY  = "BFBFBF"
SHADE_HEAD= "1F3864"                     # table header fill (navy)
SHADE_ALT = "F2F4F8"                     # zebra / rating-box fill
SHADE_CODE= "F5F5F5"
EASTASIA  = "等线"                        # DengXian, for Chinese glyphs

RATING_COLORS = {
    "overweight": RGBColor(0x1E, 0x7B, 0x34),
    "buy":        RGBColor(0x1E, 0x7B, 0x34),
    "equal-weight": RGBColor(0xB0, 0x7D, 0x2B),
    "hold":       RGBColor(0xB0, 0x7D, 0x2B),
    "neutral":    RGBColor(0xB0, 0x7D, 0x2B),
    "underweight": RGBColor(0xB0, 0x30, 0x30),
    "sell":       RGBColor(0xB0, 0x30, 0x30),
}

NUMERIC_RE = re.compile(
    r"^[\(\[-]?[$€£¥]?[\d,]+(?:\.[\d]+)?%?[\)\]]?$|"
    r"^(?:n\.?m\.?|NM|—|–|-|n/a)$", re.IGNORECASE)
CAPTION_RE = re.compile(r"^(?:Exhibit|Table|Chart)\s*\d*[:.\-]?\s*(.+)$", re.I)
SOURCE_RE  = re.compile(r"^\s*Source\s*:", re.I)


# ----------------------------------------------------------------------------
# Minimal YAML-frontmatter parser (flat keys, list-of-maps, folded scalars)
# ----------------------------------------------------------------------------
def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (meta, body). meta = {} if no frontmatter block."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    end = None
    for i in range(1, min(len(lines), 400)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta: dict = {}
    fm = lines[1:end]
    body = "".join(lines[end + 1:])
    i = 0
    list_key: str | None = None
    cur_item: dict | None = None
    while i < len(fm):
        line = fm[i].rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if list_key is not None and stripped.startswith("- "):
            # new list item: `- key: value, key2: value2`
            cur_item = {}
            for pair in _split_pairs(stripped[2:]):
                k, v = pair
                cur_item[k] = _unquote(v)
            meta[list_key].append(cur_item)
            i += 1
            continue
        if list_key is not None and cur_item is not None and line[:1] in (" ", "\t"):
            # continuation line of the current list item (e.g. `title: ...`)
            m2 = re.match(r"^(\s*)([A-Za-z0-9_][\w]*)\s*:\s*(.*)$", line)
            if m2:
                cur_item[m2.group(2)] = _unquote(m2.group(3))
                i += 1
                continue
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_][\w]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1).strip(), m.group(2).strip()
        if val == "":
            # valueless key: treat as an empty list (list items follow indented)
            meta[key] = []
            list_key = key
            i += 1
            continue
        if val.startswith(">-") or val.startswith("|-"):
            # folded / literal block: consume following indented lines
            chunks = []
            j = i + 1
            while j < len(fm) and (fm[j].startswith("  ") or fm[j].startswith("\t")):
                chunks.append(fm[j].strip())
                j += 1
            sep = " " if val.startswith(">-") else "\n"
            meta[key] = sep.join(chunks)
            list_key = None
            i = j
            continue
        if val == "[":
            meta[key] = []
            list_key = key
            i += 1
            continue
        meta[key] = _unquote(val)
        list_key = None
        i += 1
    return meta, body


def _split_pairs(s: str) -> list[tuple[str, str]]:
    """Split 'a: 1, b: 2' style inline pairs (used for list items)."""
    out = []
    for part in re.split(r",\s*(?=[A-Za-z_][\w]*\s*:)", s):
        if ":" in part:
            k, v = part.split(":", 1)
            out.append((k.strip(), v.strip()))
    return out


def _unquote(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


# ----------------------------------------------------------------------------
# docx low-level helpers
# ----------------------------------------------------------------------------
def _set_font(run, name="Calibri", size=10, bold=False, italic=False,
              color=None, caps=False):
    f = run.font
    f.name = name
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    if color is not None:
        f.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), EASTASIA)
    if caps:
        c = OxmlElement("w:caps")
        c.set(qn("w:val"), "1")
        rPr.append(c)


def _set_char_spacing(run, twips: int):
    rPr = run._r.get_or_add_rPr()
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:val"), str(twips))
    rPr.append(sp)


def _para_border(p, edge="bottom", color=RULEGRAY, sz=4, space=2):
    pPr = p._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    el = OxmlElement(f"w:{edge}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color)
    pBdr.append(el)


def _shade_cell(cell, hexfill: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexfill)
    tcPr.append(shd)


def _cell_border(cell, edges=("top", "bottom", "left", "right"), color="1F3864", sz=6):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for e in edges:
        el = OxmlElement(f"w:{e}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)


def _cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for name, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        el = OxmlElement(f"w:{name}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcPr.append(mar)


def _add_field(paragraph, code: str):
    run = paragraph.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = f" {code} "
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
    return run


def _page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    return p


# ----------------------------------------------------------------------------
# Inline content: list of (text, fmt-dict)
# ----------------------------------------------------------------------------
class MDWalker(HTMLParser):
    """Convert markdown-lib HTML output into a list of block dicts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict] = []
        self.stack: list[str] = []
        self.inlines: list = []          # current inline accumulator
        self.in_list = False
        self.list_type = None
        self.list_items: list[list] = []
        # table state
        self.in_table = False
        self.table_rows: list[tuple[bool, list[list], list]] = []
        self.table_aligns: list[str] = []
        self.cur_row = None
        self.cur_cell = None
        self.cur_cell_align = None
        self.in_thead = False
        # image handling
        self.cur_img = None

    # -- helpers ------------------------------------------------------------
    def _fmt(self) -> dict:
        s = self.stack
        f = {"bold": ("strong" in s) or ("b" in s),
             "italic": ("em" in s) or ("i" in s),
             "code": "code" in s}
        if "a" in s:
            f["link"] = True
        return f

    def _emit_para(self, kind="para", **kw):
        if self.inlines or kind in ("img",):
            self.blocks.append({"type": kind, "inlines": self.inlines, **kw})
        self.inlines = []

    # -- events -------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4", "h5"):
            self._emit_para()
            self.stack.append(tag)
            self.inlines = []
        elif tag == "p":
            if self.in_list and "li" in self.stack:
                # <p> inside a list item: keep accumulating into the item
                self.stack.append("p")
                return
            self._emit_para()
            self.stack.append("p")
            self.inlines = []
        elif tag == "blockquote":
            self._emit_para()
            self.stack.append("blockquote")
            self.inlines = []
        elif tag == "pre":
            self._emit_para()
            self.stack.append("pre")
            self.inlines = []
        elif tag == "ul" or tag == "ol":
            self._emit_para()
            self.in_list = True
            self.list_type = tag
            self.list_items = []
            self.stack.append(tag)
        elif tag == "li":
            self._emit_para()
            self.stack.append("li")
            self.inlines = []
        elif tag == "table":
            self._emit_para()
            self.in_table = True
            self.table_rows = []
            self.table_aligns = []
            self.in_thead = False
            self.stack.append("table")
        elif tag == "thead":
            self.in_thead = True
        elif tag == "tbody":
            self.in_thead = False
        elif tag == "tr":
            if self.in_table:
                self.cur_row = []
        elif tag in ("td", "th"):
            if self.in_table and self.cur_row is not None:
                self.cur_cell = []
                self.cur_cell_align = a.get("align")
                self.stack.append(tag)
                if tag == "th" and a.get("align"):
                    self.table_aligns.append(a["align"])
        elif tag == "img":
            src = a.get("src", "")
            alt = a.get("alt", "")
            # images arrive inside <p>; close current para content first
            self._emit_para(kind="img", src=src, alt=alt)
        elif tag == "hr":
            self._emit_para(kind="hr")
        elif tag == "br":
            self.inlines.append(("\n", self._fmt()))
        elif tag == "div":
            cls = a.get("class", "")
            if "pagebreak" in cls:
                self.blocks.append({"type": "pagebreak"})
        else:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5"):
            lvl = int(tag[1])
            self._emit_para(kind="heading", level=lvl)
            if tag in self.stack:
                self.stack.remove(tag)
        elif tag == "p":
            if self.in_list and "li" in self.stack:
                if "p" in self.stack:
                    self.stack.remove("p")
                return
            self._emit_para()
            if "p" in self.stack:
                self.stack.remove("p")
        elif tag == "blockquote":
            self._emit_para(kind="quote")
            if "blockquote" in self.stack:
                self.stack.remove("blockquote")
        elif tag == "pre":
            self._emit_para(kind="codeblock")
            if "pre" in self.stack:
                self.stack.remove("pre")
        elif tag == "li":
            if self.inlines:
                self.list_items.append(self.inlines)
            self.inlines = []
            if "li" in self.stack:
                self.stack.remove("li")
        elif tag == "ul" or tag == "ol":
            self._emit_para()
            if self.list_items:
                self.blocks.append({"type": "list", "list_type": self.list_type,
                                    "items": self.list_items})
            self.in_list = False
            self.list_type = None
            self.list_items = []
            if tag in self.stack:
                self.stack.remove(tag)
        elif tag == "td" or tag == "th":
            if self.in_table and self.cur_cell is not None:
                self.cur_row.append((tag == "th", self.cur_cell, self.cur_cell_align))
                self.cur_cell = None
                self.cur_cell_align = None
            if tag in self.stack:
                self.stack.remove(tag)
        elif tag == "tr":
            if self.in_table and self.cur_row is not None:
                is_head = self.in_thead or all(c[0] for c in self.cur_row if c)
                self.table_rows.append((is_head,
                                        [c[1] for c in self.cur_row],
                                        [c[2] for c in self.cur_row]))
                self.cur_row = None
        elif tag == "table":
            self.in_table = False
            self.blocks.append({"type": "table", "rows": self.table_rows,
                                "aligns": self.table_aligns})
            if "table" in self.stack:
                self.stack.remove("table")
        elif tag == "thead":
            self.in_thead = False
        elif tag == "a":
            if "a" in self.stack:
                self.stack.remove("a")
        elif tag in self.stack:
            self.stack.remove(tag)

    def handle_data(self, data):
        if not data:
            return
        if self.in_table and self.cur_cell is not None:
            self.cur_cell.append((data, self._fmt()))
        elif self.in_list and "li" in self.stack:
            self.inlines.append((data, self._fmt()))
        elif self.stack:
            self.inlines.append((data, self._fmt()))


# ----------------------------------------------------------------------------
# Renderer
# ----------------------------------------------------------------------------
class DocxRenderer:
    def __init__(self, meta: dict, md_path: Path, opts):
        self.meta = meta
        self.md_dir = md_path.parent
        self.opts = opts
        self.exhibit_no = 0
        self.h1_no = 0
        self.doc = Document()
        self._setup_page()
        self._setup_styles()

    # -- document scaffolding ----------------------------------------------
    def _setup_page(self):
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        sec.left_margin = sec.right_margin = Inches(0.95)
        sec.top_margin, sec.bottom_margin = Inches(0.85), Inches(0.85)

    def _setup_styles(self):
        st = self.doc.styles
        normal = st["Normal"]
        normal.font.name = "Calibri"
        normal.font.size = Pt(10)
        rpr = normal.element.get_or_add_rPr()
        rf = OxmlElement("w:rFonts")
        rf.set(qn("w:ascii"), "Calibri"); rf.set(qn("w:hAnsi"), "Calibri")
        rf.set(qn("w:eastAsia"), EASTASIA)
        rpr.append(rf)
        pf = normal.paragraph_format
        pf.space_after = Pt(6)
        pf.line_spacing = 1.08

        for name, size, bold, color, before, after in (
                ("Heading 1", 14, True, NAVY, 16, 8),
                ("Heading 2", 12, True, ACCENT, 10, 4),
                ("Heading 3", 11, True, DARKGRAY, 8, 3),
                ("Heading 4", 10.5, True, MIDGRAY, 6, 2)):
            h = st[name]
            h.font.name = "Calibri"; h.font.size = Pt(size); h.font.bold = bold
            h.font.color.rgb = color
            h.paragraph_format.space_before = Pt(before)
            h.paragraph_format.space_after = Pt(after)
            h.paragraph_format.keep_with_next = True
            rpr = h.element.get_or_add_rPr()
            rf = OxmlElement("w:rFonts")
            rf.set(qn("w:ascii"), "Calibri"); rf.set(qn("w:hAnsi"), "Calibri")
            rf.set(qn("w:eastAsia"), EASTASIA)
            rpr.append(rf)

    # -- cover --------------------------------------------------------------
    def render_cover(self):
        m = self.meta
        firm = m.get("firm", "Independent Equity Research")
        rtype = m.get("report_type", "EQUITY RESEARCH").upper()
        date = m.get("date", "")

        # top line: firm | date
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(firm.upper())
        _set_font(r, size=9, bold=True, color=ACCENT, caps=True)
        _set_char_spacing(r, 14)
        if date:
            r2 = p.add_run(f"\t{date}")
            _set_font(r2, size=9, color=MIDGRAY)
        _para_border(p, "bottom", RULEGRAY, sz=6)

        # logo
        if m.get("logo"):
            logo = self.md_dir / m["logo"]
            if logo.exists():
                self.doc.add_picture(str(logo), width=Inches(1.6))
                self.doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.LEFT

        # report-type banner
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run("EQUITY RESEARCH")
        _set_font(r, size=8, color=MIDGRAY, caps=True)
        _set_char_spacing(r, 18)
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(rtype)
        _set_font(r, size=15, bold=True, color=ACCENT, caps=True)
        _set_char_spacing(r, 16)
        _para_border(p, "bottom", "1F3864", sz=10)

        # company
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(m.get("company", ""))
        _set_font(r, size=25, bold=True, color=NAVY)
        ident = m.get("ticker", "")
        if m.get("exchange"):
            ident += f" · {m['exchange']}"
        if m.get("sector"):
            ident += f" · {m['sector']}"
        p2 = self.doc.add_paragraph()
        p2.paragraph_format.space_after = Pt(6)
        r = p2.add_run(ident)
        _set_font(r, size=10.5, color=MIDGRAY)

        # title
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(14)
        r = p.add_run(m.get("title", ""))
        _set_font(r, size=13.5, bold=True, color=DARKGRAY, italic=True)

        self._render_rating_box()
        self._render_key_data_line()
        if m.get("price_chart"):
            pc = self.md_dir / m["price_chart"]
            if pc.exists():
                self.exhibit_no += 1
                self._render_figure(pc, m.get("alt_price_chart",
                                              "12-month price performance"))

        self._render_analysts()
        self._render_conflict_line()
        # footer line of cover
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        r = p.add_run(f"© {m.get('copyright_year', '')} {firm} · "
                      "See important disclosures on the final pages of this report.")
        _set_font(r, size=7.5, color=LIGHTGRAY)

    def _render_rating_box(self):
        m = self.meta
        labels = ["Rating", "Target Price", "Current Price", "Upside/(Downside)"]
        values = [m.get("rating", "—"),
                  m.get("target_price_prev") and
                  f"{m['currency']} {m.get('target_price_prev')} → {m.get('currency')} {m.get('target_price')}"
                  or f"{m.get('currency', '$')} {m.get('target_price', '—')}",
                  f"{m.get('currency', '$')} {m.get('current_price', '—')}",
                  m.get("upside", "—")]
        rating_color = NAVY
        for k, c in RATING_COLORS.items():
            if k in m.get("rating", "").lower():
                rating_color = c
                break
        table = self.doc.add_table(rows=2, cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        width = Inches(6.6 / 4)
        for j, (lab, val) in enumerate(zip(labels, values)):
            for i in (0, 1):
                cell = table.cell(i, j)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                _cell_margins(cell)
                if i == 0:
                    _shade_cell(cell, SHADE_HEAD)
                    _cell_border(cell)
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    r = p.add_run(lab.upper())
                    _set_font(r, size=8, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), caps=True)
                    _set_char_spacing(r, 8)
                else:
                    _shade_cell(cell, SHADE_ALT)
                    _cell_border(cell)
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    r = p.add_run(val)
                    _set_font(r, size=12, bold=True,
                              color=rating_color if j == 0 else NAVY)
        if m.get("rating_note"):
            p = self.doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(m["rating_note"])
            _set_font(r, size=8, italic=True, color=MIDGRAY)

    def _render_key_data_line(self):
        m = self.meta
        bits = []
        if m.get("market_cap"):
            bits.append(f"Market Cap  {m['market_cap']}")
        if m.get("shares_out"):
            bits.append(f"Shares Out  {m['shares_out']}")
        if m.get("avg_daily_volume"):
            bits.append(f"Avg Daily Vol  {m['avg_daily_volume']}")
        if m.get("52wk_range"):
            bits.append(f"52-Week Range  {m['52wk_range']}")
        if m.get("pe_ntm"):
            bits.append(f"NTM P/E  {m['pe_ntm']}")
        if m.get("horizon"):
            bits.append(f"Horizon  {m['horizon']}")
        if not bits:
            return
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(12)
        for i, b in enumerate(bits):
            if i:
                p.add_run("   ·   ")
            r = p.add_run(b)
            _set_font(r, size=8.5, color=MIDGRAY)

    def _render_analysts(self):
        m = self.meta
        analysts = m.get("analysts") or []
        if not analysts:
            return
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run("ANALYSTS")
        _set_font(r, size=8, bold=True, color=ACCENT, caps=True)
        _set_char_spacing(r, 12)
        for a in analysts:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(a.get("name", ""))
            _set_font(r, size=10.5, bold=True, color=NAVY)
            extra = " · ".join(x for x in (a.get("title"), a.get("phone"),
                                           a.get("email")) if x)
            if extra:
                r2 = p.add_run(f"   {extra}")
                _set_font(r2, size=8.5, color=MIDGRAY)

    def _render_conflict_line(self):
        m = self.meta
        text = m.get("disclosure_conflict", "")
        if not text:
            return
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        _set_font(r, size=8, italic=True, color=MIDGRAY)

    # -- body ---------------------------------------------------------------
    def render_body(self, blocks):
        # post-process: caption / source classification
        for i, b in enumerate(blocks):
            if b["type"] == "para":
                txt = "".join(t for t, _ in b["inlines"]).strip()
                if SOURCE_RE.match(txt):
                    b["type"] = "source"
                elif (i + 1 < len(blocks) and blocks[i + 1]["type"] == "table"
                      and CAPTION_RE.match(txt)):
                    b["type"] = "caption"
        for b in blocks:
            t = b["type"]
            if t == "pagebreak":
                _page_break(self.doc)
            elif t == "heading":
                self._render_heading(b["level"], b["inlines"])
            elif t == "para":
                self._render_para(b["inlines"], indent=0)
            elif t == "quote":
                self._render_quote(b["inlines"])
            elif t == "source":
                self._render_para(b["inlines"], size=7.5, italic=True,
                                  color=MIDGRAY, space_after=8)
            elif t == "caption":
                self._render_para(b["inlines"], size=8.5, bold=True,
                                  color=MIDGRAY, space_after=2,
                                  keep_with_next=True)
            elif t == "list":
                self._render_list(b["list_type"], b["items"])
            elif t == "table":
                self._render_table(b["rows"], b["aligns"])
            elif t == "img":
                self._render_img(b["src"], b["alt"])
            elif t == "codeblock":
                self._render_codeblock(b["inlines"])
            elif t == "hr":
                p = self.doc.add_paragraph()
                _para_border(p, "bottom", RULEGRAY, sz=4)

    def _render_heading(self, level, inlines):
        text = self._sub("".join(t for t, _ in inlines))
        if level == 1 and not self.opts.no_numbering:
            self.h1_no += 1
            text = f"{self.h1_no}.  {text}"
        p = self.doc.add_paragraph(style=f"Heading {min(level, 4)}")
        r = p.add_run(text)
        if level == 1:
            _set_font(r, size=14, bold=True, color=NAVY)
            _para_border(p, "bottom", RULEGRAY, sz=4)
        elif level == 2:
            _set_font(r, size=12, bold=True, color=ACCENT)
        elif level == 3:
            _set_font(r, size=11, bold=True, color=DARKGRAY)
        else:
            _set_font(r, size=10.5, bold=True, color=MIDGRAY, italic=True)

    def _render_para(self, inlines, size=10, bold=False, italic=False,
                     color=None, indent=0, space_after=6, keep_with_next=False):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(space_after)
        if indent:
            pf.left_indent = Inches(indent)
        if keep_with_next:
            pf.keep_with_next = True
        self._write_inlines(p, inlines, size=size, base_bold=bold,
                            base_italic=italic, base_color=color)
        return p

    def _write_inlines(self, p, inlines, size=10, base_bold=False,
                       base_italic=False, base_color=None):
        for text, f in inlines:
            text = self._sub(text)
            if "\n" in text:
                parts = text.split("\n")
                for k, part in enumerate(parts):
                    if k:
                        p.add_run().add_break()
                    if part:
                        self._add_run(p, part, size=size, bold=base_bold or f.get("bold"),
                                      italic=base_italic or f.get("italic"),
                                      color=base_color, code=f.get("code"),
                                      link=f.get("link"))
            else:
                self._add_run(p, text, size=size, bold=base_bold or f.get("bold"),
                              italic=base_italic or f.get("italic"),
                              color=base_color, code=f.get("code"), link=f.get("link"))

    def _add_run(self, p, text, size=10, bold=False, italic=False, color=None,
                 code=False, link=False):
        r = p.add_run(text)
        if code:
            _set_font(r, name="Consolas", size=max(size - 1, 7), color=RGBColor(0x8B, 0x1A, 0x1A))
        elif link:
            _set_font(r, size=size, color=RGBColor(0x05, 0x63, 0xC1))
            r.font.underline = True
        else:
            _set_font(r, size=size, bold=bold, italic=italic, color=color)
        return r

    def _render_quote(self, inlines):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Inches(0.3)
        pf.space_after = Pt(6)
        _para_border(p, "left", "1F3864", sz=12, space=6)
        self._write_inlines(p, inlines, size=9.5, base_italic=True, base_color=MIDGRAY)

    def _render_list(self, list_type, items):
        style = "List Number" if list_type == "ol" else "List Bullet"
        for item in items:
            p = self.doc.add_paragraph(style=style)
            p.paragraph_format.space_after = Pt(3)
            self._write_inlines(p, item, size=10)

    def _sub(self, text: str) -> str:
        """Replace {{FIELD}} tokens with frontmatter values (case-insensitive)."""
        if "{{" not in text:
            return text

        def rep(m):
            key = m.group(1).strip().lower()
            for k, v in self.meta.items():
                if k.lower() == key:
                    if isinstance(v, list):
                        return str(v[0].get("name", "")) if v else ""
                    return str(v)
            return m.group(0)

        return re.sub(r"\{\{\s*([^{}]+?)\s*\}\}", rep, text)

    def _is_numeric_col(self, rows, j):
        vals = []
        for is_head, cells, _ in rows:
            if is_head or j >= len(cells):
                continue
            txt = "".join(t for t, _ in cells[j]).strip()
            vals.append(txt)
        if not vals:
            return False
        hits = sum(1 for v in vals if NUMERIC_RE.match(v))
        return hits / len(vals) >= 0.6

    def _render_table(self, rows, aligns):
        if not rows:
            return
        ncols = max(len(cells) for _, cells, _ in rows)
        table = self.doc.add_table(rows=len(rows), cols=ncols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        col_w = Inches(6.6 / ncols)
        numeric_cols = [self._is_numeric_col(rows, j) for j in range(ncols)]
        for i, (is_head, cells, cell_aligns) in enumerate(rows):
            for j in range(ncols):
                cell = table.cell(i, j)
                cell.width = col_w
                _cell_margins(cell, top=30, bottom=30, left=70, right=70)
                if is_head:
                    _shade_cell(cell, SHADE_HEAD)
                elif i % 2 == 0:
                    _shade_cell(cell, SHADE_ALT)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                if numeric_cols[j]:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                elif j < len(cell_aligns) and cell_aligns[j] == "center":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif j < len(cell_aligns) and cell_aligns[j] == "right":
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                inlines = cells[j] if j < len(cells) else []
                self._write_inlines(p, inlines, size=8.5,
                                    base_bold=is_head,
                                    base_color=RGBColor(0xFF, 0xFF, 0xFF) if is_head else None)
        # light grid
        tblPr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{e}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "C9CFD8")
            borders.append(el)
        tblPr.append(borders)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)

    def _render_img(self, src, alt):
        img_path = self.md_dir / src if src else None
        if not img_path or not img_path.exists():
            p = self.doc.add_paragraph()
            r = p.add_run(f"[missing image: {src}]")
            _set_font(r, size=9, italic=True, color=LIGHTGRAY)
            return
        self.exhibit_no += 1
        self._render_figure(img_path, alt)

    def _render_figure(self, img_path, alt):
        # caption above (WS convention: "Exhibit N: <title>")
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        cap = alt or "Price performance"
        r = p.add_run(f"Exhibit {self.exhibit_no}:  {cap}")
        _set_font(r, size=8.5, bold=True, color=MIDGRAY)
        pic_p = self.doc.add_paragraph()
        pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic_p.paragraph_format.space_after = Pt(2)
        run = pic_p.add_run()
        run.add_picture(str(img_path), width=Inches(5.8))

    def _render_codeblock(self, inlines):
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.15)
        p.paragraph_format.right_indent = Inches(0.15)
        p.paragraph_format.space_after = Pt(6)
        # shading
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), SHADE_CODE)
        pPr.append(shd)
        self._write_inlines(p, inlines, size=8, base_color=None)

    # -- header / footer (body section) -------------------------------------
    def add_body_section(self):
        m = self.meta
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        sec.left_margin = sec.right_margin = Inches(0.95)
        sec.top_margin, sec.bottom_margin = Inches(0.85), Inches(0.85)
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False

        # header: title left, date right, thin rule
        hp = sec.header.paragraphs[0]
        hp.paragraph_format.tab_stops.add_tab_stop(Inches(6.6), WD_ALIGN_PARAGRAPH.RIGHT)
        r = hp.add_run(m.get("header_title") or f"{m.get('company', '')} ({m.get('ticker', '')})")
        _set_font(r, size=8, bold=True, color=MIDGRAY, caps=True)
        r = hp.add_run(f"\t{m.get('date', '')}")
        _set_font(r, size=8, color=LIGHTGRAY)
        _para_border(hp, "bottom", RULEGRAY, sz=4)

        # footer: org left, "Page X of Y" right
        fp = sec.footer.paragraphs[0]
        fp.paragraph_format.tab_stops.add_tab_stop(Inches(6.6), WD_ALIGN_PARAGRAPH.RIGHT)
        r = fp.add_run(m.get("footer_org", ""))
        _set_font(r, size=7.5, color=LIGHTGRAY)
        r = fp.add_run("\tPage ")
        _set_font(r, size=7.5, color=LIGHTGRAY)
        _add_field(fp, "PAGE")
        r = fp.add_run(" of ")
        _set_font(r, size=7.5, color=LIGHTGRAY)
        _add_field(fp, "NUMPAGES")
        return sec

    def add_toc(self):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        r = p.add_run("Table of Contents")
        _set_font(r, size=13, bold=True, color=NAVY)
        p2 = self.doc.add_paragraph()
        run = p2.add_run()
        fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
        instr.text = ' TOC \\o "1-2" \\h \\z \\u '
        fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "separate")
        t = OxmlElement("w:t"); t.text = "Right-click and choose 'Update Field' to build the table of contents."
        fld3 = OxmlElement("w:fldChar"); fld3.set(qn("w:fldCharType"), "end")
        run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
        run._r.append(t); run._r.append(fld3)
        _page_break(self.doc)


# ----------------------------------------------------------------------------
def convert(md_path: Path, out_path: Path, opts) -> Path:
    text = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    html = md_lib.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])
    walker = MDWalker()
    walker.feed(html)
    walker.close()

    r = DocxRenderer(meta, md_path, opts)
    r.render_cover()
    r.add_body_section()
    if opts.toc:
        r.add_toc()
    r.render_body(walker.blocks)
    r.doc.save(str(out_path))
    return out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Wall Street-style Markdown → docx")
    ap.add_argument("input", help="input .md report (templates/report_template.md)")
    ap.add_argument("-o", "--output", help="output .docx path")
    ap.add_argument("--pdf", action="store_true", help="also convert to PDF via docx2pdf (needs MS Word)")
    ap.add_argument("--toc", action="store_true", help="insert a Table of Contents field")
    ap.add_argument("--no-numbering", action="store_true", help="do not number H1 sections")
    opts = ap.parse_args(argv)

    src = Path(opts.input)
    if not src.exists():
        sys.exit(f"error: input not found: {src}")
    out = Path(opts.output) if opts.output else src.with_suffix(".docx")
    out.parent.mkdir(parents=True, exist_ok=True)

    convert(src, out, opts)
    print(f"[ok] docx written: {out} ({out.stat().st_size:,} bytes)")

    if opts.pdf:
        pdf = out.with_suffix(".pdf")
        try:
            from docx2pdf import convert as d2p
            d2p(str(out), str(pdf))
            print(f"[ok] pdf written: {pdf} ({pdf.stat().st_size:,} bytes)")
        except Exception as e:  # noqa: BLE001
            print(f"[warn] PDF export failed: {e}\n"
                  "  Alternatives: (1) open the .docx in Microsoft Word and Save As PDF, "
                  "(2) install pandoc + a LaTeX engine, or (3) install typst.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
