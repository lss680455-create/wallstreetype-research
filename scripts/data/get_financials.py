"""
get_financials.py — fundamental financial indicators for US and A-share.

Sources:
  * US : Yahoo Finance v10 /quoteSummary (cookie + crumb; SOCKS5 proxy).
         Modules: incomeStatementHistory (revenue/net income per period),
         balanceSheetHistory, cashflowStatementHistory, financialData
         (margins, ROE, ROA, analyst targets), defaultKeyStatistics (EPS,
         book value, ROE, payout ratio).
  * CN : Eastmoney datacenter RPT_LICO_FN_CPD (业绩核心指标, per REPORTDATE:
         营收/归母净利/扣非EPS/毛利率/加权ROE/同比增速/BPS) — the host
         datacenter.eastmoney.com is reachable directly from mainland China
         (push2/push2his hosts are NOT — see README).
         Plus F10 主要指标 (emweb.securities.eastmoney.com ZYZBAjaxNew) with
         per-period EPS(基本/扣非/稀释), BPS, 每股公积/未分配利润/经营现金流,
         营收, 毛利率, 归母净利, 扣非净利, 同比增速.

Usage:
    python get_financials.py NVDA                 # US income/balance/cashflow
    python get_financials.py NVDA --modules financialData
    python get_financials.py 600519               # A-share key indicators
    python get_financials.py 000001.SZ --periods 6
    python get_financials.py NVDA --json

Notes:
  * US revenue/profit units are raw currency units (USD); CN units are raw CNY.
  * CN datacenter filter uses SECURITY_CODE (no exchange suffix) and MUST sort
    by UPDATE_DATE (sorting by REPORT_DATE returns error code 9501).
  * DEDUCT_BASIC_EPS (扣非EPS) is often null for Q1 reports — only filled for
    半年报/年报 in many cases (documented pitfall).
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from common import (YAHOO_RATE_LIMIT_SLEEP, get_yahoo_crumb, make_session,
                    normalize_symbol, yahoo_get)

# ---------------------------------------------------------------------------
# US: Yahoo quoteSummary
# ---------------------------------------------------------------------------
QUOTE_SUMMARY_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"

_FIN_MODULES = [
    "incomeStatementHistory", "balanceSheetHistory", "cashflowStatementHistory",
    "financialData", "defaultKeyStatistics",
]


def _raw(x):
    """Unwrap Yahoo's {'raw':..., 'fmt':...} envelope -> raw number (or None)."""
    if isinstance(x, dict):
        return x.get("raw")
    return x


def _date(x):
    """Unwrap Yahoo date envelopes ({raw: epoch, fmt: '2026-01-31'}) -> 'YYYY-MM-DD'."""
    if isinstance(x, dict):
        return x.get("fmt")
    return x


def fetch_us_financials(session, symbol: str, crumb: str,
                        modules: list[str] | None = None) -> dict:
    mods = modules or _FIN_MODULES
    data = yahoo_get(session, QUOTE_SUMMARY_URL.format(symbol=symbol),
                     params={"modules": ",".join(mods)}, crumb=crumb)
    q = data["quoteSummary"]["result"][0]
    out: dict = {"symbol": symbol, "modules": {}}

    def hist(key):
        rows = q.get(key, {}).get(key, [])  # inner list key == module name
        out["modules"][key] = []
        for r in rows:
            rec = {"period": _date(r.get("endDate"))}
            for k, v in r.items():
                if k != "endDate":
                    rec[k] = _raw(v)
            out["modules"][key].append(rec)

    if "incomeStatementHistory" in mods:
        hist("incomeStatementHistory")
    if "balanceSheetHistory" in mods:
        hist("balanceSheetHistory")
    if "cashflowStatementHistory" in mods:
        hist("cashflowStatementHistory")
    if "financialData" in mods and "financialData" in q:
        fd = q["financialData"]
        keep = ["currentPrice", "targetMeanPrice", "targetHighPrice", "targetLowPrice",
                "recommendationMean", "recommendationKey", "numberOfAnalystOpinions",
                "profitMargins", "grossMargins", "operatingMargins", "returnOnEquity",
                "returnOnAssets", "revenueGrowth", "earningsGrowth", "totalRevenue",
                "netIncomeToCommon", "freeCashflow", "dividendYield", "payoutRatio"]
        out["modules"]["financialData"] = {k: _raw(fd.get(k)) for k in keep if k in fd}
    if "defaultKeyStatistics" in mods and "defaultKeyStatistics" in q:
        dk = q["defaultKeyStatistics"]
        keep = ["trailingEps", "forwardEps", "bookValue", "priceToBook",
                "trailingPE", "forwardPE", "returnOnEquity", "payoutRatio",
                "dividendYield", "beta", "sharesOutstanding", "enterpriseValue"]
        out["modules"]["defaultKeyStatistics"] = {k: _raw(dk.get(k)) for k in keep if k in dk}
    return out


