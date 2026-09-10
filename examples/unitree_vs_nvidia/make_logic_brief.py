#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_logic_brief.py — fill the S1 industry-logic map for the Unitree-vs-NVIDIA case.

Everything numeric here is read from `data/numbers.json`, which was produced by
`compute_numbers.py` from fetched market data. Nothing in the generated file is
hand-typed; re-run this script after re-running compute_numbers.py and the map
follows the data.

Usage:  python examples/unitree_vs_nvidia/make_logic_brief.py
Output: examples/unitree_vs_nvidia/brief/industry_logic.md

Note: this is a *retro-fit* illustration. The case report was written before the
S1 stage existed; the artifact below shows what S1 produces, filled in with this
case's real numbers, so the format is not a promise on paper.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NUMBERS = HERE / "data" / "numbers.json"
OUT = HERE / "brief" / "industry_logic.md"


def c(x: float, digits: int = 2) -> str:
    """CNY 亿元 formatting."""
    return "¥{:.{d}f}亿".format(x, d=digits)


def main() -> int:
    n = json.loads(NUMBERS.read_text(encoding="utf-8"))
    u, v, g = n["unitree"], n["nvidia"], n["gaps"]

    out = f"""# Industry logic — 宇树科技 / Unitree Robotics ({u['ticker']}) vs NVIDIA ({v['ticker']})

> **S1 artifact** — filled example. Numbers are read from `data/numbers.json` by
> `make_logic_brief.py` (itself produced by `compute_numbers.py`); nothing here is hand-typed.
> Retro-fit: the report in this folder was written before S1 existed — this shows what S1 outputs.

## 1. How the company actually makes money
- **Unitree** — revenue is robot hardware: quadruped + humanoid units sold as products to
  research/industrial/consumer buyers. Revenue trajectory (CNY): FY2022 {c(u['fy2022_rev_cny_100m'])} →
  FY2023 {c(u['fy2023_rev_cny_100m'])} → FY2024 {c(u['fy2024_rev_cny_100m'])} → FY2025 {c(u['fy2025_rev_cny_100m'])}
  (FY2025 yoy {u['fy2025_rev_yoy_pct']:.1f}%), TTM {c(u['rev_ttm_cny_100m'])}; FY2025 gross margin
  {u['fy2025_gm_pct']:.1f}%; latest half-year revenue {c(u['h1_2026_rev_cny_100m'])} (yoy {u['h1_2026_rev_yoy_pct']:.1f}%).
  **Revenue exists and is compounding — this is not a pre-revenue story.** The question is not
  whether there is a business, it is what the business is worth at the price asked.
- **NVIDIA** — TTM revenue ¥{v['rev_ttm_cny_tn']:.2f}tn (${v['rev_ttm_usd_bn']:.1f}bn), net margin {v['net_margin_pct']:.1f}%.
- **Chain position** — Unitree sits at the **integrator link**: it buys actuators, reducers, sensors
  and compute, and sells finished robots. Pricing power at this link is weak-to-moderate: hardware is
  differentiable on performance and cost, but the input stack is shared with every other humanoid
  vendor, so the moat has to be proven in **unit economics and iteration speed**, not in the label.
  Role: **price-taker toward input suppliers, price-maker only if its units stay differentiated.**
  NVIDIA sits upstream of compute, where pricing power is currently at its strongest
  (PS {v['ps_ttm']:.1f}x vs Unitree {u['ps_ttm']:.1f}x).

## 2. Driver table
| Driver | Tag | Observable proxy | Source |
|---|---|---|---|
| Humanoid/quadruped **shipment volume × realised ASP** | `direct` — enters Unitree's own revenue line | quarterly unit shipments + disclosed ASP / revenue-per-unit from filings | Unitree filings; `data/unitree_all.json` |
| Gross margin on delivered units | `direct` — enters Unitree's own margin line | gross margin per period (FY2025 {u['fy2025_gm_pct']:.1f}%, H1 2026 {u['h1_2026_gm_pct']:.1f}%) | Unitree filings |
| "AI/robotics is the next platform" sector narrative | `theme` — moves the sector's multiple, **not** Unitree's P&L | sector index / peer multiples; **never** counted as Unitree revenue | market data |
| Compute demand (accelerators) | `direct` for NVIDIA only — Unitree's cost line, not its revenue | NVIDIA data-centre revenue; Unitree BOM commentary | `data/nvda_all.json` |

**Hard rule applied:** the robotics-narrative driver is tagged `theme` and is **not** written up as
Unitree revenue. The one `direct` driver that matters is shipments × ASP, which the filings do report.

## 3. Transmission chain
```
shipments × ASP → Unitree revenue → gross margin → the multiple the market pays
      ↑ proxy            ↑ proxy            ↑ proxy
```
- hop 1 (shipments × ASP → revenue): **proxy = period revenue and unit disclosures** (verifiable in filings).
- hop 2 (revenue → margin): **proxy = disclosed gross margin** ({u['fy2025_gm_pct']:.1f}% FY2025 → {u['h1_2026_gm_pct']:.1f}% H1 2026 — the direction of this hop is the actual debate).
- hop 3 (margin → multiple): **proxy = PS / PE paid** (PS {u['ps_ttm']:.1f}x, PE-TTM {u['pe_ttm']:.1f}x on TTM net profit of {c(u['np_ttm_cny_100m'])}).
- hop 4 (the market's comparison with NVIDIA): **`unverifiable` as a causal link** — Unitree's P&L has no NVIDIA
  sensitivity. It is a *valuation* comparison (market cap gap {g['market_cap_x']:.0f}x, revenue gap
  {g['revenue_x']:.0f}x as computed in `numbers.json`), not a transmission channel. The report must
  present it as "two multiples, one question", never as "Unitree revenue depends on NVIDIA".

## 4. Cycle & relative position
- Phase: **early growth with a new-listing overlay** — industry phase: emerging; the listing overlay is
  Unitree-specific (issued at {c(u['issue_price'])} on a {u['x_issue_price']:.2f}x day-one open of
  {c(u['day1_open'])}, {u['pct_from_day1_open']:.1f}% below it since). Base rate for newly-listed high-multiple
  growth names: the first-year path is dominated by supply/lock-up and narrative, not by quarterly fundamentals.
- Relative position: Unitree's TTM revenue is {g['unitree_rev_share_of_nvda_pct']:.3f}% of NVIDIA's
  ({c(u['rev_ttm_cny_100m'])} vs ¥{v['rev_ttm_cny_tn']:.2f}tn) — i.e. it is not a competitor,
  it is a different order of magnitude being asked the same question.
- Growth quality: revenue CAGR FY23–FY25 {u['rev_cagr_23_25_pct']:.1f}% with FY2025 gross margin
  {u['fy2025_gm_pct']:.1f}% — the fastest leg is real, and the H1 2026 deceleration
  (yoy {u['h1_2026_rev_yoy_pct']:.1f}%) is the number to watch.

## 5. What would break this / 这份逻辑的断点
- **The margin hop.** If delivered-unit gross margin keeps falling ({u['fy2025_gm_pct']:.1f}% → {u['h1_2026_gm_pct']:.1f}%),
  revenue growth stops translating into value, and the multiple has nothing behind it.
- **The shipment hop.** Two consecutive periods of unit growth below the trajectory implied by the
  FY2023–FY2025 revenue path would put the growth premium itself in question.
- **The scale question is not falsifiable — it is arithmetic** ({c(u['rev_ttm_cny_100m'])} vs ¥{v['rev_ttm_cny_tn']:.2f}tn).
  The report's job is to stop treating it as a narrative and state it as a number.
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out, encoding="utf-8")
    print("wrote %s (%d chars)" % (OUT, len(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
