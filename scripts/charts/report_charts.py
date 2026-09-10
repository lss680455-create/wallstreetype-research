# -*- coding: utf-8 -*-
"""
report_charts.py — Wall Street Research report chart templates.

Five chart templates in the institutional investment-bank visual style
(deep navy, faint grid, clear labels, title + subtitle + data-source footer,
500 dpi PNG, CJK fonts auto-detected via chart_style):

  1. kline_volume_chart   — candlestick + volume + MA + optional MACD (mplfinance)
  2. valuation_band_chart — historical PE/PB corridor with current point
  3. financial_trend_chart— revenue/net-profit bars + YoY growth line (dual axis)
  4. scenario_bar_chart   — base/bull/bear targets with probability-weighted EV
  5. peer_compare_chart   — horizontal industry/peer comparison bars

Every function takes plain data + title/subtitle/source strings and writes a
high-resolution PNG, so downstream docx/PDF tooling can embed the file directly.

Run `python report_charts.py` to regenerate the sample charts in ./sample_pngs/.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import mplfinance as mpf

import chart_style as cs

HERE = Path(__file__).resolve().parent
SAMPLE_DIR = HERE / "sample_pngs"

# ---------------------------------------------------------------------------
# 1) Candlestick + volume + MA + MACD (mplfinance)
# ---------------------------------------------------------------------------
def kline_volume_chart(
    df: pd.DataFrame,
    title: str,
    subtitle: str,
    source: str,
    out_path: str | Path,
    mav: tuple = (5, 10, 20, 60),
    macd: bool = True,
    dpi: int = 500,
    figsize=(11.0, 6.6),
) -> Path:
    """Candlestick chart with volume and moving averages; optional MACD panel.

    df must be indexed by DatetimeIndex with columns
    Open, High, Low, Close, Volume.
    """
    cs.apply_theme()
    df = df.copy().sort_index()
    need = {"Open", "High", "Low", "Close", "Volume"}
    if not need.issubset(df.columns):
        raise ValueError(f"df must contain {need}; got {list(df.columns)}")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.DatetimeIndex(df.index)

    marketcolors = mpf.make_marketcolors(
        up=cs.UP_COLOR, down=cs.DOWN_COLOR,
        edge="inherit", wick="inherit", volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=marketcolors,
        gridstyle="-", gridcolor=cs.GRID, gridaxis="horizontal",
        facecolor="white", figcolor="white",
        rc=cs.theme_rc(),
    )

    aps = []
    panel_ratios = [6, 2]
    if macd:
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        dif = ema12 - ema26                     # MACD line
        dea = dif.ewm(span=9, adjust=False).mean()   # signal line
        hist = dif - dea                        # histogram
        hist_colors = np.where(hist >= 0, cs.UP_COLOR, cs.DOWN_COLOR)
        aps += [
            mpf.make_addplot(hist, type="bar", panel=2, color=hist_colors,
                             alpha=0.55, width=0.8),
            mpf.make_addplot(dif, panel=2, color=cs.NAVY, width=1.2,
                             label="MACD (DIF)"),
            mpf.make_addplot(dea, panel=2, color=cs.GOLD, width=1.2,
                             label="Signal (DEA)"),
        ]
        panel_ratios.append(2)

    fig, axlist = mpf.plot(
        df, type="candle", style=style, volume=True,
        mav=mav, addplot=aps, panel_ratios=panel_ratios,
        figsize=figsize, returnfig=True,
        datetime_format="%m-%d" if len(df) <= 45 else "%Y-%m",
        xrotation=45 if len(df) <= 45 else 0,
        ylabel="Price", ylabel_lower="Volume",
        tight_layout=False,
    )
    ax_main, ax_vol = axlist[0], axlist[1]

    # Leave room for header/footer.
    fig.subplots_adjust(top=0.86, bottom=0.24, left=0.075, right=0.975,
                        hspace=0.22)

    for ax in axlist:
        ax.set_axisbelow(True)
        ax.tick_params(colors=cs.GRAY, labelsize=8)

    # Legend: MAs on main panel (mplfinance already labels them MA5/MA10/...).
    if ax_main.get_legend() is None:
        handles, labels = ax_main.get_legend_handles_labels()
        if labels:
            leg = ax_main.legend(handles, labels, loc="upper left",
                                 ncol=len(labels), fontsize=8, frameon=False,
                                 borderaxespad=0.2)
            for t in leg.get_texts():
                t.set_color(cs.GRAY)

    # MACD legend (proxy handles; deterministic even if mplfinance skips it).
    if macd:
        from matplotlib.lines import Line2D
        ax_macd = axlist[2]
        if ax_macd.get_legend() is None:
            proxies = [
                Line2D([0], [0], color=cs.NAVY, lw=1.2, label="MACD (DIF)"),
                Line2D([0], [0], color=cs.GOLD, lw=1.2, label="Signal (DEA)"),
            ]
            leg = ax_macd.legend(handles=proxies, loc="upper left", ncol=2,
                                 fontsize=8, frameon=False, borderaxespad=0.2)
            for t in leg.get_texts():
                t.set_color(cs.GRAY)

    # Last-close marker on the price panel.
    last = df.iloc[-1]
    x_last = df.index[-1]
    ax_main.axhline(last["Close"], color=cs.GOLD, lw=0.8, ls="--", alpha=0.8)
    ax_main.annotate(
        f"Last close  {last['Close']:.2f}",
        xy=(x_last, last["Close"]),
        xytext=(0.985, 0.965), textcoords="axes fraction",
        ha="right", va="top", fontsize=8.5, color=cs.NAVY_DARK,
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=cs.GOLD, lw=0.8))

    cs.add_header(fig, title, subtitle)
    cs.add_footer(fig, source=source)
    return cs.save_fig(fig, out_path, dpi=dpi)


# ---------------------------------------------------------------------------
# 2) PE/PB valuation band
# ---------------------------------------------------------------------------
def valuation_band_chart(
    dates: list,
    metric: np.ndarray,
    title: str,
    subtitle: str,
    source: str,
    out_path: str | Path,
    metric_name: str = "PE (TTM)",
    band_sigma: float = 1.0,
    dpi: int = 500,
    figsize=(10.5, 5.4),
) -> Path:
    """Historical valuation corridor (max/±1σ/mean/min) + current point.

    metric: historical PE (or PB) series, chronological. The last value is
    treated as the current reading and highlighted with percentile context.
    """
    cs.apply_theme()
    metric = np.asarray(metric, dtype=float)
    n = len(metric)
    x = np.arange(n)

    cur = metric[-1]
    mean_v, sd_v = metric.mean(), metric.std(ddof=1)
    lo, hi = mean_v - band_sigma * sd_v, mean_v + band_sigma * sd_v
    pct = float((metric <= cur).mean() * 100)

    fig, ax = plt.subplots(figsize=figsize)
    cs.style_axes(ax, grid_axis="y")

    # Corridor fill (±1σ) and area under the line.
    ax.fill_between(x, lo, hi, color=cs.NAVY, alpha=0.07, lw=0)
    ax.fill_between(x, metric, mean_v, color=cs.SKY, alpha=0.12, lw=0)
    ax.plot(x, metric, color=cs.NAVY, lw=1.1, zorder=3)

    # Band reference lines.
    bands = [
        (metric.max(),  "Max",       cs.GRAY,      "--"),
        (hi,            f"+{band_sigma:.0f}σ",  cs.NAVY_MID, ":"),
        (mean_v,        "Mean",      cs.NAVY,      "-"),
        (lo,            f"-{band_sigma:.0f}σ",  cs.NAVY_MID, ":"),
        (metric.min(),  "Min",       cs.GRAY,      "--"),
    ]
    for yv, lab, col, ls in bands:
        ax.axhline(yv, color=col, lw=0.9, ls=ls, alpha=0.9)
        ax.text(1.012, yv, f"{lab}  {yv:.1f}x", color=col, fontsize=7,
                ha="left", va="center", transform=ax.get_yaxis_transform())

    # Current point (gold star + dashed level + annotation box).
    ax.scatter([n - 1], [cur], s=190, marker="*", color=cs.GOLD,
               edgecolor="white", linewidth=0.8, zorder=6)
    ax.axhline(cur, color=cs.GOLD, lw=1.0, ls="--", alpha=0.85)
    ax.annotate(
        f"Current {metric_name}: {cur:.1f}x\n"
        f"percentile: P{pct:.0f} ({'above' if cur >= mean_v else 'below'} mean)",
        xy=(n - 1, cur), xytext=(0.10, 0.93), textcoords="axes fraction",
        fontsize=8.5, color=cs.NAVY_DARK, ha="left", va="top",
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=cs.GOLD, lw=0.8))

    # X ticks: ~8 evenly spaced dates.
    step = max(1, n // 8)
    tick_idx = list(range(0, n, step)) + ([n - 1] if (n - 1) % step else [])
    tick_idx = sorted(set(tick_idx))
    ax.set_xticks(tick_idx)
    ax.set_xticklabels([str(dates[i])[:7] for i in tick_idx], fontsize=7.5)

    ax.set_xlim(-0.5, n + 0.9)
    ax.set_ylabel(metric_name, fontsize=8.5, color=cs.GRAY)
    ax.margins(y=0.12)

    cs.add_header(fig, title, subtitle)
    cs.add_footer(fig, source=source)
    return cs.save_fig(fig, out_path, dpi=dpi)


# ---------------------------------------------------------------------------
# 3) Financial trend: bars (revenue / net profit) + YoY line (dual axis)
# ---------------------------------------------------------------------------
def financial_trend_chart(
    years: list,
    revenue: np.ndarray,
    net_profit: np.ndarray,
    yoy_growth: np.ndarray,
    title: str,
    subtitle: str,
    source: str,
    out_path: str | Path,
    unit: str = "RMB 100M (亿CNY)",
    dpi: int = 500,
    figsize=(10.5, 5.4),
) -> Path:
    """Revenue/net-profit grouped bars (left) + revenue YoY growth line (right).

    yoy_growth in percentage points, e.g. 12.5 == +12.5%.
    unit: currency/unit label for the bar axis, e.g. "US$B" or "RMB 100M (亿CNY)".
    """
    cs.apply_theme()
    years = list(years)
    revenue = np.asarray(revenue, dtype=float)
    net_profit = np.asarray(net_profit, dtype=float)
    yoy_growth = np.asarray(yoy_growth, dtype=float)
    x = np.arange(len(years))
    w = 0.38

    fig, ax1 = plt.subplots(figsize=figsize)
    cs.style_axes(ax1, grid_axis="y")

    b1 = ax1.bar(x - w / 2, revenue, width=w, color=cs.NAVY,
                 label=f"Revenue ({unit})", zorder=3)
    b2 = ax1.bar(x + w / 2, net_profit, width=w, color=cs.GOLD,
                 label=f"Net profit ({unit})", zorder=3)

    # Value labels above positive bars, below negative ones.
    lab_pad = max(revenue.max(), 0.01) * 0.012
    for xi, v in zip(x - w / 2, revenue):
        ax1.text(xi, v + (lab_pad if v >= 0 else -lab_pad), f"{v:.1f}", ha="center",
                 va="bottom" if v >= 0 else "top",
                 fontsize=6.8, color=cs.NAVY_DARK)
    for xi, v in zip(x + w / 2, net_profit):
        ax1.text(xi, v + (lab_pad if v >= 0 else -lab_pad), f"{v:.1f}", ha="center",
                 va="bottom" if v >= 0 else "top",
                 fontsize=6.8, color=cs.NAVY_DARK)

    # Left axis must show negative net profit and must not clip the tallest bar.
    lo = min(0.0, float(np.nanmin(net_profit)))
    hi = max(float(np.nanmax(revenue)), float(np.nanmax(net_profit)), 0.01)
    span = hi - lo
    ax1.set_ylim(lo - span * 0.06, hi + span * 0.16)

    # YoY growth on secondary axis.
    ax2 = ax1.twinx()
    ax2.grid(False)
    ax2.plot(x, yoy_growth, color=cs.SKY, lw=1.7, marker="o", ms=4,
             label="Revenue YoY (%)", zorder=4)
    ax2.axhline(0, color=cs.GRAY, lw=0.8, ls="--", alpha=0.7)
    ax2.set_ylabel("Revenue YoY (%)", fontsize=8.5, color=cs.GRAY)
    finite = np.asarray(yoy_growth, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size:
        ymax = max(abs(finite).max() * 1.25, 10.0)
        ymin = min(finite.min() * 1.25, 0.0)
        ax2.set_ylim(ymin - ymax * 0.08, ymax)
    ax2.tick_params(colors=cs.GRAY, labelsize=8)

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{y}" for y in years], fontsize=8)
    ax1.set_ylabel(unit, fontsize=8.5, color=cs.GRAY)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    leg = ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8,
                     frameon=False, ncol=3)
    for t in leg.get_texts():
        t.set_color(cs.TEXT)

    cs.add_header(fig, title, subtitle)
    cs.add_footer(fig, source=source)
    return cs.save_fig(fig, out_path, dpi=dpi)


# ---------------------------------------------------------------------------
# 4) Scenario probability chart (base / bull / bear)
# ---------------------------------------------------------------------------
def scenario_bar_chart(
    scenarios: list[dict],
    title: str,
    subtitle: str,
    source: str,
    out_path: str | Path,
    current_price: float | None = None,
    dpi: int = 500,
    figsize=(10.0, 4.6),
) -> Path:
    """Scenario target prices as horizontal bars with probability-weighted EV.

    scenarios: [{"name": "Bull", "prob": 0.30, "value": 28.5, "desc": "..."}]
    Colors follow convention: bull=green, base=navy, bear=red.
    """
    cs.apply_theme()

    def _scenario_key(name: str) -> int:
        """Map a scenario label to its convention slot.

        Matches English (Bull/Base/Bear) and Chinese (牛市/基准/熊市) labels,
        case-insensitively, so localised reports still get the right colours.
        """
        n = name.lower()
        if "bull" in n or "牛" in n:
            return 0
        if "bear" in n or "熊" in n:
            return 2
        if "base" in n or "neutral" in n or "基准" in n or "中性" in n:
            return 1
        return 9

    sc = sorted(scenarios, key=lambda s: _scenario_key(s["name"]))
    names = [f"{s['name']} · {s['prob'] * 100:.0f}%" for s in sc]
    vals = np.array([s["value"] for s in sc])
    cols = {0: cs.UP_GREEN, 1: cs.NAVY, 2: cs.DOWN_RED}
    colors = [cols.get(_scenario_key(s["name"]), cs.NAVY_MID) for s in sc]

    ev = float(sum(s["prob"] * s["value"] for s in sc))

    fig, ax = plt.subplots(figsize=figsize)
    cs.style_axes(ax, grid_axis="x")

    y = np.arange(len(sc))[::-1]
    ax.barh(y, vals, height=0.58, color=colors, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9, color=cs.TEXT)

    for yi, v, s in zip(y, vals, sc):
        ax.text(v + max(vals) * 0.015, yi, f"{v:.1f}",
                va="center", fontsize=9, color=cs.NAVY_DARK, fontweight="bold")
        if s.get("desc"):
            ax.text(max(vals) * 0.015, yi - 0.32, s["desc"],
                    va="top", fontsize=7.8, color=cs.TEXT, alpha=0.78)

    # Probability-weighted target (EV) and current price reference lines.
    # Both are labelled in the legend rather than inline, so the vertical
    # markers can never collide with the per-bar descriptions.
    ax.axvline(ev, color=cs.GOLD, lw=1.6, ls="--", zorder=4)
    if current_price is not None:
        ax.axvline(current_price, color=cs.GRAY, lw=1.0, ls=":", zorder=4)

    ax.set_xlim(0, max(vals) * 1.22)
    ax.set_ylim(-0.95, len(sc) - 0.25)   # room for per-bar desc text below lowest bar
    ax.set_xlabel("Target price", fontsize=8.5, color=cs.GRAY)

    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    handles = [Patch(facecolor=c, label=f"{s['name']} ({s['prob']*100:.0f}%)")
               for s, c in zip(sc, colors)]
    handles.append(Line2D([0], [0], color=cs.GOLD, lw=1.6, ls="--",
                          label=f"Probability-weighted target {ev:.1f}"))
    if current_price is not None:
        handles.append(Line2D([0], [0], color=cs.GRAY, lw=1.0, ls=":",
                              label=f"Last price {current_price:,.2f}"))
    leg = ax.legend(handles=handles, loc="lower right", fontsize=8,
                    frameon=False, ncol=3)
    for t in leg.get_texts():
        t.set_color(cs.TEXT)

    cs.add_header(fig, title, subtitle)
    cs.add_footer(fig, source=source)
    return cs.save_fig(fig, out_path, dpi=dpi)


# ---------------------------------------------------------------------------
# 5) Industry / peer comparison (horizontal bars)
# ---------------------------------------------------------------------------
def peer_compare_chart(
    labels: list[str],
    values: np.ndarray,
    title: str,
    subtitle: str,
    source: str,
    out_path: str | Path,
    xlabel: str = "",
    highlight_idx: int | None = None,
    median_line: bool = True,
    dpi: int = 500,
    figsize=(10.0, 5.2),
) -> Path:
    """Horizontal comparison bars; highlight_idx marks the subject company."""
    cs.apply_theme()
    labels = list(labels)
    values = np.asarray(values, dtype=float)

    order = np.argsort(values)[::-1]          # descending
    labels_s = [labels[i] for i in order]
    values_s = values[order]
    hi_s = np.where(order == highlight_idx)[0]
    hi_s = int(hi_s[0]) if len(hi_s) else None

    colors = [cs.GOLD if i == hi_s else cs.NAVY_MID for i in range(len(labels_s))]

    fig, ax = plt.subplots(figsize=figsize)
    cs.style_axes(ax, grid_axis="x")

    y = np.arange(len(labels_s))
    ax.barh(y, values_s, height=0.62, color=colors, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels_s, fontsize=9, color=cs.TEXT)

    for yi, v in zip(y, values_s):
        ax.text(v + max(values_s) * 0.012, yi, f"{v:.1f}",
                va="center", fontsize=8.5, color=cs.NAVY_DARK)

    if median_line:
        med = float(np.median(values_s))
        ax.axvline(med, color=cs.GRAY, lw=1.0, ls="--", alpha=0.85, zorder=2)
        ax.text(med, len(labels_s) - 0.10, f"median {med:.1f}", ha="left",
                va="bottom", fontsize=7.5, color=cs.GRAY)

    ax.set_xlim(0, max(values_s) * 1.16)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8.5, color=cs.GRAY)

    cs.add_header(fig, title, subtitle)
    cs.add_footer(fig, source=source)
    return cs.save_fig(fig, out_path, dpi=dpi)


# ---------------------------------------------------------------------------
# Demo runner — regenerates all sample charts with synthetic data
# ---------------------------------------------------------------------------
def _demo_kline_data(n: int = 260, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2025-08-01", periods=n)
    rets = rng.normal(0.0004, 0.018, n)
    rets[180:220] += 0.004                    # a mild rally into year-end
    rets[90:120] -= 0.005                     # a correction window
    close = 100 * np.exp(np.cumsum(rets))
    close = np.maximum(close, 8.0)
    open_ = np.roll(close, 1)
    open_[0] = close[0] * 0.995
    high = np.maximum(open_, close) * (1 + rng.uniform(0.002, 0.02, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.002, 0.02, n))
    vol = rng.integers(8_000_000, 32_000_000, n).astype(float)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol},
        index=dates)


def _demo_pe_series(seed: int = 7) -> tuple[list[str], np.ndarray]:
    rng = np.random.default_rng(seed)
    n = 7 * 52
    pe = 22 + np.cumsum(rng.normal(0, 0.55, n))
    pe = 18 + (pe - pe.min()) / (pe.max() - pe.min()) * 22   # scale 18..40
    pe += np.sin(np.arange(n) / 26) * 1.6
    dates = [dt.date(2019, 9, 1) + dt.timedelta(days=7 * i) for i in range(n)]
    return [d.isoformat() for d in dates], pe


def _demo_financials() -> dict:
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    revenue = [8.6, 9.9, 12.4, 14.1, 15.8, 18.3, 21.2]
    profit = [2.1, 2.5, 3.2, 3.5, 3.9, 4.6, 5.3]
    yoy = [12.4, 15.1, 25.3, 13.7, 12.1, 15.8, 15.8]
    return {"years": years, "revenue": revenue, "profit": profit, "yoy": yoy}


def _demo_scenarios() -> list[dict]:
    return [
        {"name": "Bear", "prob": 0.25, "value": 16.8,
         "desc": "Demand softens; margin back to 2019 levels"},
        {"name": "Base", "prob": 0.45, "value": 21.5,
         "desc": "Share gains continue at current pace"},
        {"name": "Bull", "prob": 0.30, "value": 27.9,
         "desc": "New product cycle accelerates; margin expansion"},
    ]


def _demo_peers() -> tuple[list[str], np.ndarray, int]:
    labels = ["示例公司 (Subject)", "同业A", "同业B", "同业C", "同业D", "同业E"]
    values = np.array([28.4, 24.1, 31.8, 19.6, 22.3, 26.7])
    return labels, values, 0


def make_all_samples(out_dir: str | Path = SAMPLE_DIR, dpi: int = 500) -> list[Path]:
    """Regenerate every sample chart; returns the list of PNG paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    made: list[Path] = []

    src = "数据来源：Wind, 公司公告, 分析师估算（示例数据，仅供演示）"

    # a) K-line + volume + MA + MACD
    df = _demo_kline_data()
    made.append(kline_volume_chart(
        df,
        title="图1 · 示例公司 股价与成交量（日线）",
        subtitle="MA5/10/20/60 · 附MACD · 2025.08-2026.09（示例数据）",
        source=src,
        out_path=out_dir / "01_kline_volume_macd.png",
        dpi=dpi))

    # b) PE valuation band
    dates, pe = _demo_pe_series()
    made.append(valuation_band_chart(
        dates, pe,
        title="图2 · 示例公司 历史PE估值走廊",
        subtitle="2019-2026 周度PE(TTM) · 均值±1σ走廊 · 当前分位（示例数据）",
        source=src,
        out_path=out_dir / "02_pe_valuation_band.png",
        metric_name="PE (TTM, x)",
        dpi=dpi))

    # c) Financial trend
    fin = _demo_financials()
    made.append(financial_trend_chart(
        fin["years"], fin["revenue"], fin["profit"], fin["yoy"],
        title="图3 · 示例公司 营收/净利与同比增速",
        subtitle="2019-2025 年度 · 左轴金额，右轴营收同比（示例数据）",
        source=src,
        out_path=out_dir / "03_financial_trend.png",
        dpi=dpi))

    # d) Scenario probability
    made.append(scenario_bar_chart(
        _demo_scenarios(),
        title="图4 · 情景分析：目标价与概率加权",
        subtitle="Bear 25% / Base 45% / Bull 30% · 概率加权目标价 22.0（示例数据）",
        source=src,
        out_path=out_dir / "04_scenario_probability.png",
        current_price=18.6,
        dpi=dpi))

    # e) Peer comparison
    labels, values, hi = _demo_peers()
    made.append(peer_compare_chart(
        labels, values,
        title="图5 · 行业对比：2026E PE (x)",
        subtitle="示例公司与同业估值对比 · 中位数虚线（示例数据）",
        source=src,
        out_path=out_dir / "05_peer_comparison.png",
        xlabel="2026E PE (x)", highlight_idx=hi,
        dpi=dpi))

    return made


if __name__ == "__main__":
    fam, cjk = cs.load_apply()
    print(f"[report_charts] theme applied, CJK font: {cjk} ({fam})")
    files = make_all_samples()
    for f in files:
        print(f"[report_charts] wrote {f} ({f.stat().st_size / 1024:.0f} KB)")
    print(f"[report_charts] done: {len(files)} sample charts")
