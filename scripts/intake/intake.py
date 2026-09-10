#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intake.py — S0 Intake CLI for the Wall Street Research pipeline.

Records the two answers the pipeline needs BEFORE a run starts:

  1. the report layout template the user picked (six style-only presets), and
  2. the research focus questionnaire (focus / horizon / depth / language /
     chart density / special requests).

It writes `brief/intake.json` — the artifact consumed by S2 (envelope), the
analyst briefs, the Red Team, the Chart Specialist and the Layout Specialist.
See `pipeline/intake.md` for the full questionnaire and injection rules.

Agent-agnostic by design: pure Python standard library, no third-party
dependencies. Any AI tool (Claude Code, Codex, Cursor, ...) or a human can run
it — or hand-write the same JSON.

Usage:
  python scripts/intake/intake.py --list
  python scripts/intake/intake.py --template goldman_hardline \
      --focus valuation,growth --horizon medium --depth full \
      --language en --charts high --notes "focus on FCF inflection"

Defaults applied to any flag you omit:
  template  goldman_hardline      horizon  medium
  depth     standard              language en
  charts    standard              focus    valuation,growth
  notes     (none)

Output: <repo_root>/brief/intake.json   (override with --out PATH)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()
STYLES_DIR = REPO_ROOT / "templates" / "styles"
DEFAULT_OUT = REPO_ROOT / "brief" / "intake.json"

# Presentation order (matches pipeline/intake.md and templates/styles/README.md)
TEMPLATE_ORDER = [
    "goldman_hardline",
    "morganstanley_restrained",
    "jpmorgan_heavyset",
    "barclays_cyanline",
    "bernstein_monochrome",
    "ubs_swissminimal",
]

# Fallback catalogue: used only if templates/styles/*.json cannot be read
# (e.g. this script was copied out of the repo on its own).
FALLBACK_TEMPLATES = [
    {"id": "goldman_hardline",
     "display_name": "高盛（硬朗风） / Hardline",
     "style_en": "Open grid, serif masthead, navy accents, hairline rules, high density",
     "style_zh": "开放式无框版式；衬线大标题+无衬线正文；深蓝强调；水平细线分区；高信息密度"},
    {"id": "morganstanley_restrained",
     "display_name": "摩根士丹利（克制风） / Restrained",
     "style_en": "Airy single column, light-weight sans masthead, one blue accent, wide margins",
     "style_zh": "大留白单栏；轻字重大标题；单一蓝色点缀；宽边距；低密度封面感"},
    {"id": "jpmorgan_heavyset",
     "display_name": "摩根大通（厚重风） / Heavyset",
     "style_en": "Dense two-column, bold sans headers over serif body, slate-blue accents",
     "style_zh": "高密度双栏；无衬线粗标题+衬线正文；灰蓝强调；灰底表头；紧凑行距"},
    {"id": "barclays_cyanline",
     "display_name": "巴克莱（青蓝风） / Cyan Line",
     "style_en": "Cyan header band, tinted side rail, cyan table header on white text, light headings",
     "style_zh": "青色页眉带；右侧浅蓝信息栏；青色表头白字；细字重大标题；中高密度"},
    {"id": "bernstein_monochrome",
     "display_name": "伯恩斯坦（学术黑白风） / Monochrome",
     "style_en": "Strict black-and-white, black masthead bar, serif body, dense grid, no color",
     "style_zh": "纯黑白；黑色顶栏；衬线正文；紧凑网格；无彩色元素；学术气质"},
    {"id": "ubs_swissminimal",
     "display_name": "瑞银（瑞士极简风） / Swiss Minimal",
     "style_en": "Two-tier title bands, deep navy + pale blue, right info rail, generous margins",
     "style_zh": "双层标题色带；深海军蓝+浅蓝；右侧信息栏；宽边距；克制的中等密度"},
]

