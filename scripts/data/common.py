"""
common.py — shared helpers for the Wall Street Research data layer.

Provides:
  * make_session() — a requests.Session that bypasses the Windows system proxy
    (trust_env=False) and uses certifi's CA bundle for SSL. Yahoo endpoints must
    pass proxies=YAHOO_PROXY (SOCKS5) — required in mainland China where Yahoo is
    blocked; override with env var YAHOO_PROXY if your SOCKS5 port differs.
  * get_yahoo_crumb() — fetch the A3 cookie + crumb that Yahoo's v7 quote and
    v10 quoteSummary endpoints require (documented pitfall: fc.yahoo.com returns
    404 but still sets the cookie — that is normal, not an error).
  * normalize_symbol(market, symbol) — canonicalize symbols for both markets:
        cn  : "600519" / "sh600519" / "600519.SH" / "600519.SS"  -> sh600519
              "000001" / "000001.SZ"                              -> sz000001
        us  : "nvda" -> "NVDA" (keeps "^VIX" indices)
  * fmt_big() — human-friendly number formatting.

Usage (as library):
    from common import make_session, YAHOO_PROXY, get_yahoo_crumb, normalize_symbol
    s = make_session()
    s.get("https://query1.finance.yahoo.com/v8/finance/chart/NVDA",
          proxies=YAHOO_PROXY, timeout=15)

Environment:
    YAHOO_PROXY   SOCKS5 proxy for Yahoo (optional; required from mainland China)
    EASTMONEY_HOST  override for the Eastmoney datacenter host if needed
"""
from __future__ import annotations

import os
import time
import certifi

import requests

# ---------------------------------------------------------------------------
# Proxy / session config
# ---------------------------------------------------------------------------
# SOCKS5 proxy for Yahoo (and any GFW-blocked host). Mainland China requires it.
# Override per-user via environment variable.
YAHOO_PROXY = os.environ.get("YAHOO_PROXY", "")
YAHOO_PROXIES = ({"http": YAHOO_PROXY, "https": YAHOO_PROXY} if YAHOO_PROXY else {})

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Seconds to sleep between Yahoo requests to stay under rate limits
# (documented pitfall: "Edge: Too Many Requests" when throttled).
YAHOO_RATE_LIMIT_SLEEP = 1.2


def make_session(use_proxy: bool = False) -> requests.Session:
    """Build a requests.Session.

    trust_env=False is CRITICAL on Windows: the OS registry proxy
    (e.g. a local SOCKS proxy) is a SOCKS-only port that
    fails HTTP CONNECT — every request would die with RemoteDisconnected.
    certifi.where() supplies a valid CA bundle for Yahoo SSL.
    """
    s = requests.Session()
    s.trust_env = False
    s.verify = certifi.where()
    s.headers.update({"User-Agent": UA, "Accept": "*/*"})
    return s


def get_yahoo_crumb(session: requests.Session) -> str:
    """Return the Yahoo crumb token (fetches A3 cookie first).

    fc.yahoo.com responds 404 but sets the A3 cookie in the process — expected.
    The crumb must ride along as a query param on v7/v10 endpoints.
    """
    session.get("https://fc.yahoo.com/", proxies=YAHOO_PROXIES, timeout=15)
    r = session.get("https://query1.finance.yahoo.com/v1/test/getcrumb",
                    proxies=YAHOO_PROXIES, timeout=15)
    r.raise_for_status()
    crumb = r.text.strip()
    if not crumb:
        raise RuntimeError("Yahoo did not return a crumb (rate-limited or blocked?)")
    return crumb


def yahoo_get(session: requests.Session, url: str, params: dict | None = None,
              crumb: str | None = None, retries: int = 3, timeout: int = 20) -> dict:
    """GET a Yahoo endpoint with cookie/crumb, rate-limit sleep and retry.

    Retries on "Edge: Too Many Requests" (HTTP 429) and 5xx with backoff.
    """
    if crumb is not None:
        params = dict(params or {})
        params["crumb"] = crumb
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, params=params, proxies=YAHOO_PROXIES, timeout=timeout)
            if r.status_code == 429 or (r.status_code == 200 and "Too Many Requests" in r.text[:400]):
                time.sleep(2 * attempt)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_err = e
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"Yahoo request failed after {retries} tries: {last_err}")


# ---------------------------------------------------------------------------
# Symbol normalization
# ---------------------------------------------------------------------------
def _cn_to_tencent(code: str) -> str:
    """Normalize a China symbol to Tencent form: sh600519 / sz000001 / bj430047."""
    c = code.strip().upper().replace(".SH", "").replace(".SS", "").replace(".SZ", "")
    c = c.replace(".BJ", "")
    if c[:2] in ("SH", "SZ", "BJ"):
        return c.lower()
    # strip stray leading letters (e.g. "SH600519" with no dot)
    c = c.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if not c:
        raise ValueError(f"invalid A-share code: {code!r}")
    # 6xxxxx -> Shanghai, 0/3xxxxx -> Shenzhen, 4/8/9xxxxx -> Beijing (NEEQ)
    if c.startswith("6"):
        return "sh" + c
    if c.startswith(("0", "3")):
        return "sz" + c
    return "bj" + c


def _is_cn(symbol: str) -> bool:
    s = symbol.strip().upper()
    if s[:2] in ("SH", "SZ", "BJ"):
        return True
    if s.endswith((".SH", ".SS", ".SZ", ".BJ")):
        return True
    # Bare 6-digit numeric code -> A-share
    return len(s) == 6 and s.isdigit()


def normalize_symbol(market: str | None, symbol: str) -> tuple[str, str]:
    """Return (market, canonical_symbol). market: 'us' | 'cn' (auto-detected).

    Examples:
        normalize_symbol(None, "NVDA")        -> ("us", "NVDA")
        normalize_symbol(None, "600519")      -> ("cn", "sh600519")
        normalize_symbol("cn", "000001.SZ")   -> ("cn", "sz000001")
        normalize_symbol("us", "^VIX")        -> ("us", "^VIX")
    """
    sym = symbol.strip()
    if market and market.lower() in ("us", "cn"):
        m = market.lower()
    else:
        m = "cn" if _is_cn(sym) else "us"
    if m == "cn":
        return m, _cn_to_tencent(sym)
    # US: uppercase, keep indices like ^VIX / ^GSPC
    return m, sym.upper() if not sym.startswith("^") else sym


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
def fmt_big(v, currency: str = "") -> str:
    """Format large numbers (market caps / revenues) as 5.41T / 2.16B / 910.9M."""
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        x = float(v)
        for suf, div in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
            if abs(x) >= div:
                return f"{x/div:.2f}{suf}{(' ' + currency) if currency else ''}"
        return f"{x:,.2f}"
    return str(v)


if __name__ == "__main__":
    for m, s in [("us", "nvda"), ("cn", "600519"), ("cn", "000001.SZ"),
                 ("us", "^VIX"), ("cn", "sh600519")]:
        print(m, s, "->", normalize_symbol(m, s))
