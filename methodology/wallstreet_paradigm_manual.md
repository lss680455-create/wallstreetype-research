# Wall Street Paradigm Manual — 华尔街研报范式手册

> **Purpose**: The methodology core of the Wall Street Research skill. Distilled from 100 institutional reports across 10 research groups (G1–G10 digests, all cross-group duplicates merged). Every rule below is directly executable when writing a research report. 正文英文，括号内为中文注。
> **How to use**: Ch1 = the report skeleton you must fill; Ch2 = the method toolbox (pick per question type); Ch3–5 = style/evidence discipline; Ch6 = self-check before publishing; Ch7 = the red-team audit another agent runs on your draft.

---

# Chapter 1 — Universal Report Architecture 通用论证骨架

> The spine shared by Goldman, Morgan Stanley, JPM, the Fed, academic papers, and forensic shorts. Fill these 8 blocks in order; each block states WHAT to write, HOW, and COMMON ERRORS.

## 1.1 Executive Summary 执行摘要
- **What**: One headline number/conclusion + the stance + the single best evidence point + probability (if any) + the one condition that would change the view. Sell-side norm: "5 Key Takeaways" up front (G2); "in brief: three sentences" (G1/JPM).
- **How**: Open with the number, not the topic ("Bull & Bear 7.9→8.5, triggering the 16th contrarian sell since 2002" — G1). State the delta vs consensus explicitly ("15% recession probability vs the market's fear"; "2024 GDP 2.1% vs Bloomberg consensus 1%" — G1/GS). Keep it to ≤10 lines; the summary must stand alone.
- **Common errors**: Headline without the number; summary contradicting the body; presenting a range as a single point (readers keep the point, drop the range — G6/TAM); burying the stance until page 3.

## 1.2 Stance Statement 立场声明
- **What**: An unambiguous position: rating/direction (Overweight/Underweight, Buy/Sell), scenario preference, or "no edge, no call." For macro: probability + calendarized path. Name the thesis with a memorable frame ("Fire and Ice" — G1/Wilson; "Copper is the New Oil" — G4).
- **How**: State it in the first 10% of the report. Separate the identification claim from the timing claim as two sentences ("it is expensive" ≠ "it bursts now" — G10/Grantham). If the conclusion is conditional, say so in the same breath as the stance, not in a footnote.
- **Common errors**: Hedge-word stance that cannot be falsified ("could go either way"); naming a frame without a falsifiable core (G2/Ives); converting an identification call into a timing call (G10).

## 1.3 Falsifiable Thesis 可证伪论点
- **What**: Every assertion translated into a measurable, checkable indicator with a threshold — never an uncheckable trend statement. "This time is different" must be decomposed into testable items (earnings quality, valuation percentile, adoption speed) and compared against history (G2/MS).
- **How**: One question + two-sided evidence (G1/GS "single question, dual-sided argument"). For each bullish claim, write its explicit invalidation condition in the same section ("what would falsify this" — G7/Soros). Concessions are strategic shields: "a pessimist could still be right" (G2/Covello) — but the real test is whether the named falsification condition is trackable.
- **Common errors**: Unfalsifiable trend statements ("AI is transformative" — G2/Meeker); circular reasoning (using low rates both as result and as evidence — G1/Summers); "costs always fall" treated as law rather than belief (G4/lithium).

## 1.4 Evidence Chain 证据链
- **What**: A causal chain from mechanism to data, with a data node at every link: micro shock → balance sheet → credit supply → macro output (G5/Hatzius); orders → deliveries → revenue → cash (G8/Boeing); capex → required end revenue → who pays (G2/Cohn).
- **How**: Walk the chain link by link, no skipped steps; where multiple estimation methods exist, present them side by side and flag which ones assume their own answer (G5). Cross-validate each node with an independent source (two respondent groups, third-party data, hard data vs survey — G6). Label the evidence layer of every number (source data → behavior survey → aggregate model, weakest to strongest — G6/GLP-1).
- **Common errors**: Omitting feedback loops (systematically understates tails — G5); "cat chasing its tail" loss estimates (G5); reporting correlation without mechanism (G1/Estrella-Mishkin); quoting a headline aggregate while the loss concentrates at nodes with thinnest buffers (G10/chip).

## 1.5 Bear Case / Counterparty Handling 反方处理
- **What**: The strongest version of the opposing argument, stated inside the body of each theme — not exiled to a risk appendix (G10/MS 2030). For single names: the company's own rebuttal, anticipated and answered (G3/UBS; G7/Nikola debate-style updates).
- **How**: Fully restate the bull case before dismantling it (G2/Covello). Answer every counter-point point-by-point after a rebuttal lands, publicly (G7). Pre-commit what "good news" would look like before the event, to kill post-hoc rationalization (G2/Rasgon). Check whether your consensus comparison cherry-picks only the indicators that support you (G1/GS).
- **Common errors**: Strawmanning the opposition; selective consensus comparison (G1); "every variable supports my view" single-sided narratives with no quantified tail (G1/Hatzius); treating a refuting datapoint as noise instead of a signal.

## 1.6 Scenario & Probability 情景概率
- **What**: A scenario family, not a point: bull/base/bear with per-branch driver assumptions (G8/Tesla); scenario fan with probabilities where supportable; target levels bound to trigger and invalidation conditions (G1/Wilson). Output probability, not binary (G1/Estrella-Mishkin).
- **How**: Express conclusions as "range + conditions" (G9/Oppenheimer), or as a scenario trio where base stays stable while bands are revised (G8). Calendarize policy/econ paths so they can be audited ex-post ("from 2024Q4, 25bp per quarter" — G1/GS). Keep identification and timing as separate statements (G10).
- **Common errors**: Single-point targets with no probability distribution (= unfalsifiable — G9/Dow 36,000); extreme ranges used as hedging statements while the real thesis is elsewhere (G8/Tesla — markets trade the delta between scenarios and the narrative); scenario presented as forecast (G4/Shell — "scenario = conditional, not prediction").

## 1.7 Risk & Exit 风险与退出
- **What**: The invalidation-condition checklist turned into trackable trigger variables; quantified tail scenarios; explicit exit triggers; a reader-trackable variable set (credit growth, revisions breadth, term spread, policy path — G1).
- **How**: For every optimistic/pessimistic conclusion, write the concrete conditions under which the logic breaks (G1/JPM "To be sure…could change"). Publish a milestone checklist so reality can be tracked against the scenario (G4/IEA). Treat thesis, timing, and position as three independent risks: pre-commit an exit threshold, size for cost of carry, assume a counterparty (G8/Herbalife; G7/Burry — "right too early is functionally wrong"). Encode conclusions into capped-loss structures (CDS/options — G7).
- **Common errors**: Tail scenarios unquantified; invalidation list too narrow (G1/JPM — 2023 logic failed as rates rose); no exit plan on bold calls (G4/Murti); disclosure without an enforced remediation deadline (G5/SCAP — "disclosure without teeth is PR").

## 1.8 Post-Mortem Hook 复盘钩子
- **What**: Leave an audit trail: date-stamped predictions, versioned numbers, reproducible data+code, pre-archived evidence. The report should be checkable after the fact — that is what makes it research rather than commentary.
- **How**: Date-stamp narratives so they can be audited (G9/Death of Equities). Publish what moved vs last year and why (version management — G4/WEO). Archive anything that can vanish before publishing (G7/Adani Wayback). Report mean AND median, swap samples/weights/estimation windows, disclose data+code (G1/Reinhart-Rogoff). Keep the framework stable while refreshing data every edition (G1/Wilson — "framework outlives the point target").
- **Common errors**: Publishing in the voice of "principle" with no specific falsifiable prediction (G1/Dalio — hard to audit ex-post); framework commitment without stated failure conditions (G1/Powell FAIT); citing URLs that have rotted or been repurposed without verification (G5).

