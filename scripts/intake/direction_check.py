#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
direction_check.py — S1 Direction Check CLI for the Wall Street Research pipeline.

Enforces gate **G0b**: the six direction-confirmation questions of S1 must be
answered *by the user*, the driver map must separate `direct` from `theme`, and
the falsification condition must be observable.  See `pipeline/logic_mapping.md`
for the questionnaire itself.

Why a script and not a paragraph of prose: the expensive failure mode is a run
that quietly answers the direction questions on the user's behalf and then
produces a beautifully typeset report nobody asked for.  A default filled in by
the agent is a **fabricated thesis**, so it fails the gate here by construction.

Agent-agnostic by design: pure Python standard library, no third-party
dependencies.  Any AI tool (Claude Code, Codex, Cursor, ...) or a human can run
it — or hand-write the same JSON.

Usage:
  python scripts/intake/direction_check.py --questions
  python scripts/intake/direction_check.py --skeleton > brief/direction_confirmed.json
  python scripts/intake/direction_check.py --check brief/direction_confirmed.json

Exit codes: 0 = G0b passes, 1 = G0b fails, 2 = usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

VIEWS = ("trade", "fundamental", "trend")
ANCHORS = ("company_guidance", "consensus", "user_range", "historical_extrapolation")
ORIENTATIONS = ("valuation-driven", "event-driven", "thematic")
EMPHASES = ("growth", "risk", "valuation")
ANSWERED_BY = ("user", "user-delegated")

QUESTIONS = [
    ("Q1", "view", "视角与期限 / View & horizon",
     "这份报告替谁看、看多久？ trade ≤3 个月 · fundamental 6–12 个月 · trend 3 年+"),
    ("Q2", "primary_driver", "主线变量 / Primary driver",
     "A3 的候选里哪一条是这份报告的论点轴？（可重排、可新增）"),
    ("Q3", "assumption_anchor", "核心假设锚点 / Assumption anchor",
     "量/价用哪套假设？ company_guidance · consensus · user_range · historical_extrapolation"),
    ("Q4", "competitive_set", "真正的对手 / Competitive set",
     "直接同业、替代技术、相邻巨头跨界——都是谁？（可多选）"),
    ("Q5", "falsification", "证伪条件 / Falsification",
     "出现什么**可观测**信号就否决这条逻辑？（订单/出货/ASP/产能利用率/毛利/政策文件编号）"),
    ("Q6", "output_orientation", "产出取向 / Output orientation",
     "valuation-driven · event-driven · thematic，侧重 growth / risk / valuation"),
]

# Words that mean "no observable condition was stated" — a mood is not a falsifier.
VAGUE_TOKENS = ("sentiment", "mood", "feeling", "gut", "情绪", "感觉", "氛围", "人气")
# Vocabulary that suggests the condition is actually checkable (/warn only, never /fail).
OBSERVABLE_TOKENS = (
    "order", "shipment", "asp", "price", "margin", "gross", "revenue", "utilis", "utiliz",
    "inventory", "backlog", "tender", "guidance", "disclos", "capex", "volume", "share",
    "unit", "contract", "delivery", "subsidy", "yoy", "qoq",
    "出货", "订单", "毛利", "收入", "产能", "价格", "招标", "库存", "交付", "披露", "占比", "指引", "销量",
)


def skeleton() -> dict:
    """Empty contract with the six questions spelled out — fill, do not invent."""
    return {
        "ticker": "",
        "as_of": "",
        "view": None,
        "primary_driver": "",
        "driver_tags": [{"driver": "", "tag": "direct", "proxy": ""}],
        "assumption_anchor": None,
        "assumption_note": "",
        "competitive_set": [],
        "falsification": "",
        "output_orientation": {"orientation": None, "emphasis": []},
        "answers": [
            {"q": q, "field": field, "answer": None, "answered_by": None,
             "note": "REQUIRED — ask the user; answered_by must be 'user' or 'user-delegated'"}
            for q, field, _zh, _hint in QUESTIONS
        ],
        "direction_assumed": False,
        "assumed_values": [],
        "created_at": datetime.now().astimezone().replace(microsecond=0).isoformat(),
    }


def questions_block() -> str:
    lines = ["S1 — 方向确认问卷 / Direction confirmation (ask all six, in one pass):", ""]
    for i, (q, field, zh, hint) in enumerate(QUESTIONS, start=1):
        lines.append("%d) [%s] %s  →  field: %s" % (i, q, zh, field))
        lines.append("   %s" % hint)
    lines += [
        "",
        "Rules: options must come from the Part A logic map (pipeline/logic_mapping.md §3);",
        "no leading questions; every option states its consequence; \"你定\" → recommend + reason,",
        "take an explicit yes/adjust and record answered_by=\"user-delegated\"; never fill in a default",
        "the user did not give — that fails gate G0b.",
    ]
    return "\n".join(lines)


