---
# ============================================================================
# Wall Street-style Equity Research Report — Markdown Master Template
# ----------------------------------------------------------------------------
# HOW TO USE (agent- or human-authored):
#   1. Copy this file, then replace EVERY {{PLACEHOLDER}} below with a value.
#      Placeholders are uppercase names in double braces — nothing else to
#      configure. Fields marked (optional) may be deleted or left empty.
#   2. The body between the second `---` and the end of the file is the
#      report prose. Any {{FIELD}} inside the body text is auto-filled from
#      the frontmatter above (e.g. {{target_price}} prints $78.00).
#   3. Convert:  python md_to_docx.py my_report.md --pdf
#   4. English is the default; Chinese is fully supported in body text.
# ============================================================================

firm: "{{FIRM_NAME}}"                    # your firm / brand line on the cover
report_type: "{{REPORT_TYPE}}"           # INITIATION OF COVERAGE | COMPANY UPDATE | SECTOR REPORT
title: "{{REPORT_TITLE}}"                # headline, e.g. "Riding the margin-inflection wave; initiate Overweight"
company: "{{COMPANY_NAME}}"
ticker: "{{TICKER}}"
exchange: "{{EXCHANGE}}"                 # e.g. NASDAQ, NYSE, SSE, HKEX
sector: "{{SECTOR}}"                     # e.g. Capital Goods
industry: "{{INDUSTRY}}"                 # (optional) e.g. Automation & Robotics
date: "{{REPORT_DATE}}"                  # e.g. September 10, 2026
currency: "{{CURRENCY}}"                 # e.g. USD, CNY, HKD
price_chart: "{{PRICE_CHART_PATH}}"      # (optional) path relative to this .md
logo: ""                                 # (optional) firm logo, e.g. "assets/logo.png"

# --- Investment summary (rendered as the Key-Data / rating box on cover) ---
rating: "{{RATING}}"                     # OVERWEIGHT / EQUAL-WEIGHT / UNDERWEIGHT (or BUY / HOLD / SELL)
rating_note: "{{RATING_NOTE}}"           # (optional) e.g. "relative to coverage universe"
target_price: "{{TARGET_PRICE}}"         # e.g. 78.00
target_price_prev: ""                    # (optional) previous target, for updates
current_price: "{{CURRENT_PRICE}}"       # e.g. 64.00
upside: "{{UPSIDE_PCT}}"                 # e.g. +22%
horizon: "{{HORIZON}}"                   # e.g. 12 months
market_cap: "{{MARKET_CAP}}"             # e.g. $4.2B
shares_out: "{{SHARES_OUTSTANDING}}"     # (optional) e.g. 65.4M
avg_daily_volume: "{{AVG_DAILY_VOLUME}}" # (optional) e.g. 1.2M
52wk_range: "{{52WK_RANGE}}"             # (optional) e.g. $41.20 – $69.80
pe_ntm: "{{NTM_PE}}"                     # (optional) e.g. 18.5x

# --- Analysts (rendered as the analyst block on cover + page 2) ---
analysts:
  - name: "{{ANALYST_1_NAME}}"
    title: "{{ANALYST_1_TITLE}}"
    phone: "{{ANALYST_1_PHONE}}"
    email: "{{ANALYST_1_EMAIL}}"
  - name: "{{ANALYST_2_NAME}}"          # (optional) delete this entry if only one analyst
    title: "{{ANALYST_2_TITLE}}"
    email: "{{ANALYST_2_EMAIL}}"

# --- Cover conflict-of-interest line (Goldman-style; edit to taste) ---
disclosure_conflict: >-
  {{FIRM_NAME}} does and seeks to do business with companies covered in its
  research reports. As a result, investors should be aware that the firm may
  have a conflict of interest that could affect the objectivity of this
  report. Investors should consider this report as only a single factor in
  making their investment decision. For the full analyst certification and
  other important disclosures, see the Disclosures section at the end of
  this report.

