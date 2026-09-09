"""
make_case_charts.py — the six exhibits of the 宇树科技 vs 英伟达 case study,
built from REAL data only (data/unitree_all.json, data/nvda_all.json,
data/numbers.json). Five of the six use the repo's institutional chart
families; Exhibit 1 is a bespoke log-scale "magnitude gap" chart drawn with
the same chart_style theme.

Run from the repo root:
    python examples/unitree_vs_nvidia/make_case_charts.py
"""
from __future__ import annotations
import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
FIG = os.path.join(BASE, "figures")
ROOT = os.path.dirname(os.path.dirname(BASE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "charts"))

import chart_style as cs                                        # noqa: E402
from report_charts import (                                     # noqa: E402
    kline_volume_chart, valuation_band_chart, financial_trend_chart,
    scenario_bar_chart, peer_compare_chart,
)

SRC_CN = ("数据来源：上交所公告/招股说明书；腾讯财经、东方财富（688836.SH，2026-09-09 收盘）")
SRC_US = ("数据来源：Yahoo Finance（NVDA，2026-09-09 收盘）；USD/CNY 6.6977（Yahoo，2026-09-09）")
SRC = (SRC_CN + "；" + SRC_US)


def load_numbers() -> dict:
    return json.load(open(os.path.join(DATA, "numbers.json"), encoding="utf-8"))


