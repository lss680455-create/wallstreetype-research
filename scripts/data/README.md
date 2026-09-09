# Wall Street Research — Data Acquisition Layer

Free, live market-data fetch for **US stocks and A-shares**. Pure Python +
`requests` — no `yfinance`, no broker SDKs, no API keys. Every value is fetched
live from public endpoints and traceable to its source; **no data is
synthesized or extrapolated**.

This is an agent-agnostic data layer: call the scripts from a terminal, wrap
them in your own agent, or `import` them as Python modules.

---

## Quick start

```bash
# snapshot (price / market cap / PE / PB / 52-week)
python get_quote.py NVDA
python get_quote.py 600519 000001.SZ        # mixed market batch

# history (front-adjusted OHLCV)
python get_history.py NVDA --range 3mo
python get_history.py 600519 --count 250    # A-share, 前复权

# fundamentals
python get_financials.py NVDA
python get_financials.py 600519 --periods 5

# unified entry point
python data_fetcher.py us NVDA all --json
python data_fetcher.py cn 600519 financials
```

Requirements: Python 3.8+, `requests`, `certifi`, `pysocks` (for SOCKS5).
```bash
pip install requests certifi pysocks
```

---

## Data sources

| Market | Data | Endpoint | Proxy |
|--------|------|----------|-------|
| US | Quote snapshot (price, mkt cap, PE, PB, EPS, div yield, 52wk, pre/post price) | Yahoo Finance `v7/finance/quote` (cookie + crumb) | SOCKS5 required from mainland China |
| US | OHLCV history (front-adjusted), incl. pre/post market bars | Yahoo Finance `v8/finance/chart` (cookie session) | SOCKS5 required from mainland China |
| US | Financials (income/balance/cashflow, margins, ROE, analyst targets) | Yahoo Finance `v10/finance/quoteSummary` (cookie + crumb) | SOCKS5 required from mainland China |
| CN | Quote snapshot (price, PE-TTM, PB, float/total MV, turnover, 52wk) | Tencent `qt.gtimg.cn` | none (direct) |
| CN | OHLCV history, 前复权/后复权 | Tencent `web.ifzq.gtimg.cn/appstock/app/fqkline/get` | none (direct) |
| CN | Key financial indicators per report period (营收/归母/扣非EPS/ROE/毛利率/同比) | Eastmoney datacenter `RPT_LICO_FN_CPD` | none (direct) |
| CN | F10 主要指标 per period (EPS/BPS/每股经营现金流/毛利/扣非净利/同比) | Eastmoney `emweb.securities.eastmoney.com` F10 API | none (direct) |

> **Why these sources?** Yahoo is the most reliable free source for US OHLCV +
> fundamentals (no API key; needs a cookie+crumb session). Tencent is the most
> stable free A-share source (the `push2`/`push2his` Eastmoney hosts are
> frequently unreachable — avoid them). Eastmoney datacenter + F10 hosts are
> reachable directly and cover A-share fundamentals well.
>
> Alternatives considered but **not** used: Stooq (download endpoint is behind a
> JS challenge; live quote CSV 404s), Alpha Vantage (free tier capped at 25
> req/day and needs a key), stockanalysis.com API (endpoints return 404 as of
> 2026-09). Yahoo's undocumented endpoints remain the best free US option.

---

## Proxy & network

- **Yahoo requires a SOCKS5 proxy from mainland China** (set it via the
  `YAHOO_PROXY` env var; outside China it works without a proxy):
  ```bash
  YAHOO_PROXY=socks5h://127.0.0.1:10808 python get_quote.py NVDA
  ```
- **Chinese sources (Tencent / Eastmoney) connect directly** — no proxy.
- **`trust_env=False` is set on all sessions.** On Windows, the OS registry
  proxy (often a SOCKS-only local port) makes HTTP CONNECT fail with
  `RemoteDisconnected`; disabling trust_env routes around it. Do not set
  `CURL_CA_BUNDLE` / `SSL_CERT_FILE` — a wrong bundle breaks both curl and
  requests.
- Yahoo SSL on Windows: `session.verify = certifi.where()` is used in
  `common.make_session()`.

---

## Rate limits & etiquette

- **Yahoo**: space requests 1–2 s apart (built into `common.yahoo_get`).
  A session cookie from `fc.yahoo.com` is required; the v7/v10 endpoints also
  need a `crumb` (auto-fetched). On throttling Yahoo returns
  `Edge: Too Many Requests` — the client retries with backoff. Keep batch
  symbol counts modest and cache results you re-use.
- **Tencent**: batch multiple symbols in one quote request (comma-separated);
  one K-line request per symbol. No documented hard limit, but be polite.