# --- Header/footer ---
header_title: "{{COMPANY_NAME}} ({{TICKER}})"
footer_org: "{{FIRM_NAME}}"
copyright_year: "{{COPYRIGHT_YEAR}}"
---

<!-- =========================================================================
  BODY — everything below is the report prose. Conventions:

  * H1 `#`        → major section (auto-numbered "1. / 2. / ..." in docx)
  * H2/H3/H4      → sub-sections
  * Tables        → standard Markdown tables; compact grid style in docx
  * Images        → `![Caption text](path)`; auto-labeled "Exhibit N: Caption"
  * "Source: ..." → line directly after a table/chart = small gray source note
  * Bold lead-ins → **What's changed:** — GS-style paragraph openers
  * {{FIELD}}     → auto-filled from the frontmatter above
  * The FIRST H1 section (Executive Summary) starts on page 2, after the
    automatically generated cover page.
========================================================================= -->

# Executive Summary

We initiate coverage of **{{COMPANY_NAME}} ({{TICKER}}, {{EXCHANGE}})** with an **{{RATING}}** rating and a **{{CURRENCY}} {{target_price}} twelve-month target price**, implying **{{upside}} upside/(downside)** from the current price of {{CURRENCY}} {{current_price}}. Our rating is relative to the coverage universe over the stated horizon, consistent with the rating definitions in the Recommendation section.

**What's changed.** {{WHAT_CHANGED}} — e.g. "Initiation of coverage: no prior rating or target price. We establish FY2026E revenue of $1,560M (+13% y/y) and EPS of $3.28, 4% above consensus, driven by automation backlog conversion."

**Investment thesis.** Our thesis rests on three pillars: (1) {{THESIS_PILLAR_1}}, (2) {{THESIS_PILLAR_2}}, and (3) {{THESIS_PILLAR_3}}.

**Key risks.** {{TOP_RISKS_ONE_LINER}}.

**Financial highlights (illustrative — replace with your own figures):**

| Metric | {{FY_MINUS_1_A}} | {{FY_0_A}} | {{FY_1_E}} | {{FY_2_E}} |
| --- | --- | --- | --- | --- |
| Revenue ({{CURRENCY}} M) | 1,240 | 1,380 | 1,560 | 1,720 |
| EBITDA margin (%) | 14.2 | 15.8 | 17.5 | 18.3 |
| EPS ({{CURRENCY}}) | 1.92 | 2.35 | 3.28 | 3.95 |
| FCF yield (%) | 5.1 | 6.2 | 8.4 | 10.1 |
| Net debt/EBITDA (x) | 1.8 | 1.4 | 0.9 | 0.5 |

Source: Company data, {{FIRM_NAME}} Research estimates.

# Company Overview

## Business Model

{{COMPANY_OVERVIEW}} — describe what the company does, how it makes money, and its revenue mix (e.g. "Revenue splits roughly 62% equipment, 24% aftermarket parts & services, and 14% software. The aftermarket mix is the strategic priority: it carries 2–3x the gross margin of equipment.").

## Industry & Market Position

{{INDUSTRY_AND_POSITION}} — market size and growth, company rank/share, and differentiation vs. peers.

## Management

{{MANAGEMENT}} — track record, credibility of guidance, key execution watch-items.

# Financial Analysis

## Revenue

{{REVENUE_ANALYSIS}} — growth drivers, backlog visibility, cyclicality.

## Margins & Profitability

{{MARGIN_ANALYSIS}} — margin trajectory, drivers, and comparison to history/peers.

## Balance Sheet & Cash Flow

{{BALANCE_SHEET_ANALYSIS}} — leverage, liquidity, FCF conversion, capital allocation optionality.

### Segment Detail