def load_unitree_history() -> pd.DataFrame:
    d = json.load(open(os.path.join(DATA, "unitree_all.json"), encoding="utf-8"))
    df = pd.DataFrame(d["history"]["bars"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df.sort_index()


# --------------------------------------------------------------------------- #
# Exhibit 1 — magnitude gap (bespoke, log scale)                              #
# --------------------------------------------------------------------------- #
def exhibit1_gap(num: dict) -> None:
    u, n = num["unitree"], num["nvidia"]
    metrics = ["市值", "收入 (TTM)", "净利 (TTM)"]
    # all three series in 十亿元人民币 (bn CNY) so the log axis is unit-consistent
    unitree = [u["market_cap_cny_100m"] / 10, u["rev_ttm_cny_100m"] / 10, u["np_ttm_cny_100m"] / 10]
    nvda = [n["market_cap_cny_tn"] * 1000, n["rev_ttm_cny_tn"] * 1000, n["np_ttm_cny_tn"] * 1000]
    gaps = [num["gaps"]["market_cap_x"], num["gaps"]["revenue_x"], num["gaps"]["net_income_x"]]

    cs.apply_theme()
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    y = np.arange(len(metrics))
    h = 0.34
    ax.barh(y + h / 2, nvda, height=h, color=cs.NAVY_DARK, label="英伟达 (NVDA)")
    ax.barh(y - h / 2, unitree, height=h, color=cs.GOLD, label="宇树科技 (688836.SH)")
    ax.set_yticks(y, metrics, fontproperties=cs.font_prop(11, "bold"))
    ax.set_xscale("log")
    ax.set_xlim(0.2, 2e5)
    ax.set_xlabel("十亿元人民币（对数刻度）", fontproperties=cs.font_prop(9.5))

    def _fmt(v: float) -> str:
        if v >= 1000:
            return f"{v:,.0f}"
        if v >= 100:
            return f"{v:,.0f}"
        if v >= 10:
            return f"{v:,.1f}"
        return f"{v:.3g}"

    for yi, v in zip(y + h / 2, nvda):
        ax.text(v * 1.3, yi, _fmt(v), va="center", fontproperties=cs.font_prop(9, "bold"),
                color=cs.NAVY_DARK)
    for yi, v in zip(y - h / 2, unitree):
        ax.text(v * 1.3, yi, _fmt(v), va="center", fontproperties=cs.font_prop(9, "bold"),
                color="#8A6D00")
    for yi, g in zip(y, gaps):
        ax.text(1.4e5, yi, f"差 {g:,.0f} 倍", va="center", ha="right",
                fontproperties=cs.font_prop(11, "bold"), color=cs.DOWN_RED)
    cs.style_axes(ax, grid_axis="x")
    ax.legend(loc="lower right", frameon=False, prop=cs.font_prop(9.5))
    cs.add_header(fig, "宇树科技 vs 英伟达 — 三个量级上的差距",
                  f"对数刻度；单位：十亿元人民币 · 宇树收入仅相当于英伟达的 "
                  f"{num['gaps']['unitree_rev_share_of_nvda_pct']}%")
    cs.add_footer(fig, source=SRC)
    cs.save_fig(fig, os.path.join(FIG, "exhibit1_gap.png"))
    print("[ok] exhibit1_gap.png")


# --------------------------------------------------------------------------- #
# Exhibit 2 — Unitree K-line since listing                                    #
# --------------------------------------------------------------------------- #
def exhibit2_kline() -> None:
    df = load_unitree_history()
    kline_volume_chart(
        df,
        title="宇树科技 (688836.SH) — 上市以来价格与成交量",
        subtitle=f"日线，{len(df)} 个交易日（2026-08-19 上市）· 均线 3/5 · 上市 16 日累计 −53%",
        source=SRC_CN,
        out_path=os.path.join(FIG, "exhibit2_kline.png"),
        mav=(3, 5), macd=False,
        figsize=(10.5, 5.0),
    )
    print("[ok] exhibit2_kline.png")


# --------------------------------------------------------------------------- #
# Exhibit 3 — NVIDIA 1Y P/E corridor (the yardstick)                          #
# --------------------------------------------------------------------------- #
def exhibit3_pe_band(num: dict) -> None:
    d = json.load(open(os.path.join(DATA, "nvda_all.json"), encoding="utf-8"))
    df = pd.DataFrame(d["history"]["bars"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    eps = 7.90                                     # Yahoo trailing EPS
    pe = (df["close"].astype(float) / eps).values
    valuation_band_chart(
        [x.strftime("%Y-%m-%d") for x in df.index], pe,
        title="标尺 — 英伟达 1 年估值走廊",
        subtitle=f"市盈率（TTM，EPS $7.90）· 区间 = 均值 ±1σ · 当前 {num['nvidia']['trailing_pe']}x",
        source=SRC_US,
        out_path=os.path.join(FIG, "exhibit3_pe_band.png"),
        metric_name="P/E (TTM)",
    )
    print("[ok] exhibit3_pe_band.png")


# --------------------------------------------------------------------------- #
# Exhibit 4 — Unitree revenue / net income                                    #
# --------------------------------------------------------------------------- #
def exhibit4_financials(num: dict) -> None:
    u = num["unitree"]
    years = ["FY2022", "FY2023", "FY2024", "FY2025"]
    rev = np.array([u["fy2022_rev_cny_100m"], u["fy2023_rev_cny_100m"],
                    u["fy2024_rev_cny_100m"], u["fy2025_rev_cny_100m"]])
    np_ = np.array([u["fy2022_np_cny_100m"], u["fy2023_np_cny_100m"],
                    u["fy2024_np_cny_100m"], u["fy2025_np_cny_100m"]])
    yoy = np.array([np.nan, u["fy2023_rev_yoy_pct"], u["fy2024_rev_yoy_pct"],
                    u["fy2025_rev_yoy_pct"]])
    financial_trend_chart(
        years, rev, np_, yoy,
        title="宇树科技 — 营业收入与净利润",
        subtitle=(f"单位：亿元人民币（柱）· 收入同比增速（线，%）· "
                  f"TTM 收入 ¥{u['rev_ttm_cny_100m']:.2f} 亿、净利 ¥{u['np_ttm_cny_100m']:.2f} 亿"),
        source=SRC_CN,
        out_path=os.path.join(FIG, "exhibit4_financials.png"),
        unit="亿元人民币",
    )
    print("[ok] exhibit4_financials.png")


# --------------------------------------------------------------------------- #
# Exhibit 5 — 12-month scenario tree                                          #
# --------------------------------------------------------------------------- #
def exhibit5_scenarios() -> None:
    scenarios = [
        {"name": "牛市 (Bull)", "prob": 0.25, "value": 800.0,
         "desc": "世界模型驱动全自主作业落地；2026 出货 1.5 万台；扣非重回高增；解禁冲击被增量资金消化"},
        {"name": "基准 (Base)", "prob": 0.50, "value": 560.0,
         "desc": "2026E 收入约 26 亿元（+53%），扣非约 6 亿元；P/S 回落至 87x 但仍是行业顶端"},
        {"name": "熊市 (Bear)", "prob": 0.25, "value": 340.0,
         "desc": "价格战使主营毛利率跌破 50%；智元等竞品份额继续蚕食；2027 年 8 月解禁前估值先行下移"},
    ]
    scenario_bar_chart(
        scenarios,
        title="宇树科技 — 12 个月情景与目标价",
        subtitle="概率加权目标价 ¥565 · 现价 ¥513.93（2026-09-09 收盘）",
        source="数据来源：现价取自腾讯财经；情景概率与目标价为本文方法示范，非投资建议",
        out_path=os.path.join(FIG, "exhibit5_scenario.png"),
        current_price=513.93,
    )
    print("[ok] exhibit5_scenario.png")


# --------------------------------------------------------------------------- #
# Exhibit 6 — catch-up timetable                                              #
# --------------------------------------------------------------------------- #
def exhibit6_catchup(num: dict) -> None:
    c = num["catch_up_years"]
    labels = [f"若收入年增 {k}" for k in ("100%", "60%", "48%", "30%", "20%")]
    values = np.array([c["100%"], c["60%"], c["48%"], c["30%"], c["20%"]], dtype=float)
    peer_compare_chart(
        labels, values,
        title="追上英伟达今天收入水平，需要多少年？",
        subtitle="以宇树 TTM 收入 ¥20.76 亿为起点，英伟达 TTM 收入 ¥2.03 万亿为终点（英伟达保持零增长）；黄色为 60% 增速的基准情景",
        source=SRC,
        out_path=os.path.join(FIG, "exhibit6_catchup.png"),
        xlabel="所需年数",
        highlight_idx=1,
        median_line=False,
    )
    print("[ok] exhibit6_catchup.png")


# --------------------------------------------------------------------------- #
# Cover price chart                                                           #
# --------------------------------------------------------------------------- #
def cover_price_chart() -> None:
    df = load_unitree_history()
    cs.apply_theme()
    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    ax.plot(df.index, df["Close"], color=cs.NAVY_MID, lw=1.6)
    ax.fill_between(df.index, df["Close"], df["Close"].min() * 0.97,
                    color=cs.NAVY_MID, alpha=0.10)
    lo, hi = float(df["Close"].min()), float(df["Close"].max())
    ax.set_ylim(lo * 0.965, hi * 1.045)
    ax.text(df.index[0], hi * 1.012,
            f"纵轴自 ¥{lo:,.2f}（区间低点）起 · 发行价 ¥150.80，现价 {df['Close'].iloc[-1] / 150.80:.2f}×",
            fontproperties=cs.font_prop(7.5), color="#8A6D00", va="bottom")
    ax.scatter([df.index[-1]], [df["Close"].iloc[-1]], color=cs.DOWN_RED, s=22, zorder=5)
    ax.annotate(f"¥{df['Close'].iloc[-1]:,.2f}", (df.index[-1], df["Close"].iloc[-1]),
                textcoords="offset points", xytext=(-46, 8),
                fontproperties=cs.font_prop(8, "bold"), color=cs.DOWN_RED)
    ax.set_ylabel("元/股", fontproperties=cs.font_prop(8))
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(cs.font_prop(7.5))
    cs.style_axes(ax, grid_axis="y")
    fig.tight_layout()
    cs.save_fig(fig, os.path.join(FIG, "cover_price.png"), dpi=300)
    print("[ok] cover_price.png")


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    num = load_numbers()
    exhibit1_gap(num)
    exhibit2_kline()
    exhibit3_pe_band(num)
    exhibit4_financials(num)
    exhibit5_scenarios()
    exhibit6_catchup(num)
    cover_price_chart()
    print("done ->", FIG)
