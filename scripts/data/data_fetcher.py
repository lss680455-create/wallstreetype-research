"""
data_fetcher.py — unified entry point for the Wall Street Research data layer.

One command fetches quotes, history, or fundamentals for either market.
Pure Python + requests, no agent/platform dependencies — run it from any
terminal or call it from any script/agent.

Usage (CLI):
    python data_fetcher.py us NVDA quote
    python data_fetcher.py us NVDA history --range 3mo
    python data_fetcher.py us NVDA financials --json
    python data_fetcher.py cn 600519 quote
    python data_fetcher.py cn 600519 history --count 250
    python data_fetcher.py cn 600519 financials --periods 5
    python data_fetcher.py us NVDA all            # quote + history + financials

Usage (library):
    import data_fetcher
    q = data_fetcher.fetch("us", "NVDA", "quote")
    h = data_fetcher.fetch("cn", "600519", "history", count=120)
    f = data_fetcher.fetch("cn", "000001", "financials")

Output format: Python dict (or JSON with --json). Data is returned, never
invented — every field traces to a live API response.

Exit codes: 0 success, 1 no data / fetch failure.
"""
from __future__ import annotations

import argparse
import json
import sys

import get_financials
import get_history
import get_quote
from common import make_session, normalize_symbol

DATA_TYPES = ("quote", "history", "financials", "all")


def fetch(market: str, symbol: str, data_type: str, **kwargs) -> dict:
    """Programmatic entry: market 'us'|'cn' (or None for auto-detect),
    data_type one of quote/history/financials/all."""
    m, canon = normalize_symbol(market, symbol)
    session = make_session()
    result: dict = {"market": m, "symbol": canon, "data_type": data_type}

    if data_type in ("quote", "all"):
        if m == "us":
            crumb = get_quote.get_yahoo_crumb(session)
            result["quote"] = get_quote.fetch_us_quote(session, [canon], crumb)[canon]
        else:
            result["quote"] = get_quote.fetch_cn_quote(session, [canon])[canon]
    if data_type in ("history", "all"):
        if m == "us":
            crumb = get_quote.get_yahoo_crumb(session)
            result["history"] = get_history.fetch_us_history(
                session, canon, crumb,
                interval=kwargs.get("interval", "1d"),
                range_=kwargs.get("range", "1y"),
                include_pre_post=kwargs.get("include_pre_post", True))
        else:
            result["history"] = get_history.fetch_cn_history(
                session, canon,
                period=kwargs.get("period", "day"),
                start=kwargs.get("start", ""), end=kwargs.get("end", ""),
                count=kwargs.get("count", 250), fq=kwargs.get("fq", "qfq"))
    if data_type in ("financials", "all"):
        if m == "us":
            crumb = get_quote.get_yahoo_crumb(session)
            result["financials"] = get_financials.fetch_us_financials(session, canon, crumb)
        else:
            result["financials"] = get_financials.fetch_cn_financials(
                session, canon, periods=kwargs.get("periods", 5))
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Unified market-data fetcher (US + A-share). "
                    "Data is fetched live — nothing is synthesized.")
    ap.add_argument("market", choices=["us", "cn"], help="market: us or cn")
    ap.add_argument("symbol", help="NVDA / 600519 / 000001.SZ / sh600519 ...")
    ap.add_argument("data_type", choices=DATA_TYPES,
                    help="quote | history | financials | all")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    # history options
    ap.add_argument("--range", default="1y", help="US history range (1d..max)")
    ap.add_argument("--interval", default="1d", help="US interval (1d/1wk/1mo/1h)")
    ap.add_argument("--period", choices=["day", "week", "month"], default="day",
                    help="CN period")
    ap.add_argument("--count", type=int, default=250, help="CN bars (default 250)")
    ap.add_argument("--start", default="", help="CN start YYYY-MM-DD")
    ap.add_argument("--end", default="", help="CN end YYYY-MM-DD")
    ap.add_argument("--fq", default="qfq", help="CN adjust: qfq/hfq/'' (default qfq)")
    # financials options
    ap.add_argument("--periods", type=int, default=5, help="CN report periods")
    args = ap.parse_args(argv)

    result = fetch(args.market, args.symbol, args.data_type,
                   range_=args.range, interval=args.interval,
                   period=args.period, count=args.count,
                   start=args.start, end=args.end,
                   fq=args.fq, periods=args.periods)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# {args.market} {args.symbol} -> {result['symbol']}")
        for part in ("quote", "history", "financials"):
            if part in result:
                print(f"# {part}:")
                _preview(result[part], part)
    return 0


def _preview(obj, part: str) -> None:
    if part == "quote":
        q = obj
        if q.get("market") == "cn":
            print(f"  {q.get('name')} price={q.get('price')} PE(TTM)={q.get('pe_ttm')} "
                  f"PB={q.get('pb')} MV(亿)={q.get('total_mv_yi')}")
        else:
            print(f"  {q.get('longName') or q.get('symbol')} price={q.get('regularMarketPrice')} "
                  f"mktCap={q.get('marketCap')} PE={q.get('trailingPE')} PB={q.get('priceToBook')}")
    elif part == "history":
        bars = obj.get("bars", [])
        print(f"  bars={len(bars)}  last={bars[-1]['date'] if bars else 'n/a'}")
        if bars:
            b = bars[-1]
            print(f"  O {b['open']} H {b['high']} L {b['low']} C {b['close']} V {b.get('volume')}")
    elif part == "financials":
        if "datacenter_indicators" in obj:  # CN
            rows = obj["datacenter_indicators"]
            print(f"  CN indicators: {len(rows)} periods, latest {rows[0]['report_date'] if rows else 'n/a'}")
        else:
            rows = obj.get("modules", {}).get("incomeStatementHistory", [])
            print(f"  US income stmts: {len(rows)} periods"
                  + (f", latest revenue {rows[0].get('totalRevenue')}" if rows else ""))


if __name__ == "__main__":
    sys.exit(main())