| Segment | {{FY_0_A}} Rev ({{CURRENCY}} M) | {{FY_1_E}} Rev ({{CURRENCY}} M) | {{FY_1_E}} GM (%) | y/y (%) |
| --- | --- | --- | --- | --- |
| {{SEGMENT_1}} | 856 | 967 | 31 | +13 |
| {{SEGMENT_2}} | 331 | 405 | 52 | +22 |
| {{SEGMENT_3}} | 193 | 226 | 68 | +17 |

Source: Company data, {{FIRM_NAME}} Research estimates.

# Valuation

## Methodology

{{VALUATION_METHODOLOGY}} — e.g. "We value {{COMPANY_NAME}} on a blend of a base-case DCF (60% weight) and forward EV/EBITDA relative to peers (40% weight), cross-checked against historical multiples."

## Discounted Cash Flow

{{DCF_DETAILS}} — WACC, terminal growth, terminal margin assumptions and the resulting equity value per share.

## Comparable Companies

| Company | Ticker | Rating | {{FY_1_E}} EV/EBITDA (x) | {{FY_1_E}} P/E (x) | {{FY_1_E}} FCF Yield (%) |
| --- | --- | --- | --- | --- | --- |
| {{COMPANY_NAME}} | {{TICKER}} | {{RATING_ABBREV}} | 11.8 | 18.5 | 8.4 |
| {{PEER_1_NAME}} | {{PEER_1_TICKER}} | {{PEER_1_RATING}} | 12.5 | 20.1 | 6.9 |
| {{PEER_2_NAME}} | {{PEER_2_TICKER}} | {{PEER_2_RATING}} | 11.0 | 17.2 | 9.3 |
| {{PEER_3_NAME}} | {{PEER_3_TICKER}} | {{PEER_3_RATING}} | 9.8 | 15.0 | 11.2 |
| Median |  |  | 11.4 | 17.9 | 8.9 |

Source: FactSet, {{FIRM_NAME}} Research estimates.

## Sensitivity Analysis

| WACC \ Terminal g | 1.5% | 2.5% | 3.5% |
| --- | --- | --- | --- |
| 8.2% | 72 | 82 | 94 |
| 9.2% | 64 | 75 | 86 |
| 10.2% | 58 | 68 | 79 |

Source: {{FIRM_NAME}} Research estimates. Values in {{CURRENCY}}/share.

## Target Price Derivation

{{TARGET_PRICE_DERIVATION}} — state the blend, the resulting target price, and the bull/bear range. **Upside/(downside) to target: {{upside}}.**

# Investment Thesis

1. **{{THESIS_1_TITLE}}** — {{THESIS_1_DETAIL}}.
2. **{{THESIS_2_TITLE}}** — {{THESIS_2_DETAIL}}.
3. **{{THESIS_3_TITLE}}** — {{THESIS_3_DETAIL}}.
4. **{{THESIS_4_TITLE}}** — {{THESIS_4_DETAIL}}.

![{{CHART_1_CAPTION}}]({{CHART_1_PATH}})

Source: Company disclosures, {{FIRM_NAME}} Research estimates.

# Catalysts & Event Calendar

| Date | Event | Potential Impact |
| --- | --- | --- |
| {{CATALYST_1_DATE}} | {{CATALYST_1_EVENT}} | {{CATALYST_1_IMPACT}} |
| {{CATALYST_2_DATE}} | {{CATALYST_2_EVENT}} | {{CATALYST_2_IMPACT}} |
| {{CATALYST_3_DATE}} | {{CATALYST_3_EVENT}} | {{CATALYST_3_IMPACT}} |
| {{CATALYST_4_DATE}} | {{CATALYST_4_EVENT}} | {{CATALYST_4_IMPACT}} |

# Risk Factors

**Business & operational risks.** {{BUSINESS_RISKS}} — e.g. customer concentration, project execution, supply chain.

**Financial risks.** {{FINANCIAL_RISKS}} — commodity/FX exposure, leverage, refinancing.

**Regulatory & macro risks.** {{REGULATORY_RISKS}} — trade policy, sector cyclicality, wage inflation.

