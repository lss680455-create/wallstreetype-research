# Industry logic — 宇树科技 / Unitree Robotics (688836.SH) vs NVIDIA (NVDA)

> **S1 artifact** — filled example. Numbers are read from `data/numbers.json` by
> `make_logic_brief.py` (itself produced by `compute_numbers.py`); nothing here is hand-typed.
> Retro-fit: the report in this folder was written before S1 existed — this shows what S1 outputs.

## 1. How the company actually makes money
- **Unitree** — revenue is robot hardware: quadruped + humanoid units sold as products to
  research/industrial/consumer buyers. Revenue trajectory (CNY): FY2022 ¥1.23亿 →
  FY2023 ¥1.59亿 → FY2024 ¥3.93亿 → FY2025 ¥16.99亿
  (FY2025 yoy 332.6%), TTM ¥20.76亿; FY2025 gross margin
  60.4%; latest half-year revenue ¥11.52亿 (yoy 48.5%).
  **Revenue exists and is compounding — this is not a pre-revenue story.** The question is not
  whether there is a business, it is what the business is worth at the price asked.
- **NVIDIA** — TTM revenue ¥2.03tn ($303.0bn), net margin 63.7%.
- **Chain position** — Unitree sits at the **integrator link**: it buys actuators, reducers, sensors
  and compute, and sells finished robots. Pricing power at this link is weak-to-moderate: hardware is
  differentiable on performance and cost, but the input stack is shared with every other humanoid
  vendor, so the moat has to be proven in **unit economics and iteration speed**, not in the label.
  Role: **price-taker toward input suppliers, price-maker only if its units stay differentiated.**
  NVIDIA sits upstream of compute, where pricing power is currently at its strongest
  (PS 17.8x vs Unitree 100.1x).

## 2. Driver table
| Driver | Tag | Observable proxy | Source |
|---|---|---|---|
| Humanoid/quadruped **shipment volume × realised ASP** | `direct` — enters Unitree's own revenue line | quarterly unit shipments + disclosed ASP / revenue-per-unit from filings | Unitree filings; `data/unitree_all.json` |
| Gross margin on delivered units | `direct` — enters Unitree's own margin line | gross margin per period (FY2025 60.4%, H1 2026 56.0%) | Unitree filings |
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
- hop 2 (revenue → margin): **proxy = disclosed gross margin** (60.4% FY2025 → 56.0% H1 2026 — the direction of this hop is the actual debate).
- hop 3 (margin → multiple): **proxy = PS / PE paid** (PS 100.1x, PE-TTM 355.8x on TTM net profit of ¥5.84亿).
- hop 4 (the market's comparison with NVIDIA): **`unverifiable` as a causal link** — Unitree's P&L has no NVIDIA
  sensitivity. It is a *valuation* comparison (market cap gap 174x, revenue gap
  978x as computed in `numbers.json`), not a transmission channel. The report must
  present it as "two multiples, one question", never as "Unitree revenue depends on NVIDIA".

## 4. Cycle & relative position
- Phase: **early growth with a new-listing overlay** — industry phase: emerging; the listing overlay is
  Unitree-specific (issued at ¥150.80亿 on a 3.41x day-one open of
  ¥1100.00亿, -53.3% below it since). Base rate for newly-listed high-multiple
  growth names: the first-year path is dominated by supply/lock-up and narrative, not by quarterly fundamentals.
- Relative position: Unitree's TTM revenue is 0.102% of NVIDIA's
  (¥20.76亿 vs ¥2.03tn) — i.e. it is not a competitor,
  it is a different order of magnitude being asked the same question.
- Growth quality: revenue CAGR FY23–FY25 226.8% with FY2025 gross margin
  60.4% — the fastest leg is real, and the H1 2026 deceleration
  (yoy 48.5%) is the number to watch.

## 5. What would break this / 这份逻辑的断点
- **The margin hop.** If delivered-unit gross margin keeps falling (60.4% → 56.0%),
  revenue growth stops translating into value, and the multiple has nothing behind it.
- **The shipment hop.** Two consecutive periods of unit growth below the trajectory implied by the
  FY2023–FY2025 revenue path would put the growth premium itself in question.
- **The scale question is not falsifiable — it is arithmetic** (¥20.76亿 vs ¥2.03tn).
  The report's job is to stop treating it as a narrative and state it as a number.
