#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_check.py — Machine quality gate (J1) for the Wall Street Research pipeline.

Usage:
    python scripts/check/build_check.py <report.md> [--numbers <numbers.json>]
                                        [--data-dir <dir>] [--verbose] [--json]

What it verifies (each check family prints PASS/FAIL; any FAIL → exit code 1):

  J1-a  Placeholders: the report body must contain NO '{{...}}' tokens
        (the report_template.md file itself is exempt; every field must be
        resolved into the final report before it can be published).
  J1-b  Exhibits: every figure shown by `![alt](path)` is auto-numbered
        "Exhibit N" in reading order; the files must EXIST, and every
        "Exhibit N" mention in the text must reference 1..K (continuous).
  J1-c  Number reference table: numbers declared in `numbers.json` (the
        digital 数字引用表) are validated against the data JSON files and
        the report text:
          - data_match       (value from data/JSON vs a number in the text)
          - derived_match    (computed from data/JSON vs text, tolerance)
          - raw              (literal expected value vs a number in text)
        Tolerance-based: rounding is fine, invented figures are not.
  J1-d  Frontmatter: required fields present, analysts list non-empty, and
        self-consistent: upside ≈ target_price/current_price − 1 (1% rel tol).
  J1-e  Tables: structural completeness (consistent column counts, non-empty
        headers) plus configured key rows from numbers.json "tables".
  J1-f  Registry: numbers.json must exist to enable families (c)/(e).

numbers.json (数字引用表) — convention: same folder as the report, or --numbers.
Checks are a list; `path` values may address a JSON file with a dotted key:

  {"id": "current_price", "kind": "data_match",
   "file": "nvda_quote.json", "path": "quote.regularMarketPrice",
   "decimals": 2, "tolerance": 0.005, "display_fmt": "$224.22"}

  {"id": "mkt_cap", "kind": "data_match", "file": "nvda_quote.json",
   "path": "quote.marketCap", "scale": 1e12, "decimals": 2, "suffix": "T"}

  {"id": "gross_margin", "kind": "data_match", "file": "nvda_financials.json",
   "path": "modules.financialData.grossMargins", "percent": true, "decimals": 1}

  {"id": "upside_rec", "kind": "derived_match",
   "num": ["@frontmatter", "target_price"], "den": ["@frontmatter", "current_price"],
   "op": "ratio_minus_1", "unit": "percent", "tol_pp": 1.0,
   "regex": r"implies\s+[+\-]?(\d+(?:\.\d+)?)\s*%", "label": "Rec section upside"}

  {"id": "peer_median", "kind": "data_match", "file": "peers.json",
   "paths": ["AMD.forwardPE", "AVGO.forwardPE", "TSM.forwardPE",
             "INTC.forwardPE", "MSFT.forwardPE"], "agg": "median",
   "decimals": 1, "suffix": "x"}

  {"id": "bear_move", "kind": "derived_match",
   "num": ["nvda_financials.json", "modules.financialData.targetLowPrice"],
   "den": ["@frontmatter", "current_price"], "op": "ratio_minus_1",
   "unit": "percent", "tol_pp": 1.0, "expected": -19.7,
   "regex": r"\$180,\s*[−\-]\s*\d+%", "label": "bear −20% move"}

  {"id": "ev_target", "kind": "raw", "value": 346.94, "display": "347",
   "tolerance": 0.05, "label": "probability-weighted target"}

  "tables": {"required_rows": [
     {"table_contains": "Fiscal year", "label_col": 0,
      "rows": ["FY2023", "FY2024", "FY2025", "FY2026"]},
     ...]}

Paths inside numbers.json are relative to the report directory.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 1

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _deep_get(obj, dotted: str):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if cur is None:
            return None
    return cur


def _round_half_up(value: float, decimals: int) -> float:
    """Decimal-based half-up rounding (float round() is banker's and also
    affected by binary representation errors, e.g. 491.965 → 491.96)."""
    q = Decimal("1").scaleb(-decimals)
    return float(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))


def _number_candidates(text: str) -> list[tuple[float, str]]:
    out = []
    for m in re.finditer(r"(?<![\w.])(-?[\d][\d,]*\.?\d*)\s*(x|%|B|T|M)?",
                         text, re.I):
        raw = m.group(1)
        try:
            val = float(raw.replace(",", ""))
        except ValueError:
            continue
        if not math.isfinite(val):
            continue
        out.append((val, raw))
    return out