---

# Chapter 2 — Methods Catalog 研究方法总库

> All reusable standard actions from G1–G10, cross-group duplicates merged into one entry each (the most complete expression wins). 60 methods in 8 functional families. Format: **Name (中文) · source groups**.

## A. 需求建模类 Demand Modeling

### A1. TAM Multiplier Chain — TAM乘数链 · G6, G10
**When**: Sizing any new/adjacent market (drugs, AI, energy transition, EVs); whenever a headline $ figure risks becoming gospel.
**How**: ① Build TAM as an explicit multiplier product — eligible base × penetration × payer/reimbursement × price × duration — never a single headline. ② Anchor to a persistent institutional inflection (chronic-disease designation, policy mandate), not pure demand extrapolation. ③ Run sensitivity on every multiplier; state which one the headline is most fragile to. ④ Attach a bottleneck checklist (which constraint binds first, its lead time) and cross-check top-down vs bottom-up counts within stated bands (G10/6Ps). ⑤ Say yourself where the number is weakest before a critic does.

### A2. Two-Stage Demand Model — 两段式需求建模 · G4
**When**: Forecasting technology-driven demand (copper, lithium, solar, EVs) where adoption is the driver.
**How**: ① Model demand as penetration rate × unit intensity (copper per EV × deployment scenarios), never a top-down guess. ② Compare the resulting deficit against historical analogue gaps to anchor price space. ③ Identify the supply-response lag (mine cycle 7–10 yrs > demand growth cycle) as the mechanism turning deficit into price. ④ Report scenario ranges, not a single target.

### A3. Revenue-Gap Audit — 收支缺口审计法 · G2
**When**: Judging whether a capex/基建 wave (AI, 5G, energy) is sustainable; testing "money flowing in" claims.
**How**: ① Derive the required end revenue from the investment via explicit multipliers (Nvidia run-rate ×2 GPU share of TCO ×2 user gross margin = terminal revenue needed). ② List "who must pay" and check actual amounts against it. ③ Re-run the same ledger on a schedule; the direction of the gap (converging or widening) is the referee. ④ Monitor revenue concentration — a single customer share is the first fragility alarm.

