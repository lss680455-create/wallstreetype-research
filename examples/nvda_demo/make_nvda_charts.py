"""
make_nvda_charts.py — generate the five institutional chart families for the
NVDA demo report using REAL fetched data (examples/nvda_demo/data/*.json).

Run from the repo root:
    python examples/nvda_demo/make_nvda_charts.py
Outputs PNGs into examples/nvda_demo/figures/ (Exhibit 1..5).
"""
from __future__ import annotations
import json
import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
FIG = os.path.join(BASE, "figures")
ROOT = os.path.dirname(os.path.dirname(BASE))
CH = os.path.join(ROOT, "scripts", "charts")
sys.path.insert(0, CH)

from report_charts import (          # noqa: E402
    kline_volume_chart,
    valuation_band_chart,
    financial_trend_chart,
    scenario_bar_chart,
    peer_compare_chart,
)

SRC = "Source: Yahoo Finance (as of 2026-09-10), company filings; NVIDIA FY ends Jan"


def load_history() -> pd.DataFrame:
    h = json.load(open(os.path.join(DATA, "nvda_history.json"), encoding="utf-8"))
    bars = h["history"]["bars"]
    df = pd.DataFrame(bars)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    df = df.rename(columns={"adj_close": "Adj Close"})
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df.sort_index()


def exhibit1(df: pd.DataFrame) -> None:
    kline_volume_chart(
        df,
        title="NVIDIA Corp. (NVDA) — Price & Volume",
        subtitle="Daily, 1Y · MA 5/10/20/60 · MACD · front-adjusted",
        source=SRC,
        out_path=os.path.join(FIG, "exhibit1_kline.png"),
    )


def exhibit2(df: pd.DataFrame) -> None:
    # Trailing-PE corridor: price history / current TTM EPS (Yahoo trailing EPS 7.90)
    eps_ttm = 7.90
    pe = df["Close"].values / eps_ttm
    dates = [d.strftime("%Y-%m-%d") for d in df.index]
    valuation_band_chart(
        dates, pe,
        title="NVIDIA Corp. — Valuation Corridor",
        subtitle="Trailing P/E (price / TTM EPS $7.90), 1Y · band = mean ± 1σ, max/min",
        source=SRC + "; trailing EPS from Yahoo",
        out_path=os.path.join(FIG, "exhibit2_pe_band.png"),
        metric_name="P/E (TTM)",
    )


def exhibit3() -> None:
    f = json.load(open(os.path.join(DATA, "nvda_financials.json"), encoding="utf-8"))
    inc = f["financials"]["modules"]["incomeStatementHistory"]
    years = [p["period"][:4] for p in inc]              # fiscal years (ends Jan)
    rev = np.array([p["totalRevenue"] / 1e9 for p in inc])
    net = np.array([p["netIncome"] / 1e9 for p in inc])
    yoy = np.zeros_like(rev)
    yoy[1:] = (rev[1:] - rev[:-1]) / rev[:-1] * 100.0
    financial_trend_chart(
        years, rev, net, yoy,
        title="NVIDIA Corp. — Revenue & Net Income",
        subtitle="Fiscal years ending January (US$B) · bars = absolute, line = YoY growth",
        source=SRC,
        out_path=os.path.join(FIG, "exhibit3_financials.png"),
        unit="US$B",
    )


def exhibit4() -> None:
    # Scenarios anchored to sell-side target distribution (Yahoo: 57 analysts)
    scenarios = [
        {"name": "Bull", "prob": 0.30, "value": 515.0,
         "desc": "AI capex stays hyper-exponential; Blackwell/Rubin sell-through exceeds; hyperscaler ROI holds"},
        {"name": "Base", "prob": 0.45, "value": 327.7,
         "desc": "Analyst consensus target (mean of 57): data-center demand compounds, competition contained"},
        {"name": "Bear", "prob": 0.25, "value": 180.0,
         "desc": "AI spend digestion / export restrictions bite; gross margin compresses; multiple de-rates"},
    ]
    scenario_bar_chart(
        scenarios,
        title="NVIDIA Corp. — 12-Month Scenario Targets",
        subtitle="Probability-weighted target $347 · last price $224 (vs consensus mean $327.7)",
        source="Source: Yahoo Finance analyst targets (n=57); scenario probabilities are illustrative",
        out_path=os.path.join(FIG, "exhibit4_scenario.png"),
        current_price=224.2,
    )


def exhibit5() -> None:
    peers = json.load(open(os.path.join(DATA, "peers.json"), encoding="utf-8"))
    nv = json.load(open(os.path.join(DATA, "nvda_quote.json"), encoding="utf-8"))["quote"]
    peers["NVDA"] = {"forwardPE": nv["forwardPE"]}
    order = ["NVDA", "AMD", "AVGO", "TSM", "INTC", "MSFT"]
    labels = [f"{s} (fwd P/E)" for s in order]
    values = np.array([peers[s]["forwardPE"] for s in order], dtype=float)
    peer_compare_chart(
        labels, values,
        title="Semis & Hyperscalers — Forward P/E Comparison",
        subtitle="NVDA trades at a forward P/E discount to most peers despite fastest growth",
        source="Source: Yahoo Finance forward P/E (as of 2026-09-10)",
        out_path=os.path.join(FIG, "exhibit5_peers.png"),
        xlabel="Forward P/E (x)",
        highlight_idx=0,
    )


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    df = load_history()
    print(f"bars: {len(df)}  {df.index[0].date()} -> {df.index[-1].date()}  last close {df['Close'].iloc[-1]:.2f}")
    exhibit1(df)
    print("exhibit1 OK (kline)")
    exhibit2(df)
    print("exhibit2 OK (pe band)")
    exhibit3()
    print("exhibit3 OK (financials)")
    exhibit4()
    print("exhibit4 OK (scenario)")
    exhibit5()
    print("exhibit5 OK (peers)")
    print("done ->", FIG)