def _find_number_in_text(text: str, value: float, rtol: float) -> tuple[bool, str]:
    for val, raw in _number_candidates(text):
        if abs(val - value) <= rtol * max(abs(value), 1e-9):
            return True, raw
    return False, ""


def _find_md_tables(body: str) -> list[list[list[str]]]:
    tables = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [re.sub(r"[*_`]", "", c.strip())
                         for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c or "---") for c in cells):
                    tbl.append(cells)
                i += 1
            if tbl:
                tables.append(tbl)
            continue
        i += 1
    return tables


# ---------------------------------------------------------------------------
# checker
# ---------------------------------------------------------------------------

class Checker:
    def __init__(self, md_path: Path, numbers: dict | None, data_dir: Path | None,
                 verbose: bool = False):
        self.md_path = md_path
        self.md_dir = md_path.parent
        self.text = md_path.read_text(encoding="utf-8")
        self.fm_text = ""
        self.body = self.text
        self.frontmatter: dict = {}
        self._split_frontmatter()
        # normalize unicode minus / en-dash so numeric tokens parse uniformly
        self.body = self.body.replace("\u2212", "-").replace("\u2013", "-")
        self.numbers = numbers or {}
        self.data_dir = data_dir or self.md_dir
        self.verbose = verbose
        self.results: list[tuple[str, str, bool, str]] = []

    # -- frontmatter (minimal YAML: flat keys, "- key: value" list items) ----
    def _split_frontmatter(self):
        t = self.text
        if not t.startswith("---"):
            return
        lines = t.splitlines(keepends=True)
        end = None
        for i in range(1, min(len(lines), 400)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            return
        fm = [l.rstrip("\n") for l in lines[1:end]]
        self.fm_text = "\n".join(fm)
        self.body = "\n".join(l.rstrip("\n") for l in lines[end + 1:])
        meta: dict = {}
        cur_list = None
        for line in fm:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if cur_list is not None and s.startswith("- "):
                item = {}
                for pair in re.split(r",\s*(?=[A-Za-z_][\w]*\s*:)", s[2:]):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        item[k.strip()] = v.strip().strip("\"'")
                meta[cur_list].append(item)
                continue
            m = re.match(r"^([A-Za-z0-9_][\w]*)\s*:\s*(.*)$", s)
            if not m:
                continue
            k, v = m.group(1), m.group(2).strip()
            if v in ("", "["):
                meta[k] = []
                cur_list = k
                continue
            if v.startswith(">-") or v.startswith("|-"):
                meta[k] = v
                cur_list = None
                continue
            meta[k] = v.strip("\"'")
            cur_list = None
        self.frontmatter = meta

    # -- results --------------------------------------------------------------
    def add(self, family: str, name: str, ok: bool, detail: str = ""):
        self.results.append((family, name, ok, detail))
        if not ok or self.verbose:
            tag = "PASS" if ok else "FAIL"
            print(f"  [{tag}] {family} · {name}"
                  + (f" — {detail}" if detail else ""))

    # -- J1-a ------------------------------------------------------------------
    def check_placeholders(self):
        ph = re.findall(r"\{\{\s*[^{}]+?\s*\}\}", self.body)
        if ph:
            uniq = sorted({p.strip() for p in ph})
            self.add("J1-a/placeholders", "no {{...}} in report body", False,
                     f"unresolved fields: {', '.join(uniq)} ({len(ph)} occurrences)")
        else:
            self.add("J1-a/placeholders", "no {{...}} in report body", True)

    # -- J1-b ------------------------------------------------------------------
    def check_exhibits(self):
        imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", self.body)
        missing = [s for s in imgs if not (self.md_dir / s.strip()).exists()]
        k = len(imgs)
        self.add("J1-b/exhibits", f"figures exist ({k} embedded)", not missing,
                 (f"missing images: {', '.join(missing)}" if missing
                  else f"auto-numbered Exhibit 1..{k}"))
        mentions = sorted({int(m) for m in re.findall(r"\bExhibit\s+(\d+)\b", self.body)})
        bad = [n for n in mentions if n < 1 or n > k]
        self.add("J1-b/exhibits", "Exhibit refs in-range & continuous (1..K)",
                 not bad and (not mentions or max(mentions) <= k),
                 f"mentions={mentions}" if not bad else f"out-of-range refs: {bad}")

    # -- J1-c ------------------------------------------------------------------
    def check_numbers(self):
        cfg = self.numbers.get("checks", [])
        if not cfg:
            self.add("J1-c/numbers", "number reference table checks", False,
                     "numbers.json declares no checks (数字引用表 empty)")
            return
        self.add("J1-c/numbers", "number reference table checks", True,
                 f"{len(cfg)} declared")
        for c in cfg:
            cid = c.get("id", "?")
            try:
                kind = c.get("kind", "data_match")
                if kind == "data_match":
                    self._data_match(cid, c)
                elif kind == "derived_match":
                    self._derived_match(cid, c)
                elif kind == "raw":
                    self._raw(cid, c)
                else:
                    self.add("J1-c/numbers", cid, False, f"unknown kind '{kind}'")
            except Exception as e:  # noqa: BLE001
                self.add("J1-c/numbers", cid, False, f"error: {e}")

    def _resolve_path(self, rel: str) -> Path:
        p = Path(rel)
        if not p.is_absolute():
            p = self.data_dir / p
            if not p.exists():
                p2 = self.data_dir / rel
                if not p2.suffix:
                    p = Path(str(p) + ".json")
        return p

    def _read_value(self, src) -> float | None:
        """src = [file | @frontmatter | @literal, dotted_path|value] → float or None."""
        if not isinstance(src, list) or len(src) != 2:
            return None
        if src[0] == "@frontmatter":
            raw = self.frontmatter.get(src[1])
            try:
                return float(str(raw).replace(",", "").replace("%", ""))
            except (TypeError, ValueError):
                return None
        if src[0] == "@literal":
            try:
                return float(str(src[1]).replace(",", "").replace("%", ""))
            except (TypeError, ValueError):
                return None
        obj = _load_json(self._resolve_path(src[0]))
        value = _deep_get(obj, src[1])
        if value is None or isinstance(value, bool):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _format_value(self, value: float, c: dict) -> float:
        if c.get("percent"):
            return value * 100.0
        if c.get("scale"):
            return value / c.get("scale", 1.0)
        return value

    def _data_match(self, cid: str, c: dict):
        paths = c.get("paths") or [c["path"]]
        agg = c.get("agg", "first")
        values = []
        for key, path in [(c["file"], p) for p in paths]:
            obj = _load_json(self._resolve_path(c["file"])) if key != "@frontmatter" else None
            v = None
            if key == "@frontmatter":
                raw = self.frontmatter.get(path)
                try:
                    v = float(str(raw).replace(",", "").replace("%", ""))
                except (TypeError, ValueError):
                    v = None
            else:
                v = _deep_get(obj, path)
                if v is None or isinstance(v, bool):
                    v = None
                else:
                    try:
                        v = float(v)
                    except (TypeError, ValueError):
                        v = None
            if v is not None:
                values.append(v)
        if not values:
            self.add("J1-c/numbers", cid, False, "no numeric value resolved")
            return
        if agg == "median":
            srt = sorted(values)
            value = (srt[len(srt) // 2] if len(srt) % 2
                     else (srt[len(srt) // 2 - 1] + srt[len(srt) // 2]) / 2)
        elif agg == "first":
            value = values[0]
        elif agg == "last":
            value = values[-1]
        else:
            self.add("J1-c/numbers", cid, False, f"unknown agg '{agg}'")
            return
        decimals = c.get("decimals", 2)
        value2 = self._format_value(value, c)
        disp = _round_half_up(value2, decimals)
        disp_s = c.get("display_fmt") or self._fmt(disp, decimals, c)
        rtol = c.get("tolerance", 0.001)
        target_text = self._match_target_text(c)
        found, raw = _find_number_in_text(target_text, disp, rtol)
        if not found and c.get("scope") == "frontmatter":
            found, raw = _find_number_in_text(self.body, disp, rtol)
        # rounding consistency: data value vs displayed value
        within = abs(value2 - disp) <= max(abs(value2) * 0.002, 0.6 * 10 ** -decimals)
        # special: a figure-based match (e.g. "-0.67%") can't use display_fmt check
        if c.get("display"):
            found, raw = _find_number_in_text(target_text, float(c["display"]), rtol)
        self.add("J1-c/numbers", cid, found and within,
                 f"data={round(value, 6)} → {disp_s}"
                 + (f" (text '{raw}')" if found else " (NOT FOUND in report text)"))

    def _fmt(self, value: float, decimals: int, c: dict) -> str:
        suffix = c.get("suffix", "")
        prefix = c.get("prefix", "")
        if decimals == 0:
            return f"{prefix}{value:.0f}{suffix}"
        return f"{prefix}{value:.{decimals}f}{suffix}"

    def _derived_match(self, cid: str, c: dict):
        num = self._read_value(c.get("num"))
        if num is None and c.get("num_expr"):
            num = self._eval_expr(c["num_expr"])
        den = self._read_value(c.get("den"))
        if den is None and c.get("den_expr"):
            den = self._eval_expr(c["den_expr"])
        if num is None or den is None:
            self.add("J1-c/numbers", cid, False, "cannot resolve num/den")
            return
        op = c.get("op", "ratio_minus_1")
        if op == "ratio_minus_1":
            val = num / den - 1.0
        elif op == "one_minus_ratio":
            val = 1.0 - num / den
        elif op == "ratio":
            val = num / den
        else:
            self.add("J1-c/numbers", cid, False, f"unknown op '{op}'")
            return
        if c.get("unit", "ratio") == "percent":
            compare = val * 100.0
        else:
            compare = val
        expected = c.get("expected")
        regex = c.get("regex")
        matched = True
        if regex:
            m = re.search(regex, self.body)
            matched = m is not None
            if expected is None and m:
                try:
                    expected = float(m.group(c.get("match_group", 1)).replace(",", ""))
                except (ValueError, IndexError):
                    expected = None
            if matched and expected is None:
                self.add("J1-c/numbers", cid, False,
                         "regex matched but no expected number — set 'expected' or capture group")
                return
        if expected is None:
            self.add("J1-c/numbers", cid, False,
                     "no expected value and no regex/capture — cannot verify")
            return
        if c.get("unit", "ratio") == "percent":
            tol = c.get("tol_pp", 1.0)
            ok = matched and abs(expected - compare) <= tol
            detail = f"computed={compare:.2f}% vs "
        else:
            tol = c.get("tol", 0.02)
            ok = matched and abs(expected - compare) <= tol * max(abs(compare), 1.0)
            detail = f"computed={compare:.4f} vs "
        self.add("J1-c/numbers", cid, ok, f"{detail}{expected}"
                 + (f" ({c.get('label', '')})" if c.get("label") else ""))

    def _match_target_text(self, c: dict) -> str:
        return self.fm_text if c.get("scope") == "frontmatter" else self.body

    def _eval_expr(self, expr: dict) -> float | None:
        """Nested [num, den, op] chain, e.g. ratio of two data values."""
        op = expr.get("op", "ratio")
        num = self._read_value(expr.get("num"))
        if num is None and expr.get("num_expr"):
            num = self._eval_expr(expr["num_expr"])
        den = self._read_value(expr.get("den"))
        if den is None or num is None:
            return None
        if op == "ratio":
            return num / den
        if op == "ratio_minus_1":
            return num / den - 1.0
        if op == "one_minus_ratio":
            return 1.0 - num / den
        return None

    def _raw(self, cid: str, c: dict):
        value = float(c.get("value"))
        disp = c.get("display")
        tolerance = c.get("tolerance", 0.05)  # relative
        if disp is None:
            decimals = c.get("decimals", 0)
            disp = _round_half_up(value, decimals)
        disp = float(disp)
        target_text = self._match_target_text(c)
        found, raw = _find_number_in_text(target_text, disp, tolerance)
        self.add("J1-c/numbers", cid, found,
                 f"expected {round(disp, 4)} in text"
                 + (f" (found '{raw}')" if found else " (NOT FOUND)"))

    # -- J1-d ------------------------------------------------------------------
    REQUIRED_FM = ["firm", "report_type", "title", "company", "ticker", "exchange",
                   "currency", "date", "rating", "target_price", "current_price",
                   "upside", "horizon", "market_cap", "copyright_year"]

    def check_frontmatter(self):
        if not self.frontmatter:
            self.add("J1-d/frontmatter", "YAML frontmatter present", False)
            return
        missing = [k for k in self.REQUIRED_FM
                   if not str(self.frontmatter.get(k, "")).strip()]
        if missing:
            self.add("J1-d/frontmatter", "required fields present", False,
                     f"missing: {', '.join(missing)}")
        else:
            self.add("J1-d/frontmatter", "required fields present", True,
                     f"{len(self.REQUIRED_FM)} required, all populated")
        analysts = self.frontmatter.get("analysts")
        ok = isinstance(analysts, list) and len(analysts) >= 1 and all(
            isinstance(a, dict) and str(a.get("name", "")).strip() for a in analysts)
        self.add("J1-d/frontmatter", "analysts list ≥ 1 named entry", ok)
        try:
            tp = float(str(self.frontmatter["target_price"]))
            cp = float(str(self.frontmatter["current_price"]))
            up_s = str(self.frontmatter["upside"])
            up = _round_half_up(
                float(re.sub(r"[^0-9.+\-eE]", "", up_s.replace("%", "")) or 0), 4)
            calc = tp / cp - 1.0
            calc_pct = _round_half_up(calc * 100.0, 2)
            ok = abs(up - calc_pct) <= max(1.0, abs(calc_pct) * 0.01)
            self.add("J1-d/frontmatter",
                     "upside ≈ target/current − 1 (1% tolerance)", ok,
                     f"upside={up}% vs calculated={calc_pct}%")
        except (KeyError, ValueError, TypeError) as e:
            self.add("J1-d/frontmatter", "upside ≈ target/current − 1", False,
                     f"parse error: {e}")

    # -- J1-e ------------------------------------------------------------------
    def check_tables(self):
        cfg_tables = self.numbers.get("tables", {})
        tables = _find_md_tables(self.body)
        if not tables:
            self.add("J1-e/tables", "markdown tables present", False)
            return
        bad = []
        for i, tbl in enumerate(tables, 1):
            ncols = len(tbl[0])
            for j, row in enumerate(tbl):
                if len(row) != ncols:
                    bad.append(f"table#{i} row{j} has {len(row)} cells (header {ncols})")
                    break
            if any(not cell.strip() for cell in tbl[0]):
                bad.append(f"table#{i} header has empty cells")
        self.add("J1-e/tables", f"{len(tables)} tables structurally complete",
                 not bad, ("; ".join(bad) if bad
                           else "consistent column counts, non-empty headers"))
        for req in cfg_tables.get("required_rows", []):
            self._required_row(req)
        for req in cfg_tables.get("required_cells", []):
            self._required_cell(req)

    def _required_cell(self, req: dict):
        """Exact-or-computed cell verification:
        {"table_contains": "...", "row": "FY2026",
         "cells": [{"col": 1, "computed": {num..., den..., op..., decimals...}},
                   {"col": 2, "exact": "130.50"}]}
        """
        table = self._find_table_containing(req.get("table_contains", ""))
        if table is None:
            self.add("J1-e/cells", f"cell table '{req.get('table_contains')}'", False)
            return
        row_label = req.get("row", "")
        row = next((r for r in table if str(r[req.get("label_col", 0)]).strip() == row_label), None)
        if row is None:
            self.add("J1-e/cells", f"row '{row_label}" + "'", False,
                     f"not found in '{req.get('table_contains')}'")
            return
        for spec in req.get("cells", []):
            col = spec.get("col")
            if col < 0 or col >= len(row):
                self.add("J1-e/cells", f"row '{row_label}' col {col}", False, "out of range")
                continue
            raw_cell = row[col].strip()
            if "computed" in spec:
                value = self._eval_expr(spec["computed"])
                if value is None:
                    self.add("J1-e/cells", f"row '{row_label}' col {col}", False,
                             "computed value unresolved")
                    continue
                if spec["computed"].get("percent"):
                    compare = value * 100.0
                else:
                    compare = value
                decimals = spec["computed"].get("decimals", 2)
                target = _round_half_up(compare, decimals)
                if raw_cell in ("—", "–", "-", "n/a", "NM", "n.m."):
                    self.add("J1-e/cells", f"row '{row_label}' col {col}", False,
                             f"cell is '{raw_cell}' but computed {target}")
                    continue
                try:
                    cell_val = float(re.sub(r"[^0-9.+\-eE]", "",
                                            raw_cell.replace(",", "")) or "nan")
                except ValueError:
                    self.add("J1-e/cells", f"row '{row_label}' col {col}", False,
                             f"could not parse cell '{raw_cell}'")
                    continue
                if spec["computed"].get("percent"):
                    tol = spec["computed"].get("tol_pp", 1.0)
                    ok = abs(cell_val - target) <= tol
                else:
                    tol = max(0.5 * 10 ** -decimals, abs(target) * spec["computed"].get("tol", 0.005))
                    ok = abs(cell_val - target) <= tol
                self.add("J1-e/cells", f"'{row_label}' {raw_cell} vs computed {target}",
                         ok, f"cell='{raw_cell}' computed={compare:.4f}")
            elif "exact" in spec:
                ok = raw_cell == str(spec["exact"])
                self.add("J1-e/cells", f"'{row_label}' col {col} exact match",
                         ok, f"expected '{spec['exact']}', got '{raw_cell}'")
            elif "cell_required" in spec:
                self.add("J1-e/cells", f"'{row_label}' col {col} non-empty",
                         bool(raw_cell), f"cell='{raw_cell}'")

    def _required_row(self, req: dict):
        contains = req.get("table_contains", "")
        label_col = req.get("label_col", 0)
        rows_required = req.get("rows", [])
        table = self._find_table_containing(contains)
        if table is None:
            self.add("J1-e/keyrows", f"key-row table '{contains}' present", False)
            return
        self.add("J1-e/keyrows", f"key-row table '{contains}' present", True)
        labels = [r[label_col].strip() for r in table]
        missing = [lbl for lbl in rows_required if lbl not in labels]
        self.add("J1-e/keyrows", f"required rows in '{contains}'", not missing,
                 ("rows present: " + ", ".join(labels)
                  if not missing else f"missing rows: {missing}"))

    def _find_table_containing(self, needle: str):
        for tbl in _find_md_tables(self.body):
            joined = " ".join(cell for row in tbl for cell in row)
            if needle and needle in joined:
                return tbl
            if not needle and tbl:
                return tbl
        return None

    # -- verdict --------------------------------------------------------------
    def verdict(self) -> bool:
        print()
        ok = all(ok for _, _, ok, _ in self.results)
        byfam: dict[str, list[bool]] = {}
        for fam, _, ok_, _ in self.results:
            byfam.setdefault(fam, []).append(ok_)
        for fam, results in sorted(byfam.items()):
            print(f"  {fam}: {sum(1 for o in results if o)} PASS / "
                  f"{sum(1 for o in results if not o)} FAIL")
        print()
        if ok:
            print(f"=== ALL CHECKS PASSED ({len(self.results)} checks) — "
                  f"{self.md_path.name} ===")
        else:
            n = sum(1 for _, _, ok_, _ in self.results if not ok_)
            print(f"=== {n} CHECK(S) FAILED — {self.md_path.name} — fix before publish ===")
        return ok


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Wall Street Research build quality gate (J1)")
    ap.add_argument("report", help="report .md to check (final, published form)")
    ap.add_argument("--numbers", help="numbers.json; default <report_dir>/numbers.json")
    ap.add_argument("--data-dir", help="data dir; default <report_dir>/data or <report_dir>")
    ap.add_argument("--verbose", action="store_true", help="print PASS details too")
    ap.add_argument("--json", action="store_true", help="print machine-readable results")
    args = ap.parse_args(argv)

    md = Path(args.report)
    if not md.exists():
        print(f"error: report not found: {md}", file=sys.stderr)
        return EXIT_FAIL
    nb_path = Path(args.numbers) if args.numbers else (md.parent / "numbers.json")
    numbers = None
    if nb_path.exists():
        numbers = _load_json(nb_path)
    data_dir = Path(args.data_dir) if args.data_dir else md.parent

    c = Checker(md, numbers, data_dir, verbose=args.verbose)
    print(f"== build_check: {md.name}" +
          (f" (numbers table: {nb_path.name})" if numbers is not None else ""))
    c.check_placeholders()
    c.check_exhibits()
    c.check_numbers()
    c.check_frontmatter()
    c.check_tables()
    c.add("J1-f/registry", "number reference table (numbers.json)",
          nb_path.exists(), str(nb_path.name) if nb_path.exists()
          else "MISSING — write a 数字引用表 to turn on J1-c/J1-e key-row checks")
    ok = c.verdict()
    if args.json:
        print(json.dumps([
            {"family": f, "name": n, "status": "PASS" if o else "FAIL", "detail": d}
            for f, n, o, d in c.results
        ], ensure_ascii=False, indent=1))
    return EXIT_OK if ok else EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
