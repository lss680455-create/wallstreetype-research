"""
compute_numbers.py — every number in the 宇树 vs 英伟达 case study, computed
from REAL fetched data. Nothing here is hand-typed.

Inputs  : data/unitree_all.json  (Tencent + Eastmoney, CN)
          data/nvda_all.json     (Yahoo Finance, US, via SOCKS5)
Outputs : data/numbers.json      (consumed by make_case_charts.py and report.md)

Run from the repo root:
    python examples/unitree_vs_nvidia/compute_numbers.py
"""
from __future__ import annotations
import json
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# USD/CNY spot, fetched live from Yahoo Finance (CNY=X) on 2026-09-09.
FX_USDCNY = 6.6977

UNITREE_SHARES = 404_464_340          # post-IPO total share count (上市公告书)
ISSUE_PRICE = 150.80                  # IPO issue price, CNY/share
DAY1_OPEN = 1100.00                   # 2026-08-19 first trade


def _f10(unitree: dict) -> dict:
    return {r["report_date"]: r for r in unitree["financials"]["f10_main_indicators"]}


def _dc(unitree: dict) -> dict:
    return {r["report_date"]: r for r in unitree["financials"]["datacenter_indicators"]}


def main() -> dict:
    u = json.load(open(os.path.join(DATA, "unitree_all.json"), encoding="utf-8"))
    n = json.load(open(os.path.join(DATA, "nvda_all.json"), encoding="utf-8"))
    uq, nq = u["quote"], n["quote"]
    nfd = n["financials"]["modules"]["financialData"]
    f10, dc = _f10(u), _dc(u)

    # ---- Unitree, trailing twelve months (FY2025 + H1-26 - H1-25) -------------
    rev_ttm = (f10["2025-12-31"]["revenue"]
               + dc["2026-06-30"]["revenue"] - dc["2025-06-30"]["revenue"])
    np_ttm = (f10["2025-12-31"]["net_profit_parent"]
              + dc["2026-06-30"]["net_profit_parent"] - dc["2025-06-30"]["net_profit_parent"])
    mkt_u_cny = uq["price"] * UNITREE_SHARES

    # ---- NVIDIA -------------------------------------------------------------
    mkt_n_usd = nq["marketCap"]
    rev_n_usd = nfd["totalRevenue"]
    np_n_usd = nq["regularMarketPrice"] / nq["trailingPE"] * nq["sharesOutstanding"]

    mkt_n_cny = mkt_n_usd * FX_USDCNY
    rev_n_cny = rev_n_usd * FX_USDCNY
    np_n_cny = np_n_usd * FX_USDCNY

    gap_mkt = mkt_n_cny / mkt_u_cny
    gap_rev = rev_n_cny / rev_ttm
    gap_np = np_n_cny / np_ttm

    # ---- how long until Unitree catches up? ---------------------------------
    catch_up = {f"{int(g*100)}%": round(math.log(gap_rev) / math.log(1 + g), 1)
                for g in (1.00, 0.60, 0.485, 0.30, 0.20)}

    # ---- market-cap parity via earnings (assume terminal P/E, net margin) ----
    parity = {}
    for pe in (20, 30, 40):
        need_ni = mkt_n_cny / pe
        for nm in (0.20, 0.30):
            need_rev = need_ni / nm
            parity[f"PE{pe}_NM{int(nm*100)}"] = {
                "need_net_income_cny_tn": round(need_ni / 1e12, 2),
                "need_revenue_cny_tn": round(need_rev / 1e12, 2),
                "x_today_revenue": round(need_rev / rev_ttm, 0),
                "years_at_60pct": round(math.log(need_rev / rev_ttm) / math.log(1.6), 1),
            }

    out = {
        "as_of": {"unitree_quote": uq["datetime"], "fx_usd_cny": FX_USDCNY},
        "unitree": {
            "ticker": "688836.SH", "name": "宇树科技-W",
            "price_cny": uq["price"], "prev_close": uq["prev_close"],
            "change_pct": uq["change_pct"], "market_cap_cny_100m": uq["total_mv_yi"],
            "market_cap_cny_bn": round(mkt_u_cny / 1e9, 2),
            "market_cap_usd_bn": round(mkt_u_cny / FX_USDCNY / 1e9, 2),
            "shares_total": UNITREE_SHARES,
            "pe_ttm": uq["pe_ttm"], "pb": uq["pb"],
            "ps_ttm": round(mkt_u_cny / rev_ttm, 1),
            "pe_ttm_on_ttm_np": round(mkt_u_cny / np_ttm, 1),
            "rev_ttm_cny_100m": round(rev_ttm / 1e8, 2),
            "np_ttm_cny_100m": round(np_ttm / 1e8, 2),
            "wk52_high": uq["wk52_high"], "wk52_low": uq["wk52_low"],
            "issue_price": ISSUE_PRICE, "day1_open": DAY1_OPEN,
            "x_issue_price": round(uq["price"] / ISSUE_PRICE, 2),
            "pct_from_day1_open": round((uq["price"] / DAY1_OPEN - 1) * 100, 1),
            "turnover_pct": uq["turnover_rate_pct"],
            "float_mv_cny_100m": uq["float_mv_yi"],
            "fy2022_rev_cny_100m": round(f10["2022-12-31"]["revenue"] / 1e8, 2),
            "fy2022_np_cny_100m": round(f10["2022-12-31"]["net_profit_parent"] / 1e8, 2),
            "fy2023_rev_cny_100m": round(f10["2023-12-31"]["revenue"] / 1e8, 2),
            "fy2023_np_cny_100m": round(f10["2023-12-31"]["net_profit_parent"] / 1e8, 2),
            "fy2023_rev_yoy_pct": round(f10["2023-12-31"]["revenue_yoy_pct"], 1),
            "fy2024_rev_cny_100m": round(f10["2024-12-31"]["revenue"] / 1e8, 2),
            "fy2024_np_cny_100m": round(f10["2024-12-31"]["net_profit_parent"] / 1e8, 2),
            "fy2024_rev_yoy_pct": round(f10["2024-12-31"]["revenue_yoy_pct"], 1),
            "fy2025_rev_cny_100m": round(f10["2025-12-31"]["revenue"] / 1e8, 2),
            "fy2025_np_cny_100m": round(f10["2025-12-31"]["net_profit_parent"] / 1e8, 2),
            "fy2025_deducted_np_cny_100m": round(f10["2025-12-31"]["deducted_net_profit"] / 1e8, 2),
            "fy2025_gm_pct": round(f10["2025-12-31"]["gross_profit"] / f10["2025-12-31"]["revenue"] * 100, 1),
            "fy2025_rev_yoy_pct": round(f10["2025-12-31"]["revenue_yoy_pct"], 1),
            "h1_2026_rev_cny_100m": round(dc["2026-06-30"]["revenue"] / 1e8, 2),
            "h1_2026_rev_yoy_pct": round(dc["2026-06-30"]["revenue_yoy_pct"], 1),
            "h1_2026_np_cny_100m": round(dc["2026-06-30"]["net_profit_parent"] / 1e8, 2),
            "h1_2026_gm_pct": round(dc["2026-06-30"]["gross_margin_pct"], 1),
            "rev_cagr_23_25_pct": round(((f10["2025-12-31"]["revenue"] / f10["2023-12-31"]["revenue"]) ** 0.5 - 1) * 100, 1),
        },
        "nvidia": {
            "ticker": "NVDA", "price_usd": nq["regularMarketPrice"],
            "market_cap_usd_tn": round(mkt_n_usd / 1e12, 2),
            "market_cap_cny_tn": round(mkt_n_cny / 1e12, 2),
            "rev_ttm_usd_bn": round(rev_n_usd / 1e9, 2),
            "rev_ttm_cny_tn": round(rev_n_cny / 1e12, 2),
            "np_ttm_usd_bn": round(np_n_usd / 1e9, 1),
            "np_ttm_cny_tn": round(np_n_cny / 1e12, 2),
            "trailing_pe": round(nq["trailingPE"], 1), "forward_pe": round(nq["forwardPE"], 1),
            "ps_ttm": round(mkt_n_usd / rev_n_usd, 1),
            "net_margin_pct": round(nfd["profitMargins"] * 100, 1),
            "rev_growth_pct": round(nfd["revenueGrowth"] * 100, 1),
            "target_mean": nfd["targetMeanPrice"], "target_high": nfd["targetHighPrice"],
            "target_low": nfd["targetLowPrice"], "n_analysts": nfd["numberOfAnalystOpinions"],
        },
        "gaps": {
            "market_cap_x": round(gap_mkt, 0),
            "revenue_x": round(gap_rev, 0),
            "net_income_x": round(gap_np, 0),
            "price_to_match_mktcap_cny": round(uq["price"] * gap_mkt, 0),
            "unitree_rev_share_of_nvda_pct": round(rev_ttm / rev_n_cny * 100, 3),
        },
        "catch_up_years": catch_up,
        "mktcap_parity": parity,
    }
    path = os.path.join(DATA, "numbers.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[ok] {path}")
    print(json.dumps({k: out[k] for k in ("gaps", "catch_up_years")}, ensure_ascii=False, indent=1))
    return out


if __name__ == "__main__":
    main()
