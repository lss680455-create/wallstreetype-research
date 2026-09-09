# Wall Street Research — Chart Templates

Static, print-ready financial charts in the institutional investment-bank
visual style, built on **matplotlib + mplfinance**. Output is high-resolution
PNG (500 dpi) that can be embedded directly into Word/PDF research reports.

Pure Python + standard plotting libraries — no browser, no GUI, no server.
Runs identically from a terminal, a CI pipeline, or any agent environment
that can execute Python.

---

## Library selection (why matplotlib + mplfinance)

| Candidate | Static report PNGs | Look & feel | Ease of use | CJK fonts | Verdict |
|---|---|---|---|---|---|
| **mplfinance** (matplotlib/mplfinance) | ✅ first-class (`savefig`, dpi control) | Candles/volume/MA out of the box; style system | Very easy, one call per chart | ✅ inherits matplotlib font handling | **Selected** for price charts |
| **matplotlib** (base) | ✅ publication-quality | Full control; you define the beauty | Moderate; theme helpers included | ✅ best-in-class | **Selected** for all non-price charts |
| **finplot** (highfestiva/finplot) | ❌ PyQtGraph/GUI; screenshots only, no `savefig` | TradingView-like (interactive) | Easy, but interactive-first | ⚠️ GUI fonts, awkward headless | Rejected — wrong paradigm |
| **plotly** | ⚠️ possible via kaleido, dpi control is weak | Pretty, interactive-first | Easy | ⚠️ browser font stack, CJK fiddly | Rejected — interactive, not print |
| **TradingView lightweight-charts** | ❌ client-side JS only; no server-side render | Best interactive candlesticks | n/a from Python | n/a | Rejected — not a static-PNG tool |

Rule that drove the choice: **the deliverable is a 500-dpi static PNG for
docx/PDF embedding, not an interactive widget.** Matplotlib is the only
ecosystem with first-class high-dpi static export, deterministic layout, and
robust CJK fonts (SimHei / Microsoft YaHei registered through font_manager).
mplfinance adds one-call candlestick+volume+MA rendering on top of it.

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `matplotlib`, `mplfinance`, `pandas`, `numpy`.

No data vendor required — every chart function takes plain Python data
(lists / dicts / pandas DataFrame).

## Chinese font handling

`chart_style.py` auto-detects a CJK font at runtime in this order:
**Microsoft YaHei → SimHei → DengXian → SimSun → KaiTi** (searches the OS
font directories, then matplotlib's registry), and falls back to DejaVu Sans
if none exists (CJK glyphs would then render as boxes — install any of the
above to fix). Also sets `axes.unicode_minus = False`, which CJK fonts
require for correct minus signs.

```python
import chart_style as cs
fam, cjk = cs.load_apply()   # applies the theme, prints the resolved font
```

## Quick start

```python
import chart_style as cs
import report_charts as rc
import pandas as pd

cs.apply_theme()

# 1) Candlestick + volume + MA + MACD
df = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
# df columns must be: Open, High, Low, Close, Volume
rc.kline_volume_chart(
    df,
    title="ACME Corp — Price & Volume (Daily)",
    subtitle="MA5/10/20/60 · MACD attached",
    source="Data source: exchange data, company filings",
    out_path="kline.png", macd=True, dpi=500,
)

# 2) PE/PB valuation band
dates = ["2019-09-01", ...]   # one per observation
pe = [22.1, 21.8, ...]        # historical PE(TTM) series
rc.valuation_band_chart(
    dates, pe,
    title="ACME Corp — Historical PE corridor",
    subtitle="Weekly PE(TTM) 2019-2026 · mean±1σ · current percentile",
    source="Data source: Wind, company filings",
    out_path="pe_band.png", metric_name="PE (TTM, x)", dpi=500,
)

# 3) Financial trend (bars + YoY line, dual axis)
rc.financial_trend_chart(
    years=[2019, 2020, 2021, 2022, 2023, 2024, 2025],
    revenue=[8.6, 9.9, 12.4, 14.1, 15.8, 18.3, 21.2],   # RMB 100M
    net_profit=[2.1, 2.5, 3.2, 3.5, 3.9, 4.6, 5.3],
    yoy_growth=[12.4, 15.1, 25.3, 13.7, 12.1, 15.8, 15.8],  # percent points
    title="ACME Corp — Revenue / Net profit & YoY growth",
    subtitle="2019-2025 annual · bars: RMB 100M, line: YoY %",
    source="Data source: annual reports, analyst estimates",
    out_path="financials.png", dpi=500,
)

# 4) Scenario probability (base / bull / bear)
rc.scenario_bar_chart(
    scenarios=[
        {"name": "Bear", "prob": 0.25, "value": 16.8, "desc": "Demand softens"},
        {"name": "Base", "prob": 0.45, "value": 21.5, "desc": "Share gains continue"},
        {"name": "Bull", "prob": 0.30, "value": 27.9, "desc": "New product cycle"},
    ],
    title="ACME Corp — Scenario targets & probability-weighted EV",
    subtitle="Bear 25% / Base 45% / Bull 30%",
    source="Data source: analyst estimates",
    out_path="scenarios.png", current_price=18.6, dpi=500,
)

# 5) Peer comparison (horizontal bars)
rc.peer_compare_chart(
    labels=["ACME (subject)", "Peer A", "Peer B", "Peer C", "Peer D"],
    values=[28.4, 24.1, 31.8, 19.6, 22.3],
    title="Industry comparison — 2026E PE (x)",
    subtitle="Subject company highlighted; dashed line = median",
    source="Data source: consensus estimates",
    out_path="peers.png", xlabel="2026E PE (x)", highlight_idx=0, dpi=500,
)
```

## Chart style reference

- **Palette**: deep navy `#0F2A43` primary, muted gold `#C9A227` accent,
  up = green `#1E8449`, down = red `#C0392B` (US convention; switch
  `cs.UP_COLOR` / `cs.DOWN_COLOR` for A-share red-up style).
- **Layout**: white print background, faint `#E4E9EF` grid, no top/right
  spines, bold navy title + gray subtitle + data-source footer with
  disclaimer and date.
- **Output**: 500 dpi PNG by default (override with `dpi=`), tight bbox,
  ready for docx/PDF embedding.

## Regenerate the sample charts

```bash
python report_charts.py
```

Writes the five demos (synthetic data, clearly labeled as such) into
`./sample_pngs/`:

```
01_kline_volume_macd.png   candlestick + volume + MA5/10/20/60 + MACD
02_pe_valuation_band.png   historical PE corridor with current-point star
03_financial_trend.png     revenue/profit bars + YoY line (dual axis)
04_scenario_probability.png bear/base/bull targets + probability-weighted EV
05_peer_comparison.png     industry PE comparison, subject highlighted
```

## Files

| File | Purpose |
|---|---|
| `chart_style.py`  | Theme (palette, CJK font detection, header/footer, save helpers) |
| `report_charts.py`| The five chart templates + demo data generator |
| `requirements.txt`| Python dependencies |
| `sample_pngs/`    | Generated sample charts (500 dpi) |

## License

MIT — free to use in research reports, portfolios, and open-source projects.
