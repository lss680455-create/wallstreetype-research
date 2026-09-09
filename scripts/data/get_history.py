"""
get_history.py — historical OHLCV bars (front-adjusted) for US and A-share.

Sources:
  * US : Yahoo Finance v8 /chart API (cookie session, SOCKS5 proxy).
         includePrePost=true returns pre/post-market bars around the latest
         session and meta.preMarketPrice / meta.postMarketPrice.
         Default range='1y', interval='1d'. Adjusted close is in adjclose[].
  * CN : Tencent web.ifzq.gtimg.cn/appstock/app/fqkline/get.
         fq='qfq' (前复权, front-adjusted) is default — the close values ARE
         already adjusted; volume unit is 手 (100 shares).
         No proxy needed.

Usage:
    python get_history.py NVDA                      # US, 1y daily
    python get_history.py NVDA --range 3mo          # US daily range
    python get_history.py NVDA --interval 1wk       # weekly
    python get_history.py 600519                    # A-share, 250 bars, 前复权
    python get_history.py 600519 --start 2024-01-01 --end 2024-12-31
    python get_history.py 000001.SZ --period week
    python get_history.py NVDA --csv out.csv        # save CSV
    python get_history.py NVDA --json               # machine-readable

Output columns: date, open, high, low, close, adj_close(US), volume
US bars carry a 'session' tag of 'pre' | 'regular' | 'post' for the most
recent day when includePrePost=true.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from common import (YAHOO_RATE_LIMIT_SLEEP, get_yahoo_crumb, make_session,
                    normalize_symbol, yahoo_get)

# Yahoo exchange timezone names -> IANA zones (for intraday bar timestamps)
_TZ = {
    "America/New_York": ZoneInfo("America/New_York"),
    "America/Chicago": ZoneInfo("America/Chicago"),
    "America/Denver": ZoneInfo("America/Denver"),
    "America/Los_Angeles": ZoneInfo("America/Los_Angeles"),
    "Europe/London": ZoneInfo("Europe/London"),
    "Asia/Shanghai": ZoneInfo("Asia/Shanghai"),
    "Asia/Hong_Kong": ZoneInfo("Asia/Hong_Kong"),
    "Asia/Tokyo": ZoneInfo("Asia/Tokyo"),
    "Europe/Amsterdam": ZoneInfo("Europe/Amsterdam"),
    "UTC": timezone.utc,
}

# ---------------------------------------------------------------------------
# US: Yahoo v8 chart
# ---------------------------------------------------------------------------
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


def fetch_us_history(session, symbol: str, crumb: str, interval: str = "1d",
                     range_: str = "1y", include_pre_post: bool = True) -> dict:
    """Return {meta: {...}, bars: [{date, open, high, low, close, adj_close,
    volume, session}]}."""
    data = yahoo_get(
        session,
        YAHOO_CHART_URL.format(symbol=symbol),
        params={"interval": interval, "range": range_,
                "includePrePost": "true" if include_pre_post else "false"},
        crumb=crumb,
    )
    res = data["chart"]["result"][0]
    meta = res["meta"]
    ts = res.get("timestamp") or []
    q = res["indicators"]["quote"][0]
    adj = None
    if "adjclose" in res["indicators"] and res["indicators"]["adjclose"]:
        adj = res["indicators"]["adjclose"][0].get("adjclose") or [None] * len(ts)

    # Distinguish pre/regular/post sessions. For daily bars Yahoo appends
    # pre & post bars around the latest session; session boundaries come from
    # meta.currentTradingPeriod if present.
    session_tag = {}
    if include_pre_post and interval in ("1d", "1h", "15m", "5m", "1m") and meta.get("currentTradingPeriod"):
        pre, reg, post = (meta["currentTradingPeriod"].get(k, {}) for k in ("pre", "regular", "post"))
        pre_start, pre_end = pre.get("start"), pre.get("end")
        reg_start, reg_end = reg.get("start"), reg.get("end")
        post_start, post_end = post.get("start"), post.get("end")
        for t in ts:
            if reg_start is not None and reg_start <= t < reg_end:
                session_tag[t] = "regular"
            elif pre_start is not None and pre_start <= t < pre_end:
                session_tag[t] = "pre"
            elif post_start is not None and post_start <= t < post_end:
                session_tag[t] = "post"
            else:
                session_tag[t] = "regular"

    bars = []
    tz = _TZ.get(meta.get("exchangeTimezoneName", ""))  # e.g. America/New_York
    for i, t in enumerate(ts):
        dt = datetime.fromtimestamp(t, tz=tz or timezone.utc)
        # daily+ bars -> calendar date; intraday bars -> local HH:MM
        date_s = dt.strftime("%Y-%m-%d") if interval in ("1d", "1wk", "1mo") \
            else dt.strftime("%Y-%m-%d %H:%M")
        bars.append({
            "date": date_s,
            "open": q["open"][i], "high": q["high"][i], "low": q["low"][i],
            "close": q["close"][i], "volume": q["volume"][i],
            "adj_close": adj[i] if adj else None,
            "session": session_tag.get(t, "regular"),
        })
    m = {k: meta.get(k) for k in ("symbol", "currency", "regularMarketPrice",
                                  "regularMarketPreviousClose", "fiftyTwoWeekHigh",
                                  "fiftyTwoWeekLow", "longName", "exchangeName",
                                  "preMarketPrice", "postMarketPrice",
                                  "regularMarketTime", "hasPrePostMarketData")}
    return {"meta": m, "bars": bars}


# ---------------------------------------------------------------------------
# CN: Tencent fqkline
# ---------------------------------------------------------------------------
TENCENT_KLINE_URL = ("http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
                     "?param={code},{period},{start},{end},{count},{fq}")

_PERIOD = {"day": "day", "week": "week", "month": "month"}


def fetch_cn_history(session, tencent_code: str, period: str = "day",
                     start: str = "", end: str = "", count: int = 250,
                     fq: str = "qfq") -> dict:
    """Fetch Tencent K-line. period: day/week/month. fq: qfq(前复权, default)
    / hfq(后复权) / '' (raw). count caps ~640 bars/request."""
    period = _PERIOD.get(period, "day")
    url = TENCENT_KLINE_URL.format(code=tencent_code, period=period,
                                   start=start, end=end, count=count, fq=fq)
    r = session.get(url, timeout=15)
    r.raise_for_status()
    d = r.json()
    node = d["data"][tencent_code]
    # key is '{fq}{period}' for adjusted data, e.g. qfqday / qfqweek
    key = f"{fq}{period}" if fq else period
    rows = node.get(key) or node.get(period) or []
    bars = []
    for row in rows:
        # [date, open, close, high, low, volume, (amount?)]
        bars.append({
            "date": row[0], "open": float(row[1]), "close": float(row[2]),
            "high": float(row[3]), "low": float(row[4]),
            "volume": float(row[5]) if len(row) > 5 else None,
            "adj_close": float(row[2]),  # qfq values already front-adjusted
        })
    name = node.get("qt", {}).get("name") if isinstance(node.get("qt"), dict) else None
    return {"meta": {"symbol": tencent_code, "name": name, "adjust": fq or "raw",
                     "period": period, "currency": "CNY"}, "bars": bars}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Historical OHLCV, front-adjusted (US + A-share)")
    ap.add_argument("symbol", help="e.g. NVDA, 600519, 000001.SZ")
    ap.add_argument("--market", choices=["us", "cn"], default=None)
    ap.add_argument("--range", default="1y", help="US range: 1d..max (default 1y)")
    ap.add_argument("--interval", default="1d", help="US interval: 1d/1wk/1mo/1h")
    ap.add_argument("--period", choices=["day", "week", "month"], default="day",
                    help="CN period")
    ap.add_argument("--count", type=int, default=250, help="CN bar count (default 250)")
    ap.add_argument("--start", default="", help="CN start date YYYY-MM-DD")
    ap.add_argument("--end", default="", help="CN end date YYYY-MM-DD")
    ap.add_argument("--no-prepost", action="store_true", help="US: skip pre/post bars")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--csv", default="", help="output CSV path")
    args = ap.parse_args(argv)

    market, canon = normalize_symbol(args.market, args.symbol)
    session = make_session()

    if market == "us":
        crumb = get_yahoo_crumb(session)
        out = fetch_us_history(session, canon, crumb, interval=args.interval,
                               range_=args.range,
                               include_pre_post=not args.no_prepost)
        meta = out["meta"]
        print(f"# {meta.get('longName') or canon} ({meta.get('symbol')}) "
              f"currency={meta.get('currency')} bars={len(out['bars'])} "
              f"last={out['bars'][-1]['date'] if out['bars'] else 'n/a'}",
              file=sys.stderr)
        print(f"# last close {meta.get('regularMarketPrice')}  "
              f"pre {meta.get('preMarketPrice')}  post {meta.get('postMarketPrice')}",
              file=sys.stderr)
    else:
        out = fetch_cn_history(session, canon, period=args.period,
                               start=args.start, end=args.end,
                               count=args.count, fq="qfq")
        m = out["meta"]
        print(f"# {m.get('name') or canon} ({canon}) {m['adjust']} bars={len(out['bars'])}",
              file=sys.stderr)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if args.csv:
        keys = ["date", "open", "high", "low", "close", "adj_close", "volume", "session"]
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            for b in out["bars"]:
                w.writerow({k: b.get(k) for k in keys})
        print(f"CSV written: {args.csv}", file=sys.stderr)
        return 0

    # pretty preview: first 3 + last 5 bars (dedupe when few bars)
    bars = out["bars"]
    if len(bars) <= 8:
        preview = bars
    else:
        preview = bars[:3] + [{"---": "..."}] + bars[-5:]
    for b in preview:
        if "---" in b:
            print("  ...")
            continue
        tag = f" [{b.get('session')}]" if b.get("session") else ""
        print(f"  {b['date']}{tag}  O {b['open']:.2f}  H {b['high']:.2f}  "
              f"L {b['low']:.2f}  C {b['close']:.2f}  V {b.get('volume')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
