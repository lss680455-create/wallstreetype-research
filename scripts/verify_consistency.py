#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_consistency.py — repo self-check for the Wall Street Research pipeline.

Run from the repo root:

    python scripts/verify_consistency.py

Checks the invariants that break silently when stages are inserted or renamed:

 1. no stage token outside S0–S10 anywhere in the tree;
 2. `pipeline/pipeline_orchestration.md` defines exactly S0…S10, in order;
 3. every stage declares the gate it owns (S0→G0, S1→G0b, S2→G0c, S3→G0d, S4→G1 … S10→G7);
 4. the six direction questions (Q1–Q6) exist in every surface that promises them;
 5. every relative markdown link and in-page anchor in the three READMEs resolves;
 6. the pipeline scripts compile;
 7. the shipped S1 sample passes gate G0b and an answer invented by the agent fails it;
 8. every number in the generated industry-logic map traces back to `data/numbers.json`.

Exit code 0 = all checks pass. stdlib only.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATES = {"S0": "G0", "S1": "G0b", "S2": "G0c", "S3": "G0d", "S4": "G1", "S5": "G2",
         "S6": "G3", "S7": "G4", "S8": "G5", "S9": "G6", "S10": "G7"}
SAMPLE = "examples/unitree_vs_nvidia/brief/direction_confirmed.json"
SAMPLE_MD = "examples/unitree_vs_nvidia/brief/industry_logic.md"


def text_files():
    exts = {".md", ".py", ".txt", ".json", ".yml", ".yaml"}
    skip = ("docs/assets/case", "docs/assets/styles")
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        rel = p.as_posix()
        if "/.git/" in rel or rel.endswith("/.git"):
            continue
        if any(s in rel for s in skip):
            continue
        yield p


def check_stage_tokens():
    bad = []
    for p in text_files():
        t = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\bS(\d{1,2})\b(?!\d)", t):
            if int(m.group(1)) > 10:
                bad.append(f"{p.relative_to(ROOT).as_posix()}: S{m.group(1)}")
    return ("no stage token outside S0–S10", not bad, ", ".join(bad[:6]) or "none found")


def check_stage_order():
    orch = (ROOT / "pipeline/pipeline_orchestration.md").read_text(encoding="utf-8")
    seq = re.findall(r"^### (S\d+) — ", orch, re.M)
    want = [f"S{i}" for i in range(11)]
    return ("stage headings are S0…S10 in order", seq == want, " → ".join(seq))


def check_gate_map():
    orch = (ROOT / "pipeline/pipeline_orchestration.md").read_text(encoding="utf-8")
    parts = re.split(r"^### (S\d+) — ", orch, flags=re.M)[1:]
    got = {}
    for i in range(0, len(parts), 2):
        stage, body = parts[i], parts[i + 1]
        found = re.findall(r"gate \*{0,2}(G0[a-d]?|G[1-7])\b", body) or \
                re.findall(r"\*\*(G0[a-d]?|G[1-7])\*\*", body)
        got[stage] = found[0] if found else "?"
    ok = got == GATES
    return ("each stage declares its own gate", ok,
            "; ".join(f"{k}→{v}" for k, v in got.items()))


def check_questions():
    surfaces = ["pipeline/logic_mapping.md", "README.md", "README_EN.md",
                "scripts/intake/direction_check.py"]
    detail, ok = [], True
    for f in surfaces:
        t = (ROOT / f).read_text(encoding="utf-8")
        n = len(set(re.findall(r"\bQ([1-6])\b", t)))
        ok &= n == 6
        detail.append(f"{f} {n}/6")
    return ("the six direction questions on every surface", ok, " · ".join(detail))


def _slugs(text):
    out = set()
    for h in re.findall(r"^#{1,6} (.+)$", text, re.M):
        a = h.strip().lower()
        a = re.sub(r"[^\w\u4e00-\u9fff \-]", "", a).replace(" ", "-")
        out.add(a)
    return out