- **Eastmoney**: datacenter requests are light; no aggressive polling.

---

## Field semantics (口径 — read before quoting numbers)

### US (Yahoo)
- `marketCap`, `totalRevenue`, `netIncome` … are in the **currency** reported
  (`currency` field, usually USD), raw units (no scaling).
- `dividendYield` is **already a percentage** (0.44 means 0.44%), `payoutRatio`
  likewise.
- `trailingPE` / `forwardPE` / `priceToBook` / `trailingEps` are point-in-time
  trailing-12-month values. Prefer TTM over single-quarter figures for
  valuation claims.
- History `adjclose` (adjusted close) is split/dividend-adjusted; use it for
  returns. Unadjusted `close` is the raw session close.
- **Pre/post market**: Yahoo populates `preMarketPrice` / `postMarketPrice`
  (and appends pre/post bars) **only during live pre/post sessions**
  (US pre-market 04:00–09:30 ET, after-hours 16:00–20:00 ET). When the market
  is closed these fields are `null` — that is expected, not a bug.
- Earnings from `quoteSummary` `incomeStatementHistory` are **fiscal-period**
  dates (`period` = fiscal period end date), not calendar quarters.

### CN (Tencent)
- `qt.gtimg.cn` responses are **GBK-encoded** — decode with
  `content.decode('gbk')`, never UTF-8 (mojibake).
- Price/PE/PB are self-explanatory; **market cap units are 亿元 (100M CNY)**;
  turnover `amount` is 万元 (10k CNY); K-line `volume` is **手** (100 shares).
- K-line with `qfq` (前复权) is **already front-adjusted** — `close` is the
  adjusted price; there is no separate adjclose column.
- Verified field map (0-indexed): `1` name, `2` code, `3` price, `4` prev
  close, `5` open, `31` change, `32` change %, `33/34` day high/low,
  `38` turnover %, `39` PE-TTM, `44` float MV(亿), `45` total MV(亿),
  `46` PB, **`67/68` 52-week high/low**.
  ⚠️ Correction to older documentation: fields `47/48` are the **±10% price
  limits** (涨停/跌停), *not* the 52-week range.

### CN (Eastmoney)
- `RPT_LICO_FN_CPD` filter uses `SECURITY_CODE` (no exchange suffix) and **must
  sort by `UPDATE_DATE`** (sorting by `REPORT_DATE` returns error 9501).
- `DEDUCT_BASIC_EPS` (扣非EPS) is often **null for Q1 reports** — populated for
  半年报/年报. Use `KCFJCXSYJLR` (F10) or the income-statement report
  `RPT_DMSK_FN_INCOME` for exact 扣非净利 amounts.
- F10 `MLR` is **gross profit in yuan** (毛利), *not* a percentage — the gross
  margin percentage is `XSMLL` in the datacenter report.
- `REPORT_DATE` is the report period end; check `NOTICE_DATE` when you need the
  actual disclosure date (avoid look-ahead bias).

---

## Scripts

| Script | Purpose |
|--------|---------|
| `common.py` | Shared session/cookie/crumb/proxy/normalization helpers |
| `get_quote.py` | Real-time quote snapshot, both markets, batch |
| `get_history.py` | Historical OHLCV (front-adjusted), both markets |
| `get_financials.py` | Fundamental indicators, both markets |
| `data_fetcher.py` | Unified entry: `data_fetcher.py <us|cn> <symbol> <quote|history|financials|all>` |

Every script runs standalone from a terminal and prints human-readable output
(`--json` for machine-readable, `--csv <path>` for history). Each has a
usage docstring at the top. `data_fetcher.fetch(market, symbol, data_type, …)`
is also importable as a Python API.

## Symbol formats

- US: `NVDA`, `AAPL`, indices `^VIX`, `^GSPC` (pass `--market us` if needed)
- CN: `600519`, `000001`, `000001.SZ`, `600519.SH`, `600519.SS`, `sh600519`,
  `sz000001`, `bj430047` — market auto-detected from the format
- CN exchange mapping: `6xxxxx`→Shanghai, `0/3xxxxx`→Shenzhen,
  `4/8/9xxxxx`→Beijing (NEEQ)

## Limitations

- Yahoo endpoints are undocumented and may change or throttle without notice;
  they require the cookie/crumb dance and a SOCKS5 proxy from China.
- US fundamental statements are annual-frequency (latest ~4 fiscal years);
  use Eastmoney datacenter for A-share quarterly detail.
- All timestamps for US intraday bars are in the exchange local timezone
  (converted via the exchange timezone name); daily bars are calendar dates.