def _is_iso(value: object) -> bool:
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def check(doc: object) -> tuple[list[tuple[str, str, str]], bool]:
    """Run every G0b check; each check reports PASS or FAIL (plus WARN notes)."""
    rows: list[tuple[str, str, str]] = []

    def rec(status: str, name: str, detail: str = "") -> None:
        rows.append((status, name, detail))

    def chk(cond: bool, name: str, fail_detail: str = "", pass_detail: str = "") -> bool:
        rec("PASS" if cond else "FAIL", name, pass_detail if cond else fail_detail)
        return bool(cond)

    if not isinstance(doc, dict):
        rec("FAIL", "top-level JSON object", "the artifact must be a JSON object")
        return rows, False

    # --- required fields --------------------------------------------------
    required = ("ticker", "as_of", "view", "primary_driver", "driver_tags", "assumption_anchor",
                "competitive_set", "falsification", "output_orientation", "answers",
                "direction_assumed", "created_at")
    missing = [k for k in required if k not in doc]
    chk(not missing, "all required fields present",
        "missing: %s" % ", ".join(missing) if missing else "",
        "%d/%d fields present" % (len(required) - len(missing), len(required)))

    ticker = str(doc.get("ticker", "")).strip()
    chk(bool(ticker), "ticker", "empty — a run without a ticker has no direction",
        "ticker = %s" % ticker)

    as_of = str(doc.get("as_of", "")).strip()
    chk(bool(as_of), "as_of", "empty — date the direction was confirmed", "as_of = %s" % as_of)

    view = doc.get("view")
    chk(view in VIEWS, "view ∈ %s" % "|".join(VIEWS), "got %r" % (view,), "view = %s" % view)

    anchor = doc.get("assumption_anchor")
    chk(anchor in ANCHORS, "assumption_anchor ∈ %s" % "|".join(ANCHORS),
        "got %r" % (anchor,), "anchor = %s" % anchor)

    oo = doc.get("output_orientation")
    chk(isinstance(oo, dict), "output_orientation is an object", "got %r" % (oo,))
    if isinstance(oo, dict):
        org = oo.get("orientation")
        chk(org in ORIENTATIONS, "orientation ∈ %s" % "|".join(ORIENTATIONS),
            "got %r" % (org,), "orientation = %s" % org)
        emph = oo.get("emphasis")
        emp_ok = isinstance(emph, list) and bool(emph) and not (set(map(str, emph)) - set(EMPHASES))
        chk(emp_ok, "emphasis ⊆ %s" % "|".join(EMPHASES), "got %r" % (emph,),
            "emphasis = %s" % ", ".join(map(str, emph or [])))

    # --- driver tags: direct vs theme -------------------------------------
    tags = doc.get("driver_tags")
    chk(isinstance(tags, list) and bool(tags), "driver_tags is a non-empty array", "got %r" % (tags,))
    direct: list[str] = []
    if isinstance(tags, list) and tags:
        bad_struct = [i for i, t in enumerate(tags) if not isinstance(t, dict)]
        chk(not bad_struct, "every driver_tags entry is an object",
            "bad entries at index %s" % bad_struct)
        named = [i for i, t in enumerate(tags)
                 if isinstance(t, dict) and not str(t.get("driver", "")).strip()]
        chk(not named, "every driver is named", "unnamed at index %s" % named)
        untagged = [i for i, t in enumerate(tags)
                    if isinstance(t, dict) and t.get("tag") not in ("direct", "theme")]
        chk(not untagged, "every driver tagged direct|theme",
            "untagged/unknown tag at index %s" % untagged)
        noproxy = [i for i, t in enumerate(tags)
                   if isinstance(t, dict) and not str(t.get("proxy", "")).strip()]
        chk(not noproxy, "every driver has an observable proxy",
            "no proxy at index %s — name the series that would show it" % noproxy)
        direct = [str(t.get("driver")) for t in tags
                  if isinstance(t, dict) and t.get("tag") == "direct"]
        chk(bool(direct), "at least one driver tagged 'direct'",
            "with no direct driver this is a trade, not a research subject — say so explicitly instead",
            "%d direct / %d theme" % (len(direct), len(tags) - len(direct)))

    primary = str(doc.get("primary_driver", "")).strip()
    chk(bool(primary), "primary_driver is non-empty", "empty — Q2 selects the axis")
    if primary and isinstance(tags, list):
        names = [str(t.get("driver", "")).lower() for t in tags if isinstance(t, dict)]
        hit = any(primary.lower() in n or n in primary.lower() for n in names if n)
        chk(hit, "primary_driver matches a tagged driver", "%r not among %r" % (primary, names),
            "axis = %s" % primary)

    cs = doc.get("competitive_set")
    chk(isinstance(cs, list) and bool(cs) and all(str(x).strip() for x in cs),
        "competitive_set is a non-empty array of names",
        "got %r — 'the usual peers' is still an answer, name them" % (cs,),
        "%d named" % (len(cs) if isinstance(cs, list) else 0))

    # --- falsification must be observable --------------------------------
    fal = str(doc.get("falsification", "")).strip()
    if chk(len(fal) >= 12, "falsification is stated", "got %r" % (fal,),
           "%.60s%s" % (fal, "…" if len(fal) > 60 else "")):
        vague = [t for t in VAGUE_TOKENS if t in fal.lower()]
        chk(not vague, "falsification is observable, not a mood",
            "%r reads as a mood — name the series or event that would settle it" % fal)
        if not any(t in fal.lower() for t in OBSERVABLE_TOKENS):
            rec("WARN", "falsification looks checkable?",
                "no obvious series keyword — double-check the user can verify it")

    # --- the six answers, by the user -------------------------------------
    answers = doc.get("answers")
    chk(isinstance(answers, list) and bool(answers), "answers is a non-empty array",
        "got %r" % (answers,))
    if isinstance(answers, list) and answers:
        by_q: dict[str, dict] = {str(a.get("q", "")): a for a in answers if isinstance(a, dict)}
        for q, field, zh, _hint in QUESTIONS:
            item = by_q.get(q)
            if item is None:
                rec("FAIL", "%s (%s) answered" % (q, field), "missing — ask it")
                continue
            who = item.get("answered_by")
            ans = item.get("answer")
            filled = ans is not None and not (isinstance(ans, str) and not ans.strip()) and ans != []
            who_ok = who in ANSWERED_BY
            chk(who_ok and filled, "%s (%s) answered by the user" % (q, field),
                "answered_by=%r, answer=%r — an agent-filled default is a fabricated thesis and fails G0b"
                % (who, ans) if not (who_ok and filled) else "",
                "answered_by=%s" % who)
            if not str(item.get("field", "")).strip():
                rec("WARN", "%s (field set)" % q, "should be %r" % field)

    # --- assumption disclosure -------------------------------------------
    assumed = doc.get("direction_assumed")
    chk(isinstance(assumed, bool), "direction_assumed is a boolean", "got %r" % (assumed,),
        "direction_assumed = %s" % assumed)
    if assumed is True:
        av = doc.get("assumed_values")
        chk(isinstance(av, list) and bool(av) and all(str(x).strip() for x in av),
            "assumed_values listed (direction_assumed=true)",
            "assumed directions must be listed on the report cover note",
            "%d assumed value(s) — print them on the cover note" % (len(av) if isinstance(av, list) else 0))

    chk(_is_iso(doc.get("created_at", "")), "created_at is ISO-8601",
        "got %r" % (doc.get("created_at"),), "created_at = %s" % doc.get("created_at"))

    ok = not any(status == "FAIL" for status, _n, _d in rows)
    n_pass = len([r for r in rows if r[0] == "PASS"])
    if ok:
        rec("PASS", "→ G0b", "%d checks passed — direction confirmed, S2 may start" % n_pass)
    return rows, ok


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="direction_check.py",
        description="S1 direction contract — gate G0b of the Wall Street Research pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See pipeline/logic_mapping.md §4 (the questionnaire) and §7 (the gate).",
    )
    ap.add_argument("--questions", action="store_true", help="print the six questions to ask the user")
    ap.add_argument("--skeleton", action="store_true", help="print an empty direction_confirmed.json template")
    ap.add_argument("--check", metavar="PATH", help="validate a brief/direction_confirmed.json")
    args = ap.parse_args(argv)

    if args.questions:
        print(questions_block())
        return 0

    if args.skeleton:
        print(json.dumps(skeleton(), indent=2, ensure_ascii=False))
        return 0

    if not args.check:
        ap.print_help()
        return 2

    path = Path(args.check)
    if not path.exists():
        print("error: %s not found" % path, file=sys.stderr)
        return 2
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print("error: %s is not valid JSON — %s" % (path, exc), file=sys.stderr)
        return 2

    rows, ok = check(doc)
    print("G0b direction check — %s" % path)
    print("=" * 78)
    for status, name, detail in rows:
        mark = {"FAIL": "x", "WARN": "!", "PASS": "+"}.get(status, "?")
        print("[%s] %-46s %s" % (mark, name, detail))
    print("=" * 78)
    n_fail = len([r for r in rows if r[0] == "FAIL"])
    n_warn = len([r for r in rows if r[0] == "WARN"])
    n_pass = len([r for r in rows if r[0] == "PASS"])
    print("G0b: %s   (%d passed, %d failed, %d warning%s)"
          % ("PASS" if ok else "FAIL", n_pass, n_fail, n_warn, "" if n_warn == 1 else "s"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