# ---------------------------------------------------------------------------
# CN: Eastmoney datacenter (RPT_LICO_FN_CPD) + F10 主要指标
# ---------------------------------------------------------------------------
DATACENTER_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
F10_URL = ("https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/"
           "ZYZBAjaxNew?type=1&code={code}")


def fetch_cn_financials(session, tencent_code: str, periods: int = 5) -> dict:
    """tencent_code like 'sh600519'; periods = number of report periods."""
    code6 = tencent_code[2:]          # strip sh/sz/bj
    f10_code = tencent_code.upper()   # SH600519 form for emweb

    # 1) datacenter 业绩核心指标 — sort MUST be UPDATE_DATE
    params = {
        "reportName": "RPT_LICO_FN_CPD", "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code6}")',
        "pageNumber": 1, "pageSize": periods,
        "sortTypes": -1, "sortColumns": "UPDATE_DATE",
        "source": "HSF10", "client": "PC",
    }
    r = session.get(DATACENTER_URL, params=params, timeout=15,
                    headers={"Referer": "https://emweb.securities.eastmoney.com/"})
    r.raise_for_status()
    dcp = r.json()
    rows1 = []
    if dcp.get("success") and dcp.get("result"):
        for row in dcp["result"]["data"]:
            rows1.append({
                "report_date": str(row.get("REPORTDATE", ""))[:10],
                "revenue": row.get("TOTAL_OPERATE_INCOME"),
                "net_profit_parent": row.get("PARENT_NETPROFIT"),
                "eps_basic": row.get("BASIC_EPS"),
                "eps_deducted": row.get("DEDUCT_BASIC_EPS"),
                "gross_margin_pct": row.get("XSMLL"),
                "roe_weighted_pct": row.get("WEIGHTAVG_ROE"),
                "revenue_yoy_pct": row.get("YSTZ"),
                "net_profit_yoy_pct": row.get("SJLTZ"),
                "bps": row.get("BPS"),
            })

    # 2) F10 主要指标 — richer per-period fields
    r2 = session.get(F10_URL.format(code=f10_code), timeout=15,
                     headers={"Referer": "https://emweb.securities.eastmoney.com/"})
    r2.raise_for_status()
    rows2 = []
    data2 = r2.json().get("data") or []
    for row in data2[:periods]:
        rows2.append({
            "report_date": str(row.get("REPORT_DATE", ""))[:10],
            "report_name": row.get("REPORT_DATE_NAME"),
            "eps_basic": row.get("EPSJB"), "eps_deducted": row.get("EPSKCJB"),
            "eps_diluted": row.get("EPSXS"), "bps": row.get("BPS"),
            "cap_reserve_ps": row.get("MGZBGJ"),        # 每股资本公积
            "undist_profit_ps": row.get("MGWFPLR"),     # 每股未分配利润
            "op_cashflow_ps": row.get("MGJYXJJE"),      # 每股经营现金流
            "revenue": row.get("TOTALOPERATEREVE"),
            "gross_profit": row.get("MLR"),              # 毛利(元) — NOT a percentage!
            "net_profit_parent": row.get("PARENTNETPROFIT"),
            "deducted_net_profit": row.get("KCFJCXSYJLR"),  # 扣非归母净利
            "revenue_yoy_pct": row.get("TOTALOPERATEREVETZ"),
            "net_profit_yoy_pct": row.get("PARENTNETPROFITTZ"),
        })

    return {"symbol": tencent_code,
            "name": rows2[0].get("report_name") if rows2 else None,
            "datacenter_indicators": rows1,
            "f10_main_indicators": rows2}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fundamental financial indicators (US + A-share)")
    ap.add_argument("symbol", help="e.g. NVDA, 600519, 000001.SZ")
    ap.add_argument("--market", choices=["us", "cn"], default=None)
    ap.add_argument("--modules", default=",".join(_FIN_MODULES),
                    help="US quoteSummary modules (comma-separated)")
    ap.add_argument("--periods", type=int, default=5, help="CN report periods (default 5)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    market, canon = normalize_symbol(args.market, args.symbol)
    session = make_session()

    if market == "us":
        crumb = get_yahoo_crumb(session)
        if args.json:
            out = fetch_us_financials(session, canon, crumb,
                                      modules=[m for m in args.modules.split(",") if m])
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return 0
        out = fetch_us_financials(session, canon, crumb,
                                  modules=["incomeStatementHistory", "financialData",
                                           "defaultKeyStatistics"])
        print(f"# {canon} — Yahoo quoteSummary")
        for stmt in ("incomeStatementHistory", "balanceSheetHistory", "cashflowStatementHistory"):
            rows = out["modules"].get(stmt, [])
            if not rows:
                continue
            print(f"\n## {stmt} (latest 3 periods)")
            for r in rows[:3]:
                print(f"  {r.get('period')}  revenue={r.get('totalRevenue'):,.0f}  "
                      f"netIncome={r.get('netIncome'):,.0f}" if r.get('totalRevenue') is not None
                      else f"  {r.get('period')}  {r}")
        fd = out["modules"].get("financialData", {})
        if fd:
            print("\n## financialData")
            for k, v in fd.items():
                if v is not None:
                    print(f"  {k}: {v:,.2f}" if isinstance(v, (int, float)) else f"  {k}: {v}")
        dk = out["modules"].get("defaultKeyStatistics", {})
        if dk:
            print("\n## defaultKeyStatistics")
            for k, v in dk.items():
                if v is not None:
                    print(f"  {k}: {v:,.2f}" if isinstance(v, (int, float)) else f"  {k}: {v}")
        return 0

    # CN
    if args.json:
        out = fetch_cn_financials(session, canon, periods=args.periods)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    out = fetch_cn_financials(session, canon, periods=args.periods)
    print(f"# {canon} — Eastmoney datacenter RPT_LICO_FN_CPD (业绩核心指标)")
    print(f"  {'report_date':<12}{'营收(元)':>16}{'归母净利(元)':>18}{'EPS':>8}"
          f"{'扣非EPS':>9}{'毛利率%':>9}{'加权ROE%':>9}{'营收YoY%':>9}{'净利YoY%':>9}")
    for r in out["datacenter_indicators"]:
        print(f"  {r['report_date']:<12}{r['revenue'] or 0:>16,.0f}{r['net_profit_parent'] or 0:>18,.0f}"
              f"{r['eps_basic'] or 0:>8.2f}{r['eps_deducted'] or 0:>9.2f}"
              f"{r['gross_margin_pct'] or 0:>9.2f}{r['roe_weighted_pct'] or 0:>9.2f}"
              f"{r['revenue_yoy_pct'] or 0:>9.2f}{r['net_profit_yoy_pct'] or 0:>9.2f}")
    print(f"\n# F10 主要指标 ({canon.upper()})")
    for r in out["f10_main_indicators"]:
        print(f"  {r['report_date']} {r['report_name']}  EPS {r['eps_basic']}  "
              f"扣非EPS {r['eps_deducted']}  BPS {r['bps']:.2f}  "
              f"营收 {r['revenue']:,.0f} 毛利 {r['gross_profit']:,.0f}  "
              f"归母 {r['net_profit_parent']:,.0f} 扣非 {r['deducted_net_profit']:,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