### A4. Demand Decomposition — 需求分解 · G6
**When**: Any consumer/top-line growth claim; same-store sales; market growth "quality" judgments.
**How**: ① Decompose growth into price effect × volume effect × customer count (Bain), or same-store sales into traffic × average check (McDonald's). ② Treat price-vs-volume divergence as the earliest turning-point signal (prices up, volumes down = demand problem, not pricing power). ③ Watch tier divergence: top clients still buying while the base shrinks is an offer/quality problem, not a demand problem. ④ Report both current- and constant-currency calibers when FX matters.

### A5. Trade-Down Detection Toolkit — 降级检测工具箱 · G6
**When**: Verifying "consumers are trading down" (or up) with multiple independent measures before concluding.
**How**: ① Measure the same phenomenon via ≥3 independent indicators: private-label share, average ticket, discount/promotion dependence, channel mix (outlet vs full-price), calorie/consumption models. ② Require mutual confirmation across measures before claiming a structural shift. ③ Confirm a "turning point" on BOTH demand side (perception surveys) and supply side (retailer margins/capability) (McKinsey). ④ Expect self-report bias in perception data and wait for post-period confirmation.

### A6. One-Time vs Structural Demand Split — 一次性与结构性需求分离 · G8
**When**: Pandemic/war/one-off boost beneficiaries; any demand spike followed by a cliff.
**How**: ① Model a "base demand" ex-shock and add shock demand as an explicit decaying overlay with a half-life. ② Track installed base vs forward demand; watch inventory build vs sell-through. ③ Use engagement/churn/usage as leading indicators before revenue turns. ④ Flag when management extrapolates the spike into capex and headcount (paying twice: overbuild + cliff).

### A7. Cross-Industry Transmission Map — 跨行业传导链 · G6
**When**: A shock (therapy, policy, price war) reprices adjacent industries.
**How**: ① Chain evidence node-by-node from source data (company disclosure, basket data) → behavior surveys → aggregate model; label the layer and sample size of every number. ② Rank exposed categories by substitution risk, not just revenue overlap. ③ Distinguish company-specific vs segment-wide vs macro factors before attributing cause. ④ Treat single-event-driven sector moves with thin underlying data as overreach until confirmed.

## B. 周期判断类 Cycle Judgment

### B1. Bear-Market Two-Leg Split — 熊市两腿拆分 · G1
**When**: Judging a drawdown's stage and end; macro/market downturns.
**How**: ① Split the decline into its valuation leg (rates/liquidity → multiple compression) and earnings leg (EPS revision cycle) and track each separately. ② Use earnings-revision breadth as the leading confirmation of a turn — not price. ③ Bind any level target to trigger and invalidation conditions. ④ Re-state the framework and refresh data every edition; keep the frame, not the point.

### B2. Cycle-Template Premise Check — 周期模板前提检验 · G2, G4
**When**: Before applying any "history repeats" template (memory cycle, commodity cycle, bubble analog).
**How**: ① List the template's key premises (demand elasticity, contract structure, cycle nature). ② Test each premise against current facts before running the template — HBM was AI-driven, not a commodity cycle (G2/SK Hynix). ③ Require ≥3 independent signals to resonate before acting (revisions breadth + inventory weeks + price momentum). ④ Surface internal analyst disagreement explicitly instead of hiding it.

### B3. Peak Decomposition — 峰值分解法 · G4
**When**: Any "peak demand / peak oil / supercycle" claim, bullish or bearish.
**How**: ① Decompose the aggregate claim by product × region before accepting it (gasoline peaks first via EV penetration; aviation/petchem later). ② When two sides argue over a peak, return both to their demand definitions and assumptions before debating numbers. ③ Check whether "peak" claims depend on policy paths (milestone vs forecast).

### B4. Structural-Bull Triple Confirmation — 结构性行情三确认清单 · G4
**When**: Calling any structural bull market in commodities/cyclicals.
**How**: ① Require all three confirmations before a structural bull: low inventories + low spare capacity + underinvestment. ② Separate the catalyst (war, policy) from the cause (chronic supply deficit) — never let an event pose as logic. ③ Validate upstream tightness with downstream price signals (crack spreads, refined products) so tightness is real, not speculative. ④ Never sweep "all commodities" into one claim — heterogeneity masks failure.

### B5. Leading-Indicator Discipline — 领先指标纪律 · G1
**When**: Confirming turns before price does; macro inflection calls.
**How**: ① Use leading variables (earnings-revision breadth, term spread, credit impulse) rather than price to confirm a turn. ② Declare the window and lag explicitly (yield curve leads recessions by 2–6 quarters — G1/Estrella-Mishkin). ③ Explain the transmission mechanism, not just the statistical correlation. ④ Compare candidate indicators against a baseline on the same data (pseudo-R², in/out-of-sample) before trusting one.

### B6. Cycle-vs-Structure via Equilibrium Rate — 均衡利率定周期/结构 · G1
**When**: "Is this cyclical or structural?" — secular stagnation, r*, deleveraging debates.
**How**: ① Estimate the equilibrium rate (r*) and its trend to classify the regime before forecasting. ② Give the structural claim testable mechanism implications plus a policy-response path (fiscal, inflation target, reform). ③ Support "this is not a new problem" with long history series. ④ Re-review long-cycle judgments periodically — policy or technology can interrupt them (2016+ US fiscal expansion).

## C. 估值类 Valuation

### C1. Bull/Base/Bear Scenario Tree — 情景树 · G8, G1
**When**: High-uncertainty growth names, macro indices, any target that must survive scrutiny.
**How**: ① Publish a bull/base/bear triplet with explicit per-branch driver assumptions (volumes, margins, share). ② Bridge every target revision to a per-share value change (waterfall). ③ Keep the base stable, revise the bands. ④ Attach probability only where supportable; flag the scenario that would break the narrative, not just the one you believe.

### C2. Valuation Tool Matching — 估值工具匹配业务 · G8
**When**: Choosing the valuation framework before computing numbers.
**How**: ① Match the tool to the business: scenario tree/DCF for high-optionality growth; SOTP (core + option value) for conglomerates and strategic bets — never blended; multiples for stable compounders. ② Identify the binding constraint first (demand, FCF, capital-market access). ③ For "long-term" narratives, demand segment P&L and pre-committed exit/milestone criteria before paying for them (Meta/Reality Labs).

### C3. Cyclically-Adjusted Valuation + Percentile — 周期归一化估值+分位 · G9
**When**: Market or sector valuation calls; "expensive/cheap" judgments.
**How**: ① Normalize with cyclically averaged earnings (CAPE-style), not single-period P/E. ② Report the historical percentile, not just the level. ③ Plot "current valuation → forward 10-yr return" scatter to show mean-reversion strength. ④ State the conditions under which the indicator fails (accounting changes, low-rate regime) before relying on it.

### C4. Incentive-Price Reverse Engineering — 激励/反推定价法 · G4
**When**: When forecasting price is hopeless but supply economics are knowable (long-horizon commodities).
**How**: ① Refuse point forecasting; instead back out the price that makes marginal supply economic — IRR hurdle × inflation scenarios. ② Write every assumption (IRR, inflation, penetration) explicitly so the result is recomputable and falsifiable. ③ Break demand aggregates to product/region before arguing peaks. ④ Remember incentive price ≠ market-clearing price; actual prices can sit far outside the range.

### C5. Total-Return Four-Factor Decomposition — 总回报四因子分解 · G9
**When**: Any long-horizon equity return forecast.
**How**: ① Decompose expected total return into earnings growth + dividends + buybacks + multiple change, and argue each item. ② When buybacks/dividends dominate, watch cash-flow quality rather than EPS growth. ③ Write the market view as "range + conditions" (interest-rate/growth regime), not a point. ④ State which regime combination invalidates the view.

### C6. Target Channel Bridge & Catalyst Chain — 目标价通道桥与催化链条 · G3, G2
**When**: Setting or re-rating any index/stock target; event-driven repricing (DeepSeek, policy turns).
**How**: ① Decompose every target into quantified channels: earnings + risk appetite + fund flows, each with its own number (G3). ② For events, build the full auditable chain catalyst → EPS → flows → target, and check which link actually moved (G2). ③ Diagnose the catalyst's nature first: micro-innovation vs macro-policy expectation. ④ State the dependency explicitly: "if earnings don't deliver, the target fails" (multiple compression).

## D. 信号验证类 Signal Verification

### D1. Thresholded Contrarian Signal + Statistical Disclosure — 阈值化反向信号与统计披露 · G1, G9
**When**: Positioning/sentiment/consensus indicators; contrarian calls.
**How**: ① Aggregate a survey/positioning measure into one 0–10 indicator with a threshold (≥8 = contrarian trigger). ② Disclose the full statistical record on every trigger: hit rate, average return, max drawdown, sample size. ③ Force an independent confirmation variable (ETF flows, sentiment-PMI divergence) before acting. ④ Treat extreme consensus (magazine covers, "Death of Equities") as the same family of signal; date-stamp narratives for later audit.

### D2. Multi-Signal Resonance — 多信号交叉验证 · G2, G6
**When**: Any directional call that rests on one observable; cycle and thematic turns.
**How**: ① Track ≥3 independent signals and require resonance before acting (revision breadth + price momentum + inventory). ② If signals conflict, surface the conflict explicitly rather than averaging it away. ③ For qualitative claims (trading down, resilience), require the same metric measured across consecutive years before calling a trend.

### D3. Survey Discipline — 调查纪律 · G6
**When**: Consumer/patient/executive survey claims; stated-preference data.
**How**: ① Publish sampling frame, fieldwork window, and margin of error with every survey claim (census-matched where possible). ② Use fixed rolling panels (monthly waves, cross-year comparable) before claiming trends. ③ Treat stated preference as a leading hypothesis only — triangulate with revealed behavior (basket, foot traffic, official stats). ④ A single cross-section cannot separate trait from trend.

### D4. Channel-Check + Hard-Data Dual Track — 渠道核查+硬数据双轨 · G2
**When**: Demand sustainability for suppliers/semis; pre-earnings checks.
**How**: ① Use first-hand channel verification (supply chain, customers, roadmap events) instead of pure model extrapolation. ② Always pair soft channel reads with hard data (order books, capacity, customer credit/backstop layering). ③ Pre-commit what counts as good news before the event ("Rubin ramp comment") to prevent post-hoc rationalization. ④ Label confirmed vs pending ("we heard X; we await the guide raise").

### D5. Independent Measurement vs Income Statement — 独立数据对抗报表 · G7, G6
**When**: Revenue/volume claims that management could inflate; fraud red flags.
**How**: ① Measure the business physically: field surveillance, foot traffic, satellite, store-level video — data management cannot rebut. ② Mirror the company's footprint in sampling design. ③ Hunt physically impossible data points (one user 25,843 orders/day) as smoking guns. ④ Cross-validate with third-party vendors (Placer.ai-style) before earnings.

### D6. Event-Evidence Discipline — 事件证据纪律 · G6
**When**: Clinical/regulatory/data events that reprice sectors.
**How**: ① Disclose case counts, sample size, interim vs final, and time window — they set the confidence interval (>90% on 94 cases ≠ the label). ② Translate endpoints into market size, pricing, and adoption scenarios. ③ Pre-commit the final-analysis threshold before the event. ④ Map which adjacent sectors reprice when the endpoint lands.

### D7. Versioned Recurring Map — 版本化定期地图 · G2, G6, G4
**When**: Any universe-level tracking (AI exposure, sentiment dashboard, annual outlooks).
**How**: ① Re-run the same universe/metric on a fixed schedule (3,600 stocks quarterly; 47th survey wave; WEO annually). ② Treat the map's own change as the signal (Adopter share 16%→30%). ③ Version every annual forecast: new data → updated scenarios → explicit revision reasons vs prior year. ④ Cross-year comparability breaks if the design changes — freeze methodology.

## E. 取证尽调类 Forensic Due Diligence

### E1. Internal-Consistency Audit — 报表内部一致性审计 · G7, G8
**When**: Screening any "high-growth" narrative; before trusting reported earnings.
**How**: ① Check earnings/ROE vs operating cash flow divergence — the earliest no-insider signal (Enron). ② Benchmark company margins against peers for unexplained gaps (SMCI vs Dell/HPE). ③ Mine footnotes for related-party SPEs and off-balance-sheet leverage. ④ Watch accruals-vs-cash divergence and mark-to-market black boxes.

### E2. Balance-Sheet Integrity & Cash Verification — 资产负债表完整性与现金物理核验 · G7, G8
**When**: Financial platforms, banks, any firm where cash is a headline asset.
**How**: ① Verify large cash balances with a third party directly — trustee-sent screenshots/emails count as possible forgeries (Wirecard's €1.9B). ② For platforms: test client-asset segregation and custody before revenue quality; check disclosed reserves against liabilities. ③ Treat auditor resignation, delayed filings, and restatement history as hard material events. ④ Follow the intermediaries doing the real work — fraud hides in third-party agents.

### E3. Inverted Incentive Attribution — 激励归因倒置 · G7
**When**: Explaining why a business behaves the way it does; fraud discovery.
**How**: ① Study the side paid by volume while holding no risk: lenders not borrowers (Burry), channels not brands (Valeant), suppliers not customers (SMCI). ② Ask who gets paid by volume and who actually holds the risk after securitization/structuring. ③ Use the incentive structure to predict behavior, then verify against observed conduct.

### E4. Ownership/Supply-Chain Penetration Map — 股权与供应链穿透制图 · G7
**When**: Related-party suspicion, shell structures, opaque supply chains.
**How**: ① Draw the ownership/shell network from public filings across jurisdictions (Mauritius shells → listed entities via swaps). ② Trace fund flows node by node; map family-controlled suppliers and their margin impact. ③ Cross-check exports/customers against sanctions lists. ④ Benchmark margins after stripping related-party effects.

### E5. Auditor-Fit Red Flags + Bayesian Prior — 审计错配与历史先验 · G7
**When**: Any fraud-probability assessment.
**How**: ① Flag auditor-client size mismatch (tiny firm auditing a giant conglomerate). ② Use auditor resignation, delayed 10-Ks, and restatement history as Bayesian priors that raise fraud probability. ③ Treat "aggressive but legal" accounting as a thesis, not just fraud hunting. ④ Independently assess the accuser's credibility: track record, incentives, wolf-cry history.

### E6. Evidence Grading & Pre-Archiving — 证据分级与预归档 · G7
**When**: Publishing allegations or claims an adversary would attack.
**How**: ① Grade evidence: documentary > corroborated testimony > circumstantial; label each claim's grade. ② Make every allegation independently verifiable so opponents cannot break one link and collapse the chain. ③ Archive anything that can vanish (Wayback) BEFORE publishing. ④ Pair fraud claims with a pure valuation leg kept independent of them.

### E7. Cross-Caliper Verification — 交叉口径核验 · G3, G8
**When**: Official/company numbers that will be contested (leverage, GDP, growth).
**How**: ① Rebuild the reported number with self-constructed micro data (off-balance-sheet guarantees, JV debt, trust financing → true net debt 170% vs reported 108%). ② Treat a contradiction between behavior and numbers (aggressive land buys vs cash claims) as a research trigger. ③ Cross-check official aggregates against independent calibers (self-built, alternative series, foreign-country data). ④ Classify every datapoint as blip or turn by checking series context before interpreting.

### E8. Objective-Metric Priority — 客观指标优先法 · G5
**When**: The subject controls its own scorecard (capital adequacy, fair value, "long-term" strategy).
**How**: ① Pick a metric the subject cannot define or dress up (tangible equity/tangible assets over Tier-1; statutory filings over company marks). ② Compute it across all peers to build a ranking. ③ Cross-validate with two independent signals (fund flows, valuation). ④ Anchor the conclusion to one observable trigger event (dividend cut) so it is checkable.

### E9. Vulnerability & Blowup Checklist — 脆弱性与爆仓检查清单 · G5
**When**: Any leveraged institution, bank, fund, or systemic-stability review.
**How**: ① Run the blowup trinity: maturity mismatch × concentration × high leverage — any leverage subject first passes this gate (LTCM). ② For systems, review the four quadrants: valuations / debt & leverage / external & funding / contagion & spillovers (IMF GFSR). ③ Translate every qualitative risk into a measurable indicator (spreads, VIX, funding-pressure indices). ④ Quantify tail scenarios over point forecasts.

### E10. Counterfactual Attribution — 反事实归因 · G5
**When**: "Was this crisis/outcome avoidable?" attribution and policy lessons.
**How**: ① List ALL candidate causes before weighting any (nine-dimension enumeration — FCIC). ② Require evidence, not narrative, per cause. ③ Judge "avoidable" by explicitly constructing the counterfactual world ("if reform X had existed") before assigning blame. ④ Publish dissenting views alongside conclusions — read the dissent before citing the conclusion.

## F. 政策分析类 Policy Analysis

### F1. Policy Scoring Parameterization — 政策打分参数化 · G6, G1
**When**: Estimating the market/budget impact of a statute or policy.
**How**: ① Translate statute → mechanism → parameterized price/budget effect → scored output (CBO negotiation: 57–75% discounts, $100B savings). ② Label every assumption so anyone can re-run the model. ③ Split static (price) from dynamic (innovation/R&D) effects explicitly — dynamic is the most contested. ④ Treat any institutional score as versioned; re-score as implementation details emerge.

### F2. Two-Layer Policy Analysis — 两层面政策分析 · G3
**When**: Policy/regulatory shocks (crackdowns, tariffs, subsidies).
**How**: ① Quantify the fundamentals layer first: the policy's impact on the earnings curve; update targets. ② Judge the pricing layer independently: has the market overshot? ③ Act only when the layers diverge (earnings cut but price overcorrected = buy). ④ Distinguish structural regulation from cyclical disturbance — mislabeling produced repeated buy-the-dip losses (2021-22 China tech).

### F3. Condition Checklist Discipline — 条件清单纪律 · G3, G1, G2, G4
**When**: Any forecast, scenario, or bold thesis — before and after.
**How**: ① BEFORE forecasting: enumerate observable gate conditions (vaccination coverage, policy levers, capacity) and track them — never bet on timing (G3). ② AFTER concluding: write the invalidation conditions — "what would make this wrong" — for every optimistic/pessimistic conclusion, converted into trackable trigger variables (G1, G2, G4). ③ The hedge word in your title is a falsification condition — revisit it. ④ Spell out which policy change would break the trend.

### F4. Reaction-Function & Terminology Dictionary — 反应函数与术语字典 · G1
**When**: Central-bank and policy-maker analysis.
**How**: ① Analyze the framework parameters and reaction function, not single-point forecasts. ② Maintain a wording-change dictionary — "deviations" → "shortfalls" is a policy-turn early signal. ③ Translate framework changes into market-pricing meaning (higher inflation tolerance → higher nominal anchor). ④ Audit framework promises against subsequent actions, not words.

### F5. Policy-Put Lever List — 政策工具箱逐项清单 · G3
**When**: Markets driven by policy support expectations (China, fiscal, rate paths).
**How**: ① Itemize the policy levers one by one (each tool gets its own check). ② Track each lever's status; state what prices already imply vs consensus. ③ Price the policy put as asymmetric payoff, not a point. ④ Write "if policy support doesn't deliver, the target fails" explicitly.

### F6. Disclosure-as-Policy — 披露即政策 · G5
**When**: Stress tests, regulatory transparency, credibility-restoring events.
**How**: ① Define one uniform adverse scenario, not per-firm custom. ② Apply uniform methodology/calibers so results are comparable. ③ Disclose results at both aggregate and individual levels — credibility comes from publishing bad news. ④ Attach an enforced, dated remediation plan (capital raise); disclosure without a deadline is PR.

### F7. Regulatory-Caliber vs Market-Pricing Gap — 监管口径vs市场定价对照 · G5
**When**: Capital instruments (AT1/CoCo), regulatory capital, any regime-vs-market tension.
**How**: ① Read the instrument's loss-absorption clauses, not its marketing label (AT1 = equity pretending to be debt). ② Place regulatory treatment and market pricing side by side; a break (AT1 counted as capital but priced as equity) is an early-warning signal. ③ Map the holders to see who absorbs surprise losses; complex instruments flowing to retail = governance failure. ④ Treat regulatory discretion itself as a risk variable.

## G. 量化验证类 Quantitative Verification

### G1. Mimicking-Factor Construction + Double-Sort — 模仿因子+双排序回归 · G9
**When**: Testing whether a "premium" or economic story is real and tradeable.
**How**: ① Translate the story into tradable sorted portfolios (size × BM double-sort → SMB/HML mimicking factors). ② Estimate factor loadings with time-series regressions; report t-values. ③ Check the new factor's correlation with known factors before adding it (factor-zoo overfitting). ④ Report construction choices (breakpoints, equal vs value weights) — they change conclusions.

### G2. J/K Formation-Holding Recipe + Overlapping Samples — J/K形成-持有配方 · G9
**When**: Any factor/strategy backtest that must withstand scrutiny.
**How**: ① Sort into deciles on a J-month formation window, hold K months (momentum standard). ② Use overlapping portfolios to enlarge observations; test a formation×holding grid. ③ Report returns before AND after transaction costs, plus liquidity constraints. ④ Test seasonal (January reversal) and extreme-tail behavior (momentum crashes) explicitly.

### G3. Black-Litterman Reverse Optimization — 反推均衡+贝叶斯融合 · G9
**When**: Portfolio construction where MVO input sensitivity destroys stability.
**How**: ① Reverse-optimize market weights to implied equilibrium returns as the base. ② Express views as "return + confidence" structured inputs. ③ Blend by confidence to posterior returns; use as optimizer input. ④ Never feed single-point hand-made expected returns into MVO; external-review your views — garbage in, garbage out.

### G4. Crisis Simulation Replay — 危机模拟回放 · G9
**When**: Explaining a quant/leverage crisis; attributing losses without hindsight narrative.
**How**: ① Reconstruct the strategy's P&L from public data and replay the shock (Khandani-Lo August 2007). ② Model the cascade: one fund deleveraging → same-sign crowded strategies squeezed. ③ Monitor crowding (correlation, leverage) as a risk variable more important than the model. ④ Stress-test for leverage contraction + liquidity dry-up, not just equity bears.

### G5. Skill-vs-Luck Base-Rate Audit — 技能vs运气基率审计 · G9
**When**: Evaluating any track record, strategy, or "master" claim.
**How**: ① Compute the base rate: how many would outperform under randomness alone? ② Check for survivorship and sample-selection bias first. ③ Require methodological clustering — a whole village of outperformers beats a single lucky tail. ④ Prefer record length and consistency over return height.

### G6. Robustness Suite — 稳健性检验套件 · G1
**When**: Any empirical threshold, average, or headline conclusion.
**How**: ① Re-run over alternative sample periods, groupings, and weightings. ② Report mean AND median (means are outlier-contaminated — Reinhart-Rogoff). ③ Disclose data + code as the floor of credibility; re-run original data before citing any threshold-type finding. ④ Distinguish correlation from causation explicitly.

### G7. Probabilistic Modeling + Consensus Gap — 概率化建模+共识对照 · G1
**When**: Macro/econ predictions, recession calls, policy paths.
**How**: ① Formalize the question as a probability model, not a binary judgment (probit on term spread → recession probability). ② Compare candidate indicators against baseline on the same data (pseudo-R², in/out-of-sample). ③ Show the numeric gap vs consensus beside your own number. ④ Calendarize the path (policy rate, GDP) for ex-post audit.

### G8. State-Dependent Correlation & Stress-Test Suite — 状态依赖相关性与压力测试套件 · G9, G5, G10
**When**: Diversification/asset-allocation claims; portfolio risk review.
**How**: ① Attach the failure macro-state to every diversification claim (inflation shock → stocks/bonds correlation flips positive — 60/40 2022). ② Monitor rolling correlations, not long-run averages. ③ Stress-test with inflation/rate shocks and liquidity dry-up, not just equity bears (SCAP scenarios; Taleb's "impossible" shocks). ④ Under fat tails, size for survivability and use barbell/convexity rather than prediction accuracy.

### G9. Backtest Crowding Audit — 回测拥挤度审查 · G9
**When**: Trusting any backtested edge.
**How**: ① Ask: how much same-sign capital is already trading this? ② Treat strategy crowding (correlations → 1 in stress) as the fatal backtest blind spot. ③ Distinguish sample-in fit from out-of-sample validity; a factor zoo is an overfitting signal. ④ Report which regime invalidates the edge.

## H. 主题叙事类 Thematic Narrative

### H1. Necessity Ladder + Falsifiable Anchor — 必要性阶梯+可证伪锚点 · G10, G2
**When**: Building a theme (labor, power, AI, geopolitics) into an investable thesis.
**How**: ① Start from a world-scale necessity (labor scarcity, power, data), not sector popularity. ② Force every theme to carry ONE falsifiable quantity plus a date (GWh, units, adoption %) and a timetable. ③ Map the cross-industry winner/loser transmission chain using a beneficiary taxonomy (Enabler/Adopter/Disrupted/Protected/Wildcard — G2); quantify each winner claim. ④ Write the counter-thesis inside the same document, not in a risk appendix. ⑤ No anchor = narrative, not a thesis.

### H2. Event-Mechanism Decomposition — 事件机制拆解 · G10
**When**: Extreme events (squeezes, negative prices, crashes) that attract sentiment narratives.
**How**: ① Decompose the event into participant rules × feedback loops × institutional/physical constraints (GameStop: retail flow → dealer gamma → short covering). ② Identify the forced transactor and whose hedging rule amplifies (dealers, ETFs). ③ Check structural preconditions (borrow cost, options volume, storage) BEFORE attributing to sentiment. ④ Explain extreme prints via the constraint chain, not a demand story; distinguish the headline index from what readers actually hold.

### H3. Incentive-Reversal Test — 激励反转测试 · G10, G4
**When**: Any "algorithmic guarantee," arbitrage loop, or paradigm assumption ("battery costs must fall", "peg holds").
**How**: ① Model each actor's incentive under both normal and stressed states (Terra: depeg converts the guarantee into a sell engine). ② Ask who becomes a forced seller in the failure state. ③ Surface and stress-test the sector's implicit paradigm assumption instead of accepting it (MS lithium named "battery costs must keep falling" as belief, not law). ④ Treat unbacked claims (peg, TVL, yield) as narrative until a real withdrawal test.

### H4. Narrative Datafication — 叙事数据化三问 · G10
**When**: Media-coined concepts ("Great Resignation", "peak X", "trading down") driving markets.
**How**: ① Rebuild the concept from primary official series (quits rate, participation, vacancies) — official-data-first is the cheapest antidote to narrative drift. ② Decompose the aggregate by group and time (demographic, region, product). ③ Classify structural vs cyclical vs transient before concluding. ④ Let numbers arbitrate the media story; expect data revisions to rewrite it.

### H5. Identification ≠ Timing Split — 识别≠时点分离 · G10, G9
**When**: Bubble/overvaluation calls; any "expensive" thesis.
**How**: ① Write "is it expensive?" and "when does it burst?" as two separate statements, never merged. ② Score bubbles against a pre-written four-element checklist (extreme valuation percentiles, accelerating price action, irrationality markers, systemic fragility — G10/Grantham). ③ Express downside with probabilities, not dates. ④ Treat "this time is different" and extreme consensus as contrarian alarms; single-point targets require probability + invalidation conditions (G9).

### H6. Scenario Discipline Trio — 情景纪律三件套 · G4, G3
**When**: Any scenario/outlook under deep uncertainty (energy, macro, geopolitics).
**How**: ① State explicit assumptions (technology, policy, behavior) up front, plus a milestone checklist so reality can be tracked against the scenario. ② Mark every output as scenario vs forecast — a scenario asks "what could happen under these assumptions"; a forecast bets on one path. ③ Back-cast from a top-down constraint (carbon budget, policy mandate) rather than only extrapolating trends. ④ Publish scenario families with version management (what changed vs last year and why).

### H7. Testable Historical Analogy — 可检验历史类比 · G3, G1, G4
**When**: "It's like Japan / 2000 / the 2000s supercycle" arguments.
**How**: ① Enumerate the "like" indicators (credit impulse, private-sector deleveraging, property prices) AND the "unlike" indicators (capital controls, state share, policy toolkit). ② Track the series month by month; analogies are maps, not destinations — watch whether the "unlike" conditions still hold. ③ Use multi-country, multi-decade pattern matching ("like/unlike" checklist) to avoid single-sample over-extrapolation (G1). ④ Anchor reversal to supply clearing / physical series rather than demand optimism (G3).

### H8. Mechanism/Identity Skeleton First — 恒等式/机制骨架先行 · G1, G2
**When**: Any macro/flow question where the choice of lens determines the answer.
**How**: ① Choose the analytic identity or mechanism before the data: three-sector identity (fiscal + private + external = 0), saving-investment flows, bear-market two legs — the same phenomenon changes attribution with the lens (G1). ② Quantify the total ledger first (total investment, total spend) before arguing returns — "money flowing in" is not evidence (G2). ③ Locate the current stage in the cycle/template before forecasting. ④ Use flow data rather than narrative to judge capital direction.

---

# Chapter 3 — Writing Canon 行文范式

> The language and structural conventions that make a report read like Wall Street research.

## 3.1 Opening Sentence Formula 开头句公式
- **Lead with the number and the delta**: "Bull & Bear rose 7.9→8.5, triggering the 16th contrarian signal since 2002 (63% historical hit rate)." / "We see a 15% recession probability vs market fears of 40%."
- **Formula**: `[Measurable fact/level] + [what it implies] + [vs-consensus or vs-history delta] + [one-line stance]`.
- **Title as thesis**: a narrative hook is fine ("The Final Descent", "Copper is the New Oil", "Fire and Ice") but the body must immediately go numeric and flat — no emotional words (G1/GS). Title hedging words ("yet", "for now") ARE falsification conditions — keep and revisit them (G3).

## 3.2 Rating & Target-Price Expression 评级与目标价表达
- **Never a naked point target**: publish bull/base/bear or a range+conditions; every target carries its earnings/valuation/flows channel decomposition (G3) and its trigger/invalidation conditions (G1).
- **Express moves as ranges or bands**: "+15–20% fair value", "MSCI China 75→85" with the chain behind it (G2). A target revision must be bridged to per-share value change (G8).
- **Rating = stance + probability + horizon**: "Overweight — 60% probability of base case over 12 months." If you cannot attach a probability, say so (G1).
- **Incentive-price calls**: report the price that makes supply economics work rather than a forecast level (G4).

## 3.3 Number Presentation Rules 数字呈现规则
- Every number gets its unit, its time window, its source, and its caliber (constant vs current FX, nominal vs real, mean vs median).
- Headline numbers come with their fragility statement: "sensitive to minor tweaks in penetration" (G6) or a sensitivity grid.
- Report mean AND median for bucket averages; report pre- and post-cost returns for factors; report both sides of the estimate where methods differ (G5).
- Percentages without denominators are forbidden: "77% of consumers" requires n= and sampling frame (G6).
- Distinguish confirmed vs estimated vs pending explicitly ("we heard X; we await the guide").

## 3.4 Chart Citation Norms — Exhibit N 图表引用规范
- Every chart is an "Exhibit N" referenced by number in the text ("Exhibit 1 shows the three-sector balance at zero") — never an uncited figure (G1/JPM).
- Every exhibit carries a source footnote, a date, and a caliber note (G2/Meeker: every slide footnoted; G6/UBS: methodology box before findings).
- The text must tell the reader what to see in the exhibit ("the divergence begins in 2022Q3") — a chart is evidence, not decoration.
- One figure-one point: an exhibit supports a single claim; do not overload (G9/FF: tables as evidence, not ornament).

## 3.5 Tone Discipline — 自信但可证伪 语气纪律
- **Confident, specific, falsifiable** — never "could go either way" as a stance, never hype as analysis (G2/Ives is the anti-pattern: emotion for positioning, not for valuation).
- **Concession is a strength**: "63% accuracy is not perfect" (G1); "a pessimist could still be right" (G2); "we were early — that is on us" (G7/SK Hynix public close).
- **No emotional adjectives** in the evidence body; reserve vivid framing for the title and exec summary only (G1/GS).
- **Disclose what you excluded**: models must state their boundary ("we exclude multiplier effects and policy offsets" — G5/Hatzius).
- **Own your mistakes publicly** — it is the cheapest credibility purchase available (G2/Morgan Stanley closing the SK Hynix sell; G7/Soros publishing his own wrong calls).

---

# Chapter 4 — Chart Canon 图表规范

> Chart type → what it expresses, distilled from the 10 groups' chart styles. Every chart: source footnote, date, caliber note, and an "Exhibit N" reference in text.

## 4.1 Chart-Type → Purpose Mapping 类型→用途映射表

| Chart type 图表类型 | Expresses 表达什么 | Sources | Key specs |
|---|---|---|---|
| **K-line / price+volume timeline 价格量时间线** | Event chronology, squeeze mechanics, milestone arcs (price ≠ fundamentals) | G10 GameStop; G8 Tesla/Peloton arcs | Overlay short interest/options OI/borrow rate; mark event dates; never present price alone as fundamental evidence |
| **Valuation band / percentile fan 估值带与分位扇形** | Where valuation sits vs history; "expensive/cheap" with mean-reversion context | G9 CAPE/Shiller; G3 A/H premium; G1 scenario bands | Cyclically adjusted earnings; percentile axis; draw the historical range band; add forward-return scatter for mean-reversion strength |
| **Financial trend / revision breadth 财务趋势与修正广度** | Earnings direction, revisions breadth as leading indicator | G1 Wilson revisions breadth; G2 margin-diff; G8 anchor-KPI vs consensus | Rolling revision breadth; consensus-vs-actual markers; include the anchor KPI's falsification threshold |
| **Scenario tree / waterfall bridge 情景树与桥接瀑布** | Bull/base/bear branches with driver assumptions; target-revision reconciliation | G8 Tesla scenario tree; G3 target bridge; G2 gap chart | Each branch labeled with drivers + probability; waterfall bridges every revision to per-share value; per-branch P&L |
| **Comparison bar / peer matrix 对比条形图与同业矩阵** | Rankings, gaps vs peers, polarization, exposure heatmaps | G5 Whitney TE/TA peer rank; G6 polarization; G2 AI-exposure heatmap | Same metric across all peers (subject cannot redefine); color = direction of gap; heatmap cells carry values |
| **S-curve / adoption + cost curve 渗透率S曲线与成本曲线** | Adoption speed vs history; cost-decline trajectory | G2 Meeker/ARK; G4 copper intensity; G10 MS 2030 | Same coordinate system as historical technologies; mark current position; show regression + confidence interval, extrapolation = "待检验信念" |
| **Causal chain / mechanism diagram 传导链与机制图** | Link-by-link transmission (micro→macro, catalyst→EPS→flows→target) | G5 Hatzius; G2 DeepSeek chain; G10 LUNA/GameStop loops | Each node = a data point; arrows = mechanism with lag; flag which link actually moved |
| **Fund-flow / ownership map 资金流与股权穿透图** | Where money flows, who controls whom, forced transactors | G7 Adani/Valeant/Wirecard; G3 A/H flows | Trace to the final buyer/entity; label each node; shell/offshore entities highlighted |
| **Timeline / milestone checklist 时间线与里程碑核查表** | Scenario tracking, policy paths, event sequences | G4 IEA milestones; G1 calendarized path; G5 LTCM timeline | Dated events + policy responses paired; milestone vs actual markers; versioned across editions |
| **Summary table / exhibit table 汇总表（证据型表格）** | The evidence itself: buckets, cohorts, comparisons | G1 Reinhart-Rogoff tables; G9 FF factor tables; G7 vintage cohorts | Table = evidence, not decoration; report mean+median; note sample, window, weighting |

## 4.2 Making Specs 制图规范
- **Colors**: one neutral base (gray/black) for context; ONE accent color for the thesis line; red for risk/negative, green for positive only when direction is unambiguous. Heatmaps: sequential single-hue scale; diverging (red→white→blue) for gaps. Avoid rainbow — each color must carry meaning.
- **Annotation**: every chart names the takeaway in 1 line ("Divergence begins 2022Q3 — price up, volume down"); mark thresholds (trigger levels, falsification bands) with dotted lines and labels; label the final datapoint with its value.
- **Source footnote**: `Source: [institution], [date], caliber: [constant/current FX, real/nominal, mean/median].` Every exhibit gets one (G2, G6). No invented series — rebuilt data carries its construction note.
- **Scale honesty**: percentiles on valuation charts, log scale for cost curves, dual-axis only when the two series are explicitly linked (price vs volume). Never truncate a y-axis to exaggerate a move.
- **Scenario charts**: fan/band charts carry probability labels per branch; scenario vs forecast marked on the chart itself (G4).

---

# Chapter 5 — Evidence Discipline 证据纪律

## 5.1 Evidence Grading 证据分级
- **Tier 1 — Documentary/primary**: official filings, statutes, contracts, third-party confirmations (cash confirmed by counterparty, not screenshots — G7/Wirecard).
- **Tier 2 — Corroborated testimony**: named sources, multiple independent confirmations (ex-employees, channel interviews with hard-data backup — G7/Nikola).
- **Tier 3 — Circumstantial/inference**: accounting red flags, incentive analysis, "behavior contradicts numbers" triggers (G7, G3).
- **Rule**: every claim in a report is labeled by tier; allegations published against a subject must be independently verifiable — one broken link must not collapse the chain (G7/Adani). Soft evidence ("we heard X", "management sounds happy") is labeled soft and paired with hard data (G2/Rasgon).

## 5.2 Caliber Discipline 口径纪律
- Every number carries its caliber: constant vs current FX (G6/Bain — can flip the headline), real vs nominal, mean vs median (G1/RR), reported vs self-rebuilt (G3/UBS 170% vs 108%), scenario vs forecast (G4/Shell).
- When two camps disagree, return to definitions and assumptions before arguing numbers (G4/WEO peak debate).
- Decompose aggregates before accepting them: product × region (G4), price tier / customer tier / city tier (G6), structural vs cyclical vs transient (G10/BLS).
- Headline ≠ instrument: distinguish what the reader actually holds/trades from the index everyone quotes (G10/negative oil).

## 5.3 Source Citation Rules 来源标注规则
- Every number, chart, and claim gets a source + date; charts carry Exhibit numbers and source footnotes (Ch4).
- Verify links before citing — URLs rot and get repurposed (G5/Whitney list; G1); cite the underlying primary source, not a media relay, and note when the URL in a checklist no longer points where claimed.
- Version-stamp institutional numbers: scores get revised (G6/CBO), official data gets revised (G3/G10) — record the version and the as-of date.
- Label the author's incentive: a company's own scenario is not independent evidence (G4/bp); a short seller's claims carry their incentives (G8); a decision-maker's narrative is self-serving until triangulated (G5/Bernanke ↔ FCIC ↔ external criticism).
- Public data + reproducible code is the floor of credibility for any threshold/empirical claim (G1/RR Excel affair).

## 5.4 Triangulation Requirements 三角验证要求
- Stated preference must be paired with revealed behavior (G6 — survey + basket/traffic/official stats).
- One datapoint is a blip, not a turn — check series context (G3/population); one cross-section cannot separate trait from trend (G6).
- Surveys need dual independent respondent groups where claims are structural (executive + consumer — G6/McKinsey).
- Insider/internal narratives are read against official attribution and external criticism (G5).
- Official aggregates are hypotheses until cross-checked with self-built or foreign-caliber series (G3/IMF).

---

# Chapter 6 — Red Flag Checklist 红旗清单

> All lessons/red flags from G1–G10, deduplicated. One sentence each; (G#) = source group. If ≥2 flags fire on your draft, rewrite before publishing.

**论证与证伪类**
1. A signal/indicator is only valid at extremes; in the normal range it is noise (G1).
2. Hit rates near a coin flip (63%) are not an edge without trend and breadth confirmation (G1).
3. A "concession" sentence is only a shield if the falsification condition it names is actually trackable (G2).
4. Trend statements that cannot be falsified ("AI is transformative") are commentary, not research (G2, G10).
5. Single-point targets without probability distribution are unfalsifiable (G9).
6. "This time is different" without a testable decomposition is the classic top-of-cycle rhetoric (G2, G9).
7. "Costs always fall" / "demand always grows" treated as law rather than belief breaks at regime change (G4, G10).
8. Circular reasoning: using the same variable as both result and evidence (low rates as proof of stagnation) (G1).
9. A framework published as "principle" with no specific falsifiable prediction cannot be audited later (G1).
10. A model that omits feedback loops systematically understates tails (G5).
11. Loss/impact estimates that assume their own answer ("cat chasing its tail") (G5).
12. Correlation reported without mechanism or lag is a headline, not a finding (G1).
13. Cherry-picking only the consensus indicators that support your view (G1).
14. A single-sided narrative where every variable supports the thesis and tails are unquantified (G1, G8).

**数据与口径类**
15. A headline number survives while its range is dropped — the point is the risk, not the estimate (G6).
16. Official aggregates are hypotheses; un-cross-checked official numbers over-trust (G3).
17. One data point interpreted as a trend (a blip read as a turn) (G3).
18. Mean-only averages are outlier-contaminated; report median and robustness (G1).
19. Constant vs current FX can flip a headline — always check both (G6).
20. Sampling frame, fieldwork window, and margin of error missing from a survey claim (G6).
21. Stated preference presented as revealed behavior (G6).
22. An online survey over-represents digital-savvy consumers (G6).
23. Single-cross-section conclusions presented as trends (G6).
24. Aggregates that hide where losses actually concentrate (thin JIT buffers) (G10).
25. A "peak" accepted at aggregate level without product × region decomposition (G4).
26. Citation of a link/URL without verifying it still points to the claimed source (G5, G1).

**估值与点位类**
27. Point targets are fragile; the framework is the deliverable (G1, G4, G8).
28. Extreme ranges used as hedging statements while the real thesis lives elsewhere (G8).
29. Markets trade the delta between scenarios and the narrative, not the base case (G8).
30. Milestone coverage without the bear case is cheerleading (G8).
31. "Long-termism" claims without segment data and exit criteria are unfalsifiable (G8).
32. A target that depends on earnings follow-through without the dependency stated (G3).
33. Multiples paying for growth duration while the anchor KPI already decelerates (G8).
34. Valuation inputs controlled by the subject (fair value, self-marked marks) accepted at face value (G5, G7).
35. An identification call ("expensive") silently converted into a timing call ("sell now") (G10).
36. Structural judgments treated as permanent without periodic re-review against policy/tech change (G1).

**叙事与情绪类**
37. "Money flowing in" is herd behavior, not evidence of fundamentals (G2).
38. Extreme consensus (covers, manias) is a contrarian signal; perfect self-consistency of a story is when risk is highest (G9).
39. Concept-swap in transmission ("exposure" reported as "unemployment", "fraud-identified" as "worthless") (G2, G7).
40. A single CEO comment or event repricing a sector while underlying data is thin = event-driven pricing detached from fundamentals (G6).
41. One-time demand extrapolated into capex and trend (paying twice) (G8).
42. Media narrative outrunning the underlying official series (G10).
43. A company's own scenario/corporate research treated as independent evidence (G4).
44. Hype-driven reports used as valuation when they are only positioning/emotion signals (G2).

**时序与执行类**
45. Right but too early is functionally equivalent to wrong (G3, G7, G8).
46. Thesis correct ≠ timing correct ≠ position correct — three independent risks (G8).
47. Correct thesis + wrong market regime (momentum) = loss; don't short narrative stocks on fundamentals alone (G7).
48. Fraud identified ≠ permanent value destruction — judge survival separately (G7).
49. One success licenses overconfidence ("I was right once, therefore always") (G4, G5).
50. Frameworks assume conditions that change: elasticity, crowding, correlation, contract structure — premise-check every template (G4, G2, G9).
51. Disclosure without an enforced deadline is PR, not policy (G5).
52. Regulatory silence or political protection is both a red flag and the biggest execution obstacle (G7).
53. Backtests ignore crowding — strategy edge dies when copied (G9).
54. Rare events are underrepresented in any sample — backtest complacency (G10).
55. Exit on hypothesis breakage, never hold against evidence out of price conviction (G7).

---

# Chapter 7 — Red Team Question Bank 红队质询问题库

> A red-team officer (or the author self-auditing) asks these of the draft. Grouped by dimension; each question is directly usable as-is.

## 7.1 Thesis Falsifiability 论点可证伪性
1. What single observation, if it appeared tomorrow, would prove this thesis wrong — and is it in the report?
2. Is every claim translated into a measurable indicator with a threshold, or is any left as an uncheckable trend statement?
3. Where is the "this time is different" assertion, and is it decomposed into testable items against history?
4. Does the thesis have an explicit invalidation-condition list, and can each condition be tracked month to month?
5. Is the stance binary or hedged into unfalsifiability — could a reader verify you were wrong within 12 months?
6. Are the scenario and the forecast clearly labeled as different things?
7. Does the concession sentence name a real falsification condition, or is it a rhetorical shield?
8. If the report is right on direction but wrong on timing, does it say what that costs?

## 7.2 Data Quality 数据质量
9. What is the source, date, and caliber (constant/current FX, real/nominal, mean/median) of every headline number?
10. Which numbers are official aggregates taken on faith instead of cross-checked with independent calibers?
11. Are survey claims accompanied by sampling frame, fieldwork window, sample size, and margin of error?
12. Is stated preference anywhere presented as revealed behavior without a hard-data triangulation?
13. Are means reported without medians, or robustness checks omitted, on bucket averages and thresholds?
14. Which link in the evidence chain has no data node — and why was it skipped?
15. Does the model state what it excludes (feedback loops, policy offsets, multiplier effects)?
16. Are any estimates circular — assuming the answer in the inputs?
17. Have the cited sources and URLs been verified to still point where claimed?
18. Was the raw data re-run before citing a famous threshold (e.g., 90% debt/GDP)?

## 7.3 Valuation Logic 估值逻辑
19. Why is this valuation tool the right one for this business, and what would be the wrong tool?
20. Is the target expressed as a range/band with per-branch drivers, or as a naked point?
21. What is the implied risk-premium or growth-duration assumption baked into the multiple — and is it plausible?
22. Does the target decompose into earnings + valuation + flows channels, each quantified?
23. If earnings don't deliver, does the target fail — and is that dependency written down?
24. Which scenario would break the narrative, and is it given the same detail as the base case?
25. Are "long-term" claims backed by segment P&L and pre-committed exit/milestone criteria?
26. Does the valuation survive a percentile check against history, or is it anchored only to a favorable window?

## 7.4 Missing Bear Case 反方遗漏
27. Where is the strongest version of the opposing argument, stated fully and then answered?
28. Which consensus indicator that contradicts you was left out of the comparison?
29. Is the bear case in the body of each theme or buried in a risk appendix?
30. What would a smart adversary say on the first page of their rebuttal — and is that already addressed?
31. For single names: is the company's own likely rebuttal anticipated and answered point-by-point?
32. Are the incentives of every source disclosed — who wrote this, what do they gain?
33. If the report is bullish, where is the quantified tail scenario; if bearish, where is the recovery case?
34. Is there a counterparty who could fight this thesis for years, and is the plan sized for that?

## 7.5 Narrative Traps 叙事陷阱
35. Which emotionally loaded words ("revolutionary", "gold rush", "transformative") appear in the evidence body, and what number replaces each one?
36. Is "money flowing in" being treated as evidence of fundamentals rather than herd behavior?
37. Is a media concept being cited without rebuilding it from primary official series?
38. Which aggregation hides the story — is the claim decomposed by product/region/tier before concluding?
39. Is extreme consensus being read as confirmation rather than as a contrarian alarm?
40. Is a scenario presented with a confidence its assumptions do not support?
41. Is the title's hedge word ("yet", "for now") actually tracked as a falsification condition?
42. Is the narrative being priced while the underlying data is still thin (single-event repricing)?

## 7.6 Timing & Mismatch 时间错配
43. Are identification ("it is expensive") and timing ("it bursts now") kept as separate statements?
44. How long could the thesis be right but early, and does the funding/position survive that gap?
45. Is the conclusion encoded with an exit trigger, or is there only a target?
46. Are thesis, timing, and position sized as three independent risks?
47. Does the call carry probability + invalidation + exit, or is it a one-way extrapolation?
48. Which assumptions (elasticity, correlation, crowding, contract structure) could flip before the horizon — and is each re-checked?
49. Is the policy/econ path calendarized so it can be audited after the fact?
50. If the report is a versioned forecast, does it state what changed vs last year and why?

---

*End of manual. Ch1 gives the skeleton, Ch2 the toolbox (60 deduped methods), Ch3–5 the style and evidence law, Ch6 the pre-publish self-check, Ch7 the adversarial audit. Sources: G1–G10 digests (100 reports), all cross-group overlaps merged; the most complete expression was kept for each merged item.*