# --------------------------------------------------------------------------
# Allowed questionnaire values (canonical token -> description)
# --------------------------------------------------------------------------
FOCUS_VALUES = {
    "valuation": "估值 / valuation-driven",
    "growth": "成长 / growth",
    "cyclical": "周期 / cyclical",
    "event-driven": "事件驱动 / event-driven",
    "defensive": "防御 / defensive",
    "bull-bear": "多空辩论 / bull-bear debate",
}
FOCUS_ALIASES = {
    "event": "event-driven",
    "event_driven": "event-driven",
    "events": "event-driven",
    "cycle": "cyclical",
    "defense": "defensive",
    "bullbear": "bull-bear",
    "bull_bear": "bull-bear",
    "debate": "bull-bear",
}
HORIZON_VALUES = {"short": "≤3 months", "medium": "6–12 months", "long": ">12 months"}
DEPTH_VALUES = {
    "quick": "fast brief — no red-team child, no figures",
    "standard": "standard research note — full chain, ≥3 figures",
    "deep": "full deep-dive — full figure set, 2 red-team rounds",
}
DEPTH_ALIASES = {"full": "deep"}
LANGUAGE_VALUES = {"en": "English", "bilingual": "English + 中文", "zh": "中文"}
CHART_VALUES = {"low": "1–2 figures", "standard": "3–5 figures", "high": "full set (6+)"}
CHART_ALIASES = {"medium": "standard", "med": "standard"}

