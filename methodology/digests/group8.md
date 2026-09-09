# G8 组凝练 — 个股深度研究 Single-Name Deep Research (10篇)

*Source: report_list_100.md, lines 91-100. 英文为主，括号内为中文注。*

## 组总览：个股深度研究的方法论主线

G8 covers single-stock deep research in both directions — initiation-style valuation (Tesla, Meta) and forensic/event-driven takedowns (GEnron, FTX, Boeing). The methodological spine: **convert a company into a falsifiable financial model**. Common thread across all ten: (1) decompose the business into segments and KPIs, then identify the single metric anchoring the growth narrative (Netflix's net adds, BYD's share, Meta's segment loss); (2) forecast through explicit drivers (volume × price × margin, share × price-band) instead of growth-rate assumptions; (3) pick the valuation tool matched to the business — scenario tree/DCF for high-uncertainty growth, SOTP for conglomerates and strategic bets, cost-curve analysis for competitive shifts; (4) express the target price as a band (bull/base/bear) with per-branch assumptions, bridging any revision to per-share value; (5) state falsification triggers — the print or event that breaks the thesis. The bear-side cases add a second spine: **balance-sheet integrity before business-model beauty** (asset segregation, cash-flow-vs-earnings divergence, segment transparency, third-party data cross-checks), plus the discipline that thesis-correct ≠ timing-correct ≠ position-correct. Recurring red flags: one-time demand mistaken for trend, narrative without segment data, culture/regulation treated as unquantifiable, milestones celebrated without the bear case.

---

### Tesla Scenario Valuation: $10 Worst Case to $2,500 Bull (Morgan Stanley / Adam Jonas, 2019-2021)
- **研究方法**: High-uncertainty growth stocks get a scenario tree, not a point target: bull $391 / base $230 / bear $10 (cut from $97), each branch carrying explicit driver assumptions — the bear case halved China volume (trade-war risk) and eroded margins, producing $16.4B lost value ≈ $87/share to bridge old→new bear. Optionality-style valuation: value the narrative (robotaxi, energy) separately from near-term cash flows, each with its own falsification conditions; self-funding (FCF) and capital-market access treated as the binding constraint.
- **行文范式**: Bull/base/bear triplet in one note; per-business-line sections (auto, energy, autonomy); base target kept stable while the bear band is revised — a template for communicating confidence bands instead of point precision.
- **图表特征**: Scenario tree / waterfall bridging old to new targets; per-scenario P&L; China volume × ASP sensitivity grid; share-price band vs target chart.
- **可复用标准动作**: Identify the binding constraint (demand / FCF / capital access) → model per-scenario volumes and margins → bridge value changes to per-share → keep base, move the band → attach probability only where supportable.
- **教训或红旗**: Extreme ranges are partly hedging statements — the $10 headline was not the thesis; markets trade the delta between scenarios and the narrative, not the base case. (极端区间本质是对冲性言论)
- **可执行规则**: Always publish a bull/base/bear triplet with per-branch driver assumptions; bridge every target revision to a per-share value change; flag the scenario that would break the narrative, not just the one you believe.

---

### 'GEnron'? Markopolos versus General Electric (Harvard Business School Case / Harry Markopolos, 2019)
- **研究方法**: Forensic template for evaluating short-seller fraud claims: treat the 175-page report as a hypothesis set and test each claim independently — LTC insurance reserve adequacy ($29B gap claim, cross-checked via statutory filings vs peers like Prudential), cash-flow-vs-earnings divergence, working capital, Baker Hughes accounting. Key move: pull **third-party/counterparty data** (statutory annual statements, Schedule H) instead of relying on the target's own disclosures.
- **行文范式**: Case-study structure: allegation → evidence chain → management rebuttal → what to verify next; forces a decision under incomplete information.
- **图表特征**: Reserve-sensitivity tables ($ per 25bps); peer-comparison reserve charts; cash-flow-vs-earnings gap charts; timeline of allegations vs company statements.
- **可复用标准动作**: List allegations → map each to a testable metric → source independent data → size the claimed fraud as % of market cap → assess accuser credibility (track record, incentives, "wolf-cry" history).
- **教训或红旗**: "Bigger than Enron" framing invites skepticism; even a credible accuser (Madoff whistleblower) needs per-claim verification; short sellers profit from declines, so their incentives belong in your reading. (狼来了式指控的可信度要单独评估)
- **可执行规则**: Verify every fraud claim against third-party data, never the target's filings alone; size alleged fraud as % of market cap before weighing it; discount repeated alarms from the same accuser.

---

### Boeing 737 MAX: FAA Failures and the Crashes (U.S. House Committee via Reuters, 2020)
- **研究方法**: Root-cause attribution for a safety event using layered analysis: engineering defect (MCAS) × regulatory failure (delegated certification/ODA) × corporate culture (schedule pressure, cost cutting). Then translate the event into a quantified financial transmission chain: groundings → delivery pause → production-rate cuts → compensation/penalties → order-book and share impact.
- **行文范式**: Investigative-committee structure — findings per layer with evidence, then consequences; for stock work: event → P&L/cash-flow bridge with explicit duration assumptions.
- **图表特征**: Crash/grounding timeline; deliveries vs production-rate charts; certification-delegation structural diagram; cost waterfall (compensation, idle production, penalties).
- **可复用标准动作**: For any operational/regulatory shock: build the causal chain to hard financials (orders → deliveries → revenue → cash), quantify each link, then estimate duration — fleet-grounded duration is the key valuation variable.
- **教训或红旗**: Culture and regulation are soft variables that must be wired to hard outcomes to be priced; consensus models lag such events because they keep prior delivery schedules. Safety incidents hit production rates before they hit prices.
- **可执行规则**: Convert any safety/regulatory event into an orders→deliveries→cash chain before touching the model; assume recovery takes longer than management guides.

---

### Netflix: First Subscriber Loss in a Decade (Reuters, 2022)
- **研究方法**: Growth-anchor analysis: identify the single KPI the market prices (net subscriber adds), decompose it (gross adds / churn / ARPU), and stress what the multiple implied. A -200K add miss broke the DCF anchor → ~25% market cap destroyed in a day: saturation is gradual in the data but discontinuous in the price.
- **行文范式**: Event-driven re-rating piece: the KPI print → the reaction → what the multiple was really paying for (growth duration, not current cash flows). Template for any subscription-growth company.
- **图表特征**: Subscriber-adds trend with consensus-vs-actual markers; ARPU decomposition; penetration curve vs saturation estimate; valuation-multiple history.
- **可复用标准动作**: Track the anchor KPI quarterly vs consensus; maintain an explicit penetration/saturation estimate; stress-test the DCF on decelerating adds (mature-growth terminal value); treat guidance revisions as the catalyst trigger.
- **教训或红旗**: Narrative metrics must be checkable every quarter; one miss at the anchor can erase a year of multiple expansion — the multiple was never about near-term cash flows but about growth duration. (增长叙事必须逐季可跟踪)
- **可执行规则**: Every growth thesis must name its anchor KPI and its falsification threshold; test what the multiple implies about growth duration before assuming it.

---

### Peloton: From Pandemic Success to Record Low (Business Insider, 2022)
- **研究方法**: Demand-pull-forward analysis: separate one-time COVID demand from structural demand. 2020's explosion (installed base, backlog) became 2022's demand cliff as pull-forward saturated the addressable base; inventory build and supply-ramp decisions amplified the earnings swing. Engagement/churn tracked as leading indicators of installed-base value.
- **行文范式**: Rise-and-fall chronology (2020 peak → 2022 record low) with financial markers at each turn — the standard case template for pandemic-beneficiary stocks.
- **图表特征**: Revenue / installed-base / engagement trend charts; inventory vs sell-through; margin bridge from demand mix; share-price arc vs fundamentals.
- **可复用标准动作**: Model a "base demand" ex-shock; add shock demand as an explicit decaying overlay; watch inventory vs forward demand; use engagement and churn as leading indicators before revenue turns.
- **教训或红旗**: One-time demand is not a trend; management extrapolates the spike into capex and headcount, then pays twice (overbuild + demand cliff). (需求前置陷阱)
- **可执行规则**: Always separate one-time from structural demand and show both series; for consumer durables, let usage/engagement metrics lead revenue.

---

### FTX Collapse: A Post-Mortem (Seven Pillars Institute, 2022)
- **研究方法**: Governance-and-audit forensics: audit balance-sheet integrity before the business model — client-asset segregation (commingling with Alameda), related-party transactions, who controls the keys; founder charisma vs balance-sheet common sense; regulatory vacuum ≠ legality.
- **行文范式**: Post-mortem structure: what happened → the governance failures → the audit/regulatory gaps → transferable red flags for any financial platform.
- **图表特征**: Funds-flow diagram (customer assets → Alameda → positions); marketing-narrative vs balance-sheet contrast table; timeline of audit/regulatory signals missed.
- **可复用标准动作**: For any platform/financial firm: check asset custody and segregation first, then related-party exposure, auditor independence, and whether disclosed reserves match liabilities — the balance sheet is the business model's floor.
- **教训或红旗**: Too-good-to-be-true returns + charismatic founder + opaque custody = exit; regulatory absence is not legal safety; audits are only as good as data access. (客户资产隔离是生命线)
- **可执行规则**: Test client-asset segregation before revenue quality for any financial platform; treat founder halo as a discount factor, not a premium.

---

### Nvidia Crosses $1 Trillion Market Cap (CNBC, 2023)
- **研究方法**: Milestone-valuation study: map the TAM chain from AI capex (hyperscaler spend) → accelerator/GPU revenue via explicit share-and-pricing assumptions; milestone coverage should price both sides of the divergence — structural-AI bulls vs bubble skeptics — rather than narrate the milestone.
- **行文范式**: Milestone + framework: what the crossing means, the demand chain, then both bull and bear arguments stated fairly; milestone as datapoint, not verdict.
- **图表特征**: GPU revenue vs AI capex mapping; market-cap milestone timeline; segment mix (data-center share); competitor/peer share charts.
- **可复用标准动作**: Build the TAM chain with explicit share and pricing assumptions; sensitivity the valuation to capex growth and share; benchmark the multiple vs history and peers; re-verify mapping assumptions quarterly.
- **教训或红旗**: Milestone coverage without the bear case is cheerleading; capex→revenue mapping assumptions (share, price, spend longevity) age fast. (里程碑事件研究要看多空分歧定价)
- **可执行规则**: For any AI-infrastructure name, show the capex→revenue mapping with share assumptions and re-check it quarterly; treat milestone events as data, never as conclusions.

---

### Ackman's $1B Herbalife Short (Pershing Square / Bill Ackman, 2012-2018)
- **研究方法**: Full public-short campaign anatomy: pyramid-scheme thesis built from business-model forensics (distributor economics, revenue concentration, churn), escalated through public roadshows (hundreds of slides), fought by counterparty Icahn's opposing position, and resolved by the 2016 FTC settlement ($200M fine + business-model overhaul — partial vindication) — while the short was closed in 2018 at a ~$760M-$1B loss.
- **行文范式**: Case study of thesis → catalyst path → counterparty → exit; the throughline is that thesis correctness, timing, and position sizing are three independent variables.
- **图表特征**: MLM structure diagram; distributor-churn and revenue-concentration charts; share-price timeline vs campaign events; position-vs-price P&L.
- **可复用标准动作**: A short thesis needs: forensic business-model analysis, a regulatory/legal catalyst path, and a pre-committed exit plan; size the position for cost of carry (borrow fees, time) — not just thesis confidence.
- **教训或红旗**: Being right is not enough: counterparties can fight the thesis, regulatory timelines run for years, and carry costs destroy P&L; public crusades also harden management against settlement. (观点正确≠时点正确≠仓位正确)
- **可执行规则**: Treat thesis, timing, and sizing as three independent risks; always pre-commit an exit threshold when shorting.

---

### BYD Overtakes Tesla in Quarterly EV Sales (CNBC, 2024)
- **研究方法**: Competitive-shift analysis: identify the structural cost advantage (vertical integration — battery self-supply + localized supply chain) and show how it flows through the cost curve into a share inflection and price-band down-migration (invading from below). The overtake is a datapoint on a trend, not an isolated event.
- **行文范式**: Competitive-landscape piece: cost-structure comparison → share trajectory → implications for incumbents' unit economics.
- **图表特征**: Quarterly delivery-share chart (BYD vs Tesla); cost-per-kWh / vertical-integration curve; price-band position map; margin comparison.
- **可复用标准动作**: Map both competitors' cost curves; quantify the per-unit cost gap; forecast share by price band; translate incumbent share loss into volume/margin sensitivity.
- **教训或红旗**: Watch share inflection points and price-band invasion rather than single-quarter prints; structural cost advantages compound — a 5% share move becomes a margin war the next year. (份额拐点+价格带下沉)
- **可执行规则**: In any duopoly/oligopoly, model the cost-curve gap first — share follows cost; track share by price band, not just total volume.

---

### Meta Lost $13.7B on Reality Labs in 2022 (CNBC, 2023)
- **研究方法**: Segment-transparency analysis: the Reality Labs segment P&L (revenue + operating loss) made the metaverse pivot auditable and changed the market narrative — "long-termism" claims need segment data plus exit/milestone criteria before they can be priced.
- **行文范式**: Earnings-analysis piece: segment P&L vs corporate narrative; core cash cow (Family of Apps) valued separately from the venture bet.
- **图表特征**: Segment revenue/op-loss trend; core-vs-venture SOTP waterfall; capex allocation chart; spend-vs-milestone timeline.
- **可复用标准动作**: Split valuation into core (stable cash flows → multiples) + venture bets (option value with explicit milestones); demand segment-level disclosure; tie "long-term" spending to pre-committed exit criteria.
- **教训或红旗**: Management long-termism is unfalsifiable without segment data and stop rules; a disclosed loss line is the market's best audit tool — if a company hides it, that itself is information. (长期主义表述需要分部数据+退出标准)
- **可执行规则**: Value conglomerates/strategic-bet companies as core + option, never blended; require segment P&L and exit criteria before paying for "long-term" narratives.

---

## 凝练后这组的核心资产 (可迁移到任何个股研报的方法)

1. **Bull/base/bear 情景树**：高不确定性个股以情景树替代单点目标价，每支路配显式驱动假设；任何目标价修订都要桥接回每股价值变化。
2. **锚定KPI纪律**：点名市场真正定价的那个指标（订阅净增/交付量/份额/分部亏损），给出证伪阈值，逐季对照 consensus 跟踪。
3. **估值工具匹配业务**：高期权价值成长股用情景/DCF，集团与战略押注用 SOTP（核心+期权，绝不混合），稳定复利股用倍数；先选工具再算数。
4. **事件→财务传导链**：安全/监管/运营冲击一律先拆成订单→交付→收入→现金的逐环量化链，并显式估计持续时间，再动模型。
5. **资产负债表优先的取证清单**：客户资产隔离、现金流与盈利背离、关联方敞口、用第三方/对手方数据交叉验证（法定报表、对手方披露）、储备敏感性。
6. **一次性需求与结构性需求分离**：冲击需求作为显式衰减叠加层建模；耐用消费品用使用/留存等先行指标领先营收。
7. **成本曲线先行的竞争分析**：份额跟随结构性成本差距；按价格带跟踪份额、盯拐点而非单季数字。
8. **论点/时点/仓位三独立**：做空尤其要先承诺退出阈值、计入持有成本，并假设存在对手方——对≠赚。
