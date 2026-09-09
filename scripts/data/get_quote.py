"""
get_quote.py — real-time quote snapshot for US and A-share stocks.

Sources:
  * US  : Yahoo Finance v7 /finance/quote (cookie + crumb required).
          Fields: price, change%, market cap, trailing/forward PE, PB, EPS,
          dividend yield, 52-week high/low, pre/post-market price.
  * CN  : Tencent qt.gtimg.cn (GBK-encoded, tilde-delimited; batch by comma).
          Fields: price, open, high/low, PE(TTM), PB, float/total market cap,
          turnover rate, 52-week high/low. No proxy needed (mainland China).

Usage:
    python get_quote.py NVDA                     # US auto-detect
    python get_quote.py 600519                   # A-share auto-detect
    python get_quote.py 000001.SZ 600519 AAPL    # mixed batch
    python get_quote.py us NVDA AAPL MSFT        # force US market
    python get_quote.py cn 600519 000001         # force CN market
    python get_quote.py --json NVDA 600519       # machine-readable output

Notes:
  * Yahoo requires SOCKS5 proxy in mainland China (set env YAHOO_PROXY,
    e.g. socks5h://127.0.0.1:10808). Tencent works directly.
  * Tencent response is GBK — decode with .decode('gbk', 'replace'), never UTF-8.
  * Tencent field positions (0-indexed, verified 2026-09):
      1 name | 2 code | 3 price | 4 prev_close | 5 open | 30 datetime |
      31 chg | 32 chg_pct | 33 high | 34 low | 37 amount(万) | 38 turnover% |
      39 PE(TTM) | 44 float_mv(亿) | 45 total_mv(亿) | 46 PB | 67/68 52wk H/L
      (47/48 are ±10% price limits, NOT 52-week — older docs are wrong there)
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from common import (YAHOO_PROXIES, YAHOO_RATE_LIMIT_SLEEP, fmt_big,
                    get_yahoo_crumb, make_session, normalize_symbol,
                    yahoo_get)

# ---------------------------------------------------------------------------
# A-share: Tencent qt.gtimg.cn
# ---------------------------------------------------------------------------
TENCENT_QUOTE_URL = "http://qt.gtimg.cn/q={codes}"

# Verified field map (0-indexed) — see module docstring
_TX = {
    "name": 1, "code": 2, "price": 3, "prev_close": 4, "open": 5,
    "datetime": 30, "change": 31, "change_pct": 32, "high": 33, "low": 34,
    "amount_wan": 37, "turnover_rate": 38, "pe_ttm": 39,
    "float_mv_yi": 44, "total_mv_yi": 45, "pb": 46,
    "wk52_high": 67, "wk52_low": 68,
}


def _to_float(x: str) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fetch_cn_quote(session, tencent_codes: list[str]) -> dict[str, dict]:
    """Batch fetch Tencent quotes. tencent_codes like ['sh600519','sz000001']."""
    url = TENCENT_QUOTE_URL.format(codes=",".join(tencent_codes))
    r = session.get(url, timeout=15)
    r.raise_for_status()
    # GBK decode is mandatory — UTF-8 gives mojibake
    text = r.content.decode("gbk", "replace")
    out: dict[str, dict] = {}
    for line in text.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, payload = line.split("=", 1)
        f = payload.strip('"').split("~")
        if len(f) < 69:
            continue
        tcode = key[2:] if key.startswith("v_") else key  # 'v_sh600519' -> 'sh600519'
        price = _to_float(f[_TX["price"]])
        prev = _to_float(f[_TX["prev_close"]])
        out[tcode] = {
            "market": "cn",
            "symbol": f[_TX["code"]],
            "name": f[_TX["name"]],
            "price": price,
            "prev_close": prev,
            "open": _to_float(f[_TX["open"]]),
            "high": _to_float(f[_TX["high"]]),
            "low": _to_float(f[_TX["low"]]),
            "change": _to_float(f[_TX["change"]]),
            "change_pct": _to_float(f[_TX["change_pct"]]),
            "datetime": f[_TX["datetime"]],
            "volume_shou": _to_float(f[6]),
            "amount_wan": _to_float(f[_TX["amount_wan"]]),
            "turnover_rate_pct": _to_float(f[_TX["turnover_rate"]]),
            "pe_ttm": _to_float(f[_TX["pe_ttm"]]),
            "pb": _to_float(f[_TX["pb"]]),
            "float_mv_yi": _to_float(f[_TX["float_mv_yi"]]),
            "total_mv_yi": _to_float(f[_TX["total_mv_yi"]]),
            "wk52_high": _to_float(f[_TX["wk52_high"]]),
            "wk52_low": _to_float(f[_TX["wk52_low"]]),
            "currency": "CNY",
        }
    return out


# ---------------------------------------------------------------------------
# US: Yahoo v7 finance/quote
# ---------------------------------------------------------------------------
QUOTE_FIELDS = [
    "shortName", "longName", "regularMarketPrice", "regularMarketChangePercent",
    "marketCap", "trailingPE", "forwardPE", "priceToBook", "bookValue",
    "epsTrailingTwelveMonths", "dividendYield", "sharesOutstanding",
    "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "regularMarketDayHigh",
    "regularMarketDayLow", "regularMarketVolume", "marketState",
    "preMarketPrice", "postMarketPrice", "currency", "exchange",
]


def fetch_us_quote(session, symbols: list[str], crumb: str) -> dict[str, dict]:
    """Batch fetch Yahoo v7 quotes for US symbols."""
    out: dict[str, dict] = {}
    # v7 accepts a comma-separated symbols param; batch of 10 is safe
    for i in range(0, len(symbols), 10):
        batch = symbols[i:i + 10]
        data = yahoo_get(
            session,
            "https://query1.finance.yahoo.com/v7/finance/quote",
            params={"symbols": ",".join(batch)},
            crumb=crumb,
        )
        for q in data.get("quoteResponse", {}).get("result", []):
            out[q["symbol"]] = {k: q.get(k) for k in QUOTE_FIELDS}
            out[q["symbol"]]["market"] = "us"
            # Yahoo dividendYield is already a percentage (0.44 = 0.44%)
        if i + 10 < len(symbols):
            time.sleep(YAHOO_RATE_LIMIT_SLEEP)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _split_args(args: list[str], market: str | None) -> tuple[list[str], list[str]]:
    """Split symbols into (us_symbols, cn_tencent_codes)."""
    us, cn = [], []
    for sym in args:
        m, canon = normalize_symbol(market, sym)
        (us if m == "us" else cn).append(canon)
    return us, cn


def _pretty(out: dict[str, dict]) -> str:
    lines = []
    for sym in sorted(out):
        q = out[sym]
        if q["market"] == "cn":
            mv = fmt_big((q["total_mv_yi"] or 0) * 1e8, q["currency"])
            lines.append(
                f"{q['name']} ({q['symbol']})  {q['price']} {q['currency']}  "
                f"{q['change_pct']:+.2f}%  PE(TTM) {q['pe_ttm']}  PB {q['pb']}  "
                f"MV {mv}  turn {q['turnover_rate_pct']}%  "
                f"52wk {q['wk52_low']}~{q['wk52_high']}  @{q['datetime']}")
        else:
            mv = fmt_big(q["marketCap"], q["currency"])
            chg = q.get("regularMarketChangePercent")
            chg_s = f"{chg:+.2f}%" if chg is not None else "n/a"
            pre = f"  pre {q['preMarketPrice']}" if q.get("preMarketPrice") else ""
            post = f"  post {q['postMarketPrice']}" if q.get("postMarketPrice") else ""
            lines.append(
                f"{q.get('longName') or sym} ({sym})  {q['regularMarketPrice']} {q.get('currency','USD')}  "
                f"{chg_s}  mktCap {mv}  PE {q['trailingPE']} (fwd {q['forwardPE']})  "
                f"PB {q['priceToBook']}  divYld {q['dividendYield']}%  "
                f"52wk {q['fiftyTwoWeekLow']}~{q['fiftyTwoWeekHigh']}{pre}{post}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Real-time quote snapshot (US + A-share)")
    ap.add_argument("symbols", nargs="+", help="e.g. NVDA, 600519, 000001.SZ")
    ap.add_argument("--market", choices=["us", "cn"], default=None,
                    help="force market; auto-detected by default")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    us_syms, cn_codes = _split_args(args.symbols, args.market)
    session = make_session()
    out: dict[str, dict] = {}
    if cn_codes:
        out.update(fetch_cn_quote(session, cn_codes))
    if us_syms:
        crumb = get_yahoo_crumb(session)
        out.update(fetch_us_quote(session, us_syms, crumb))

    if not out:
        print("No data returned for: " + ", ".join(args.symbols), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(_pretty(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