DEFAULTS = {
    "template": "goldman_hardline",
    "focus": ["valuation", "growth"],
    "horizon": "medium",
    "depth": "standard",
    "language": "en",
    "charts": "standard",
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _force_utf8_stdout() -> None:
    """Keep Chinese template names printable on any console / pipe."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def load_templates():
    """Read templates/styles/*.json; fall back to the built-in catalogue."""
    templates = []
    if STYLES_DIR.is_dir():
        for path in sorted(STYLES_DIR.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(data, dict) or not data.get("id"):
                continue
            templates.append({
                "id": data["id"],
                "display_name": data.get("display_name", data["id"]),
                "style_en": data.get("style_en", ""),
                "style_zh": data.get("style_zh", ""),
            })
    if not templates:
        templates = list(FALLBACK_TEMPLATES)

    order = {tid: i for i, tid in enumerate(TEMPLATE_ORDER)}
    templates.sort(key=lambda t: (order.get(t["id"], len(order)), t["id"]))
    return templates


def _normalize(value: str, aliases: dict) -> str:
    return aliases.get(value, value)


def _parse_focus(raw: str, errors: list) -> list:
    out, seen = [], set()
    for item in raw.split(","):
        token = item.strip().lower().replace(" ", "-")
        if not token:
            continue
        token = _normalize(token, FOCUS_ALIASES)
        if token not in FOCUS_VALUES:
            errors.append(
                "unknown --focus value '%s' (allowed: %s)"
                % (item.strip(), ", ".join(FOCUS_VALUES))
            )
            continue
        if token not in seen:
            seen.add(token)
            out.append(token)
    if not out and not errors:
        errors.append("--focus was empty; give at least one of: %s" % ", ".join(FOCUS_VALUES))
    return out


def _parse_list(raw: str) -> list:
    """Comma- or semicolon-separated free text -> list, order preserved."""
    items = []
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk and chunk not in items:
            items.append(chunk)
    return items


def cmd_list(templates: list) -> int:
    print("Wall Street Research — layout templates (style-only; no institution logos or text marks)")
    print("=" * 88)
    for i, t in enumerate(templates, 1):
        print("%d. %s" % (i, t["id"]))
        print("   %s" % t["display_name"])
        if t.get("style_zh"):
            print("   zh: %s" % t["style_zh"])
        if t.get("style_en"):
            print("   en: %s" % t["style_en"])
        print()
    print("Choose one with:  --template <id>   (a mix / custom layout is allowed — describe it in --notes)")
    print("Questionnaire options: --focus %s | --horizon %s | --depth %s"
          % ("|".join(FOCUS_VALUES), "|".join(HORIZON_VALUES), "|".join(DEPTH_VALUES)))
    print("                       --language %s | --charts %s | --notes \"...\""
          % ("|".join(LANGUAGE_VALUES), "|".join(CHART_VALUES)))
    print("This command writes nothing.")
    return 0


def main(argv=None) -> int:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        prog="intake.py",
        description="S0 Intake — choose a report layout template and record the research focus questionnaire.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See pipeline/intake.md for the full S0 procedure and how each answer is injected into the pipeline.",
    )
    parser.add_argument("--list", action="store_true",
                        help="list the six layout templates (id + display name + one-line style); writes nothing")
    parser.add_argument("--template", metavar="ID",
                        help="layout template id (default: %s)" % DEFAULTS["template"])
    parser.add_argument("--focus", metavar="LIST",
                        help="comma-separated research focus (default: valuation,growth); "
                             "allowed: " + ", ".join(FOCUS_VALUES))
    parser.add_argument("--horizon", metavar="H", help="short | medium | long (default: medium)")
    parser.add_argument("--depth", metavar="D", help="quick | standard | deep (alias: full) (default: standard)")
    parser.add_argument("--language", metavar="L", help="en | bilingual | zh (default: en)")
    parser.add_argument("--charts", metavar="C", help="low | standard | high (alias: medium) (default: standard)")
    parser.add_argument("--notes", metavar="TEXT",
                        help="free-text special request (ESG, technicals, policy, peer comparison, template mix, ...)")
    parser.add_argument("--special", metavar="LIST",
                        help="extra special requests, comma-separated; merged with --notes")
    parser.add_argument("--out", metavar="PATH",
                        help="output path (default: <repo_root>/brief/intake.json)")
    args = parser.parse_args(argv)

    templates = load_templates()
    by_id = {t["id"]: t for t in templates}

    if args.list:
        return cmd_list(templates)

    errors = []

    # --- template ---------------------------------------------------------
    template_id = args.template.strip() if args.template else DEFAULTS["template"]
    template_used_default = not args.template
    if template_id not in by_id:
        errors.append("unknown --template '%s' (valid ids: %s)"
                      % (template_id, ", ".join(t["id"] for t in templates)))
    template = by_id.get(template_id, {})

    # --- questionnaire ----------------------------------------------------
    focus = _parse_focus(args.focus, errors) if args.focus else list(DEFAULTS["focus"])

    horizon = (args.horizon or DEFAULTS["horizon"]).strip().lower()
    horizon = _normalize(horizon, {"6m": "medium", "12m": "medium", "1y": "medium", "3m": "short", "5y": "long"})
    if horizon not in HORIZON_VALUES:
        errors.append("unknown --horizon '%s' (allowed: %s)" % (args.horizon, ", ".join(HORIZON_VALUES)))

    depth_raw = (args.depth or DEFAULTS["depth"]).strip().lower()
    depth = _normalize(depth_raw, DEPTH_ALIASES)
    if depth not in DEPTH_VALUES:
        errors.append("unknown --depth '%s' (allowed: %s; alias full=deep)"
                      % (args.depth, ", ".join(DEPTH_VALUES)))

    language = (args.language or DEFAULTS["language"]).strip().lower()
    language = _normalize(language, {"zh-cn": "zh", "cn": "zh", "both": "bilingual", "en+zh": "bilingual"})
    if language not in LANGUAGE_VALUES:
        errors.append("unknown --language '%s' (allowed: %s)" % (args.language, ", ".join(LANGUAGE_VALUES)))

    charts_raw = (args.charts or DEFAULTS["charts"]).strip().lower()
    charts = _normalize(charts_raw, CHART_ALIASES)
    if charts not in CHART_VALUES:
        errors.append("unknown --charts '%s' (allowed: %s; alias medium=standard)"
                      % (args.charts, ", ".join(CHART_VALUES)))

    special_requests = []
    if args.notes:
        special_requests.extend(_parse_list(args.notes))
    if args.special:
        special_requests.extend(x for x in _parse_list(args.special) if x not in special_requests)

    if errors:
        print("[intake] ERROR — nothing written:", file=sys.stderr)
        for err in errors:
            print("  - %s" % err, file=sys.stderr)
        print("\nRun 'python scripts/intake/intake.py --list' to see the templates.", file=sys.stderr)
        return 2

    payload = {
        "template_id": template_id,
        "template_display_name": template.get("display_name", template_id),
        "focus_areas": focus,
        "horizon": horizon,
        "depth": depth,
        "language": language,
        "chart_density": charts,
        "special_requests": special_requests,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }

    out_path = Path(args.out).expanduser() if args.out else DEFAULT_OUT
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- report -----------------------------------------------------------
    print("[intake] template : %s — %s%s"
          % (template_id, payload["template_display_name"],
             "  (default)" if template_used_default else ""))
    print("[intake] focus    : %s" % ", ".join(focus))
    print("[intake] horizon  : %s (%s)" % (horizon, HORIZON_VALUES[horizon]))
    print("[intake] depth    : %s — %s" % (depth, DEPTH_VALUES[depth]))
    print("[intake] language : %s (%s)" % (language, LANGUAGE_VALUES[language]))
    print("[intake] charts   : %s (%s)" % (charts, CHART_VALUES[charts]))
    print("[intake] special  : %s" % (", ".join(special_requests) if special_requests else "(none)"))
    print("[intake] wrote    : %s" % out_path)
    print("[intake] content  :")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("[intake] next     : S2 — build envelope.json from this file (see pipeline/intake.md §Injection).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