**Market risks.** {{MARKET_RISKS}} — multiple compression, peer contagion, liquidity.

# Recommendation

## Rating

**{{RATING}}** — {{RATING_DEFINITION}}. **{{CURRENCY}} {{target_price}} target price** vs. current price of {{CURRENCY}} {{current_price}}.

## Rating Definitions

- **Overweight (OW)** — expected to outperform the relevant industry coverage universe over the next 12 months.
- **Equal-weight (EW)** — expected total return in line with the relevant industry coverage universe.
- **Underweight (UW)** — expected to underperform the relevant industry coverage universe.
- **Not Rated (NR)** — coverage not currently assigned.

> Rating scales vary by firm: Goldman Sachs uses Buy/Neutral/Sell plus a Conviction List; Morgan Stanley and J.P. Morgan use Overweight/Equal-weight/Underweight (with Not-Rated). Pick ONE scale, state it, and keep it consistent throughout.

## Key Assumptions to Monitor

1. {{ASSUMPTION_1}}
2. {{ASSUMPTION_2}}
3. {{ASSUMPTION_3}}
4. {{ASSUMPTION_4}}

**Next catalyst:** {{NEXT_CATALYST}}.

# Analyst Certification

I, {{ANALYST_1_NAME}}, hereby certify that all of the views expressed in this report accurately reflect my personal views about the subject company and its securities, which have not been influenced by considerations of the firm's business or client relationships. My compensation is based on various factors, including research quality, accuracy of estimates, investor feedback, and firm profitability — not on any specific recommendation contained in this report.

# Disclosures & Disclaimer

**Analyst interests.** The analysts responsible for this report do not beneficially own securities of the subject company, except as disclosed. {{FIRM_NAME}} and/or its affiliates may hold positions in, act as market maker for, or perform services for companies covered in this report.

**Nature of this report.** This report is produced for information and educational purposes only. It is not an offer to sell or a solicitation of an offer to buy any security, and it does not constitute investment advice, a personal recommendation, or tax, legal, or accounting advice. It does not take into account the investment objectives, financial situation, or particular needs of any individual recipient. Recipients should make their own independent investment decisions and, where appropriate, seek professional advice.

**Forward-looking statements.** Statements herein that are not historical facts, including target prices, ratings, and financial forecasts, are forward-looking statements based on current estimates and assumptions that involve risks and uncertainties. Actual results may differ materially. Past performance is not a guide to future performance; future returns are not guaranteed, and a loss of original capital may occur. Target prices are expressions of opinion at the date of publication and are subject to change without notice.

**No warranty.** Information in this report is provided "as is" without warranty of any kind, express or implied. Data is believed reliable but is not guaranteed for accuracy or completeness. Third-party data providers make no warranties and shall have no liability for damages relating to such data.

**Distribution.** This report may not be reproduced, redistributed, or republished, in whole or in part, without the prior written consent of {{FIRM_NAME}}.

© {{copyright_year}} {{FIRM_NAME}}. All rights reserved.

# Appendix

## A. Rating Distribution (for illustration, FINRA-style)

| Rating Category | Count | % of Total | % of IBC |
| --- | --- | --- | --- |
| Overweight / Buy | 152 | 42 | 47 |
| Equal-weight / Hold | 158 | 43 | 42 |
| Underweight / Sell | 56 | 15 | 10 |
| Total | 366 | 100 | 99 |

## B. Glossary

- **EBITDA** — earnings before interest, taxes, depreciation, and amortization
- **EV/EBITDA** — enterprise value divided by EBITDA
- **FCF yield** — free cash flow divided by market capitalization
- **WACC** — weighted average cost of capital

## C. Data Sources

{{DATA_SOURCES}} — company filings (10-K/10-Q/annual reports), guidance and disclosures, FactSet, consensus estimates, and {{FIRM_NAME}} Research estimates. All figures are in {{CURRENCY}} unless otherwise stated.