def check_links():
    bad = []
    for f in ["README.md", "README_EN.md", "examples/unitree_vs_nvidia/README.md"]:
        path = ROOT / f
        t = path.read_text(encoding="utf-8")
        anchors = _slugs(t)
        for _label, url in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", t):
            if url.startswith(("http", "mailto")):
                continue
            target, _, frag = url.partition("#")
            if target and not (path.parent / target).exists():
                bad.append(f"{f}: missing {url}")
            elif frag and frag.lower() not in anchors:
                bad.append(f"{f}: no anchor #{frag}")
    return ("relative links and anchors resolve", not bad, ", ".join(bad[:6]) or "0 broken")


def check_compile():
    files = ["scripts/intake/direction_check.py", "examples/unitree_vs_nvidia/make_logic_brief.py",
             "docs/assets/make_readme_assets.py"]
    r = subprocess.run([sys.executable, "-m", "py_compile", "-q", *[str(ROOT / f) for f in files]],
                       capture_output=True, text=True)
    return ("pipeline scripts compile", r.returncode == 0, r.stderr.strip()[:200] or f"{len(files)} files, exit 0")


def _run_check(args):
    return subprocess.run([sys.executable, *args], cwd=str(ROOT), capture_output=True, text=True)


def check_gate_behaviour():
    good = _run_check(["scripts/intake/direction_check.py", "--check", SAMPLE])
    doc = json.loads((ROOT / SAMPLE).read_text(encoding="utf-8"))
    for a in doc["answers"]:
        a["answered_by"] = "agent-default"          # the violation the gate exists to catch
    tmp = ROOT / "brief/_verify_bad.json"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    bad = _run_check(["scripts/intake/direction_check.py", "--check", "brief/_verify_bad.json"])
    tmp.unlink()
    n = len(re.findall(r"^\s*\[", good.stdout, re.M))
    ok = good.returncode == 0 and bad.returncode == 1
    return (f"gate G0b: sample passes, agent-invented answer fails ({n} checks)",
            ok, f"sample exit {good.returncode} · invented exit {bad.returncode}")


def check_traceable_numbers():
    """Every figure in the generated S1 map must exist in data/numbers.json."""
    nums = json.loads((ROOT / "examples/unitree_vs_nvidia/data/numbers.json").read_text(encoding="utf-8"))
    known = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)):
            for s in (f"{o}", f"{o:.1f}", f"{o:.2f}", f"{o:.3f}"):
                known.update({s, s.lstrip("-")})          # the map may write a drop without the sign
            known.add(f"{round(o):,}" if abs(o) >= 1000 else f"{round(o)}")
    walk(nums)

    md = (ROOT / SAMPLE_MD).read_text(encoding="utf-8")
    md = re.sub(r"`[^`]*`", " ", md)                     # ignore inline code / labels
    md = re.sub(r"\b\d{5,6}\.(?:SH|SZ|SS|HK|BJ)\b", " ", md, flags=re.I)   # tickers are labels
    stray = []
    for tok in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", md):
        raw = tok.replace(",", "")
        if raw in known or tok in known:
            continue
        if re.fullmatch(r"(?:19|20)\d\d", raw):           # a year, not a figure
            continue
        if 1 <= float(raw) <= 12 and "." not in raw:      # step numbers
            continue
        stray.append(tok)
    return ("S1 map figures all trace to numbers.json", not stray,
            ", ".join(sorted(set(stray))[:8]) or "all matched")


CHECKS = [check_stage_tokens, check_stage_order, check_gate_map, check_questions,
          check_links, check_compile, check_gate_behaviour, check_traceable_numbers]


def main() -> int:
    print("verify_consistency — %s\n" % ROOT)
    fails = 0
    for i, fn in enumerate(CHECKS, 1):
        name, ok, detail = fn()
        print("[%s] %d. %s — %s" % ("PASS" if ok else "FAIL", i, name, detail))
        fails += 0 if ok else 1
    print("\n%d/%d checks passed" % (len(CHECKS) - fails, len(CHECKS)))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
