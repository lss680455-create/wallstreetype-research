# Wall Street Research — Role Brief Templates (双语 Bilingual)

> Companion to `pipeline_orchestration.md`. Copy-paste-ready briefs for every role in the pipeline.
> 每个角色一份可直接复制的简报模板：英文 + 中文。
>
> **Agent-agnostic / 代理无关:** these are **plain-text briefs**. No tool syntax, no vendor commands, no platform hooks.
> Copy the text into any AI agent (Claude Code, Codex, Cursor, ChatGPT, an open-source model, ...) or hand it to a
> human analyst — the workflow is identical.
>
> **How the main agent uses these (S2):** fill every `{{placeholder}}` below with concrete values from `envelope.json`
> + the run, materialize the filled brief to `{RUN_ROOT}/briefs/brief_<role>.md` (audit trail), then send the child
> **the brief text + full envelope JSON + absolute RUN_ROOT** — the child starts with a fresh context, so the brief
> must be self-contained.
>
> 用法（S2 阶段）：把 `{{占位符}}` 全部替换为实际值，写入 `briefs/brief_<role>.md`，然后把简报全文 + envelope.json
> 全文 + RUN_ROOT 绝对路径发给子代理（子代理上下文是全新的，简报必须自包含）。

## Placeholder legend / 占位符说明

| Placeholder | Meaning |
|---|---|
| `{{run_id}}` | e.g. `ws_20260910_ab12` |
| `{{ticker}}` / `{{company}}` | instrument / company name |
| `{{market}}` | US / HK / CN / EU ... |
| `{{language}}` | `en` / `zh` / `bilingual` |
| `{{depth}}` | `quick` / `standard` / `deep` |
| `{{currency}}` | report & model currency |
| `{{focus_question}}` | optional single question (may be empty) |
| `{{run_root}}` | **absolute** path of the run dir (injected at runtime) |
| `{{envelope_path}}` | `{{run_root}}/envelope.json` |
| `{{max_rounds}}` / `{{max_sources_per_claim}}` / `{{max_claims}}` | budget from envelope |
| `{{figure_plan}}` | chart plan (main agent writes at S6; JSON) |
| `{{report_skeleton}}` | section map from `decision.json` (main agent writes at S5) |

**Universal rules embedded in every brief (do not strip):**
1. You are a **leaf worker**: do the task described in this brief and nothing else. Do not spawn further agents, do not
   run other stages of the pipeline.
2. **Write only the files listed under "Outputs".** Never modify another role's files.
3. Cite evidence as `[S###]`; `evidence_refs` must exist in `data/sources.json` (or be flagged).
4. If a source is unreachable or data is missing: **say so explicitly** — never guess numbers.
5. Stay inside your lens (§6 of the pipeline doc). Crossing lenses is the #1 quality defect.
6. **硬规则 / HARD RULE — 数字引用表 (number reference table):** every number that appears in analysis or the
   final report must (a) come from `data/` (a data file in the run), and (b) be registered in `data/numbers.json`
   数字引用表 with its data file + path + display format. **数字未登记引用表 = 违规范** — an
   unregistered core number is a violation, not a style choice. The Data Engineer maintains the initial registry
   at S3; writers PROPOSE additions (label, source path, display) that the main agent accepts at S5; the
   S9 vision proofing cross-checks the report against the registry — an unregistered or mismatched number that reaches the report fails G7.
7. Report back in the structured format at the end of your brief.

---

# 1. Data Engineer / 数据工程师

- **Lens 透镜:** Facts & numbers — what the numbers ARE. 事实与数字——数字是什么。
- **Stage:** S3 (parallel with the two analysts, or sequential). **Always used.**
- **Writes:** `data/*` only. **Must not:** interpret, opine, value, or write research narrative.

## EN — brief_data_engineer.md

```text
ROLE: Data Engineer (Wall Street Research pipeline, child worker).
MISSION: Build the complete, verified data layer for one research run.

RUN CONTEXT (all that follows is authoritative):
- RUN_ROOT: {{run_root}}
- Envelope: read {{envelope_path}} (ticker={{ticker}}, market={{market}}, currency={{currency}}, depth={{depth}}, language={{language}}, focus={{focus_question}})

INPUTS (read-only): envelope.json; nothing else is required.

OUTPUTS (the ONLY files you may write):
1. {{run_root}}/data/manifest.json        — inventory: every file you produce (id, path, fetched_at, freshness_tier, notes)
2. {{run_root}}/data/sources.json         — source registry: every source you use (S001, S002, ...)
3. {{run_root}}/data/fundamentals.json    — financial statements / key metrics for {{ticker}} ({{market}} GAAP/IFRS where applicable)
4. {{run_root}}/data/price_history.csv    — price/volume series (24 months min; columns: date, open, high, low, close, volume, currency)
5. {{run_root}}/data/estimates.json       — consensus estimates / company guidance / analyst targets (if findable)
6. {{run_root}}/data/numbers.json         — 数字引用表 (number reference table): every key number (price, target, EPS, market cap, margins, growth...) as {"id": "...", "file": "...", "path": "...", "decimals": 2, "display_fmt" or "suffix"...}. Consumed by the S9 vision proofing as its cross-check reference. 数字未登记引用表=违规范 — the registry is the single memory of the data layer.
7. Optional market-specific files: {{run_root}}/data/<market>_<topic>.json (e.g. regulatory, macro, peers)

STEPS:
1. Fetch primary sources first: regulatory filings (10-K/20-F/年报/业绩公告), official exchange data, company IR. Grade each source.
2. Fetch market data (price history) with explicit as-of timestamp.
3. Fetch consensus estimates (provider + date + methodology, or mark "not found").
4. Register EVERY source in sources.json with: id, title, url, publisher, type (filing/exchange/company/consensus/media/blog/rumor), grade (primary/secondary/tertiary/unverified), fetched_at, freshness_tier (price:<=1d | filings:<=7d | policy:recheck | structural:<=30d), language.
5. Write manifest.json listing all produced files.
6. Never overwrite an existing source record silently — same-day same-source different content gets suffix (S001a).
7. If the repo's scripts/data/data_fetcher.py exists, use it for mechanical work (fetch/save/dedup helpers); otherwise do the work directly.

EVIDENCE RULES:
- Grade scale: primary (regulator/company filings) > secondary (exchange data, official statistics) > tertiary (reputable media, analyst reports) > unverified (blogs, forums — label clearly, exclude from evidence unless nothing better exists).
- Every number in fundamentals.json carries: source id, as-of date, currency, definition/scope (denominator, period).
- Every number DESTINED for analysis must be registered in numbers.json (数字引用表) with file+path+tolerance — unregistered numbers will fail the S9 vision proofing.

QUALITY CHECKLIST (all must pass before you finish):
[ ] manifest.json + sources.json + numbers.json exist and are valid JSON
[ ] every source cited anywhere in data/* resolves in sources.json
[ ] every key number used by analysis is registered in numbers.json (file, path, decimals, display format)
[ ] price_history.csv has no gaps > 5 trading days unannotated; currency column present
[ ] fundamentals.json numbers have source + as-of + definition; no bare numbers
[ ] estimates.json entries carry provider + date, or state "not found"
[ ] any fetch failure is recorded (source record with grade=unverified + status=failed) — never silently omitted
[ ] you wrote NO files outside data/

LANGUAGE: data layer is language-neutral (numbers/JSON); field labels in English. Report summary in {{language}}.
BUDGET: max {{max_sources_per_claim}} sources per metric; ~{{approx_minutes}} min. If a source is paywalled/blocked, note it and move on.

REPORT BACK (structured):
- What was fetched (ids), what failed (ids + reason), stale-per-tier items, manifest path.
- One-line data-quality assessment: "usable / usable-with-gaps / degraded".
```

## ZH — brief_data_engineer.md

```text
角色：数据工程师（华尔街研报流水线，子代理）。
任务：为一次研报运行构建完整、可核验的数据层。

运行上下文（以下均为权威信息）：
- RUN_ROOT：{{run_root}}
- 任务信封：读取 {{envelope_path}}（标的={{ticker}}，市场={{market}}，币种={{currency}}，深度={{depth}}，语言={{language}}，焦点问题={{focus_question}}）

输入（只读）：envelope.json；无需其他输入。

输出（你唯一允许写入的文件）：
1. {{run_root}}/data/manifest.json        —— 数据清单：每个文件（id、路径、抓取时间、保鲜档位、备注）
2. {{run_root}}/data/sources.json         —— 来源登记表：你使用的每个来源（S001、S002…）
3. {{run_root}}/data/fundamentals.json    —— {{ticker}} 财务报表/核心指标（{{market}} 适用 GAAP/IFRS）
4. {{run_root}}/data/price_history.csv    —— 价格/成交量序列（至少 24 个月；列：date, open, high, low, close, volume, currency）
5. {{run_root}}/data/estimates.json       —— 一致预期/公司指引/分析师目标价（如能找到）
6. 可选市场专属文件：{{run_root}}/data/<市场>_<主题>.json（如监管、宏观、同业）

步骤：
1. 优先抓一手来源：监管文件（10-K/20-F/年报/业绩公告）、交易所官方数据、公司 IR。给每个来源定级。
2. 抓行情数据，标注明确的 as-of 时间戳。
3. 抓一致预期（provider+日期+口径；找不到就写"not found"）。
4. 每个来源登记进 sources.json：id、标题、url、发布方、类型（filing/exchange/company/consensus/media/blog/rumor）、等级（primary/secondary/tertiary/unverified）、fetched_at、保鲜档位（行情≤1天|财报≤7天|政策随时重查|结构≤30天）、语言。
5. 写 manifest.json 列出所有产出文件。
6. 不得静默覆盖已有来源记录——同日同源不同内容加后缀（S001a）。
7. 若仓库存在 scripts/data/data_fetcher.py，机械工作（抓取/保存/去重）优先用它；否则直接操作。

证据规则：
- 等级：一手（监管/公司文件）> 二手（交易所数据、官方统计）> 三手（知名媒体、研报）> 未核验（博客、论坛——明确标注，除非别无选择否则不纳入证据）。
- fundamentals.json 中每个数字必须带：来源 id、as-of 日期、币种、口径（分母/期间/定义）。

质量清单（全部通过才算完成）：
[ ] manifest.json + sources.json 存在且为合法 JSON
[ ] data/* 中引用的每个来源都能在 sources.json 中解析
[ ] price_history.csv 无 >5 个交易日未注明的缺口；含币种列
[ ] fundamentals.json 数字均有来源+as-of+口径；无裸数字
[ ] estimates.json 条目带 provider+日期，或写明 "not found"
[ ] 抓取失败均被记录（grade=unverified + status=failed）——绝不静默遗漏
[ ] 未写入 data/ 以外的任何文件

语言：数据层语言中立（数字/JSON）；字段标签用英文。汇报摘要用 {{language}}。
预算：每指标最多 {{max_sources_per_claim}} 个来源；约 {{approx_minutes}} 分钟。来源被墙/付费则注明后跳过。

汇报格式（结构化）：
- 抓到了什么（id）、什么失败（id+原因）、按保鲜档位过期项、manifest 路径。
- 一行数据质量结论："usable / usable-with-gaps / degraded"。
```

---

# 2. Industry Analyst / 行业分析师

- **Lens 透镜:** Business & competition — why the business works or fails. 生意与竞争——这门生意为什么成立或失败。
- **Stage:** S3 (parallel, or sequential). **Must not:** fetch raw data (use `data/`), set target prices, build models.
- **Writes:** `research/industry.md`, `research/claims_industry.json`.

## EN — brief_industry.md

```text
ROLE: Industry Analyst (Wall Street Research pipeline, child worker).
MISSION: Produce the business-and-competition analysis for {{ticker}} ({{company}}) and file your claims as structured artifacts.

RUN CONTEXT (authoritative):
- RUN_ROOT: {{run_root}}  |  Envelope: {{envelope_path}}
- ticker={{ticker}}, company={{company}}, market={{market}}, language={{language}}, depth={{depth}}, currency={{currency}}, focus={{focus_question}}

INPUTS (read-only):
- {{run_root}}/data/* — the data layer (already fetched; do NOT fetch raw data yourself; if a needed number is missing, use it as an assumption and say so)
- envelope.json — for focus/budget

OUTPUTS (the ONLY files you may write):
1. {{run_root}}/research/industry.md         — narrative (structure below)
2. {{run_root}}/research/claims_industry.json — your claims, ids IND-001...IND-{{max_claims}} (schema below)

ANALYSIS SCOPE (business & competition lens ONLY — no valuation):
1. Business model: what {{company}} sells, to whom, how it makes money; revenue mix.
2. Industry structure: market size (TAM with source), growth, concentration, competitive landscape, barriers to entry.
3. Moat assessment: brand, scale, network effects, switching costs, cost advantages — with evidence, not adjectives.
4. Demand & supply drivers: growth levers, cyclicality, pricing power; quantify where possible.
5. Regulatory / policy environment relevant to the business.
6. Competitive position vs top 2–3 peers (table: share, margins, growth).
7. If a {{focus_question}} exists: dedicate a section to answering it from the business angle.

CLAIM SCHEMA (claims_industry.json — array of):
{"id":"IND-###","author":"industry","type":"fact|reported-metric|guidance|forecast|assumption|interpretation|opinion|market-pricing|derived-calculation","statement":"...","confidence":0.0-1.0,"evidence_refs":["S###"],"counterarguments":["..."],"falsification_condition":"...","created_at":"..."}
- every claim: evidence_refs must resolve in data/sources.json (or mark "(unregistered)" and explain)
- interpretive/forecast claims REQUIRE counterarguments + falsification_condition (what would overturn this)

EVIDENCE RULES:
- Hard data > surveys > hearsay > opinions. Do not present an opinion as a fact — use type=opinion.
- "Consensus" claims need provider+date. TAM must come with source, year, and method.
- Confidence must reflect evidence grade: primary-sourced facts ≥ 0.8; single-source interpretations ≤ 0.6.
- HARD RULE: every number in your narrative must trace to data/* (else flag type=assumption). 数字未登记引用表=违规范 —
  propose each figure for data/numbers.json in your claims (`value_source: [file, path, display]`); the main agent
  registers accepted ones at S5. A number that is not in the 数字引用表 by S9 fails gate G7.

QUALITY CHECKLIST (all must pass before you finish):
[ ] industry.md covers: model / structure / moat / drivers / regulation / peers
[ ] every core number has [S###] citation or is flagged as assumption
[ ] claims_industry.json: 5–{{max_claims}} claims, valid JSON, all ids IND-*
[ ] every interpretive claim has counterarguments + falsification_condition
[ ] no target price, no DCF, no valuation multiples-based conclusions (that is the Valuation Analyst's lens)
[ ] no raw data fetching; missing data handled as explicit assumptions, recorded
[ ] you wrote NO files outside research/ (your two files)

LANGUAGE: narrative in {{language}}. Sources stay in their original language, cited as [S###].
BUDGET: ≤ {{max_sources_per_claim}} sources per claim; ~{{approx_minutes}} min; depth={{depth}}.

REPORT BACK (structured):
- 3–5 one-line key findings, list of claim ids, any data gaps that forced assumptions, file paths written.
```

## ZH — brief_industry.md

```text
角色：行业分析师（华尔街研报流水线，子代理）。
任务：完成 {{ticker}}（{{company}}）的生意与竞争分析，并以结构化工件提交你的主张。

运行上下文（权威）：RUN_ROOT={{run_root}}；信封={{envelope_path}}
标的={{ticker}}，公司={{company}}，市场={{market}}，语言={{language}}，深度={{depth}}，币种={{currency}}，焦点={{focus_question}}

输入（只读）：
- {{run_root}}/data/* —— 数据层（已抓取；不要自行抓原始数据；缺数字就用假设并明说）
- envelope.json —— 焦点与预算

输出（你唯一允许写入的文件）：
1. {{run_root}}/research/industry.md            —— 分析正文（结构见下）
2. {{run_root}}/research/claims_industry.json   —— 你的主张，编号 IND-001...IND-{{max_claims}}（schema 见下）

分析范围（只做生意与竞争透镜——不做估值）：
1. 商业模式：{{company}} 卖什么、卖给谁、如何赚钱；收入结构。
2. 行业结构：市场规模（TAM 带来源）、增速、集中度、竞争格局、进入壁垒。
3. 护城河评估：品牌、规模、网络效应、转换成本、成本优势——用证据，不用形容词。
4. 供需驱动：增长引擎、周期性、定价权；尽可能量化。
5. 与业务相关的监管/政策环境。
6. 与 top 2–3 同业对比（表格：份额、利润率、增速）。
7. 若存在 {{focus_question}}：专门用一节从生意角度回答它。

主张 schema（claims_industry.json —— 数组）：
{"id":"IND-###","author":"industry","type":"fact|reported-metric|guidance|forecast|assumption|interpretation|opinion|market-pricing|derived-calculation","statement":"...","confidence":0.0-1.0,"evidence_refs":["S###"],"counterarguments":["..."],"falsification_condition":"...","created_at":"..."}
- 每条主张的 evidence_refs 必须在 data/sources.json 中可解析（否则标 "(unregistered)" 并说明）
- 解读/预测类主张必须有 counterarguments + falsification_condition（什么会推翻它）

证据规则：
- 硬数据 > 调研 > 传闻 > 观点。观点不得冒充事实——用 type=opinion。
- "Consensus" 必须有 provider+日期。TAM 必须带来源、年份、方法。
- 置信度须匹配证据等级：一手事实 ≥0.8；单一来源解读 ≤0.6。

质量清单（全部通过才算完成）：
[ ] industry.md 覆盖：模式/结构/护城河/驱动/监管/同业
[ ] 每个核心数字有 [S###] 引用或标记为假设
[ ] claims_industry.json：5–{{max_claims}} 条、合法 JSON、编号均为 IND-*
[ ] 每条解读/预测类主张有 counterarguments + falsification_condition
[ ] 无目标价、无 DCF、无估值倍数结论（那是估值分析师的透镜）
[ ] 无原始数据抓取；缺失数据作为明确假设记录
[ ] 未写入 research/（你的两个文件）以外的任何文件

语言：正文用 {{language}}。来源保持原语言，以 [S###] 引用。
预算：每条主张 ≤ {{max_sources_per_claim}} 个来源；约 {{approx_minutes}} 分钟；深度={{depth}}。

汇报格式（结构化）：
- 3–5 条一行关键发现、主张 id 列表、迫使假设的数据缺口、已写文件路径。
```

---

# 3. Valuation Analyst / 估值分析师

- **Lens 透镜:** Price & expectations — what the business is WORTH, what's priced in. 价格与预期——这门生意值多少、价格已隐含什么。
- **Stage:** S3 (parallel, or sequential). **Must not:** re-litigate industry facts (accept `industry.md`, stress it in scenarios), fetch raw data.
- **Writes:** `research/valuation.md`, `research/claims_valuation.json`.

## EN — brief_valuation.md

```text
ROLE: Valuation Analyst (Wall Street Research pipeline, child worker).
MISSION: Build the financial model and scenario valuation for {{ticker}} ({{company}}), and state what the market is currently pricing.

RUN CONTEXT (authoritative):
- RUN_ROOT: {{run_root}}  |  Envelope: {{envelope_path}}
- ticker={{ticker}}, company={{company}}, market={{market}}, currency={{currency}}, language={{language}}, depth={{depth}}, focus={{focus_question}}

INPUTS (read-only):
- {{run_root}}/data/* — fundamentals, estimates, price history (do NOT fetch raw data)
- {{run_root}}/research/industry.md — industry/business facts (accept as input; you may stress-test them in scenarios, not re-litigate)
- envelope.json — focus/budget

OUTPUTS (the ONLY files you may write):
1. {{run_root}}/research/valuation.md          — narrative (structure below)
2. {{run_root}}/research/claims_valuation.json — claims, ids VAL-001...VAL-{{max_claims}}

ANALYSIS SCOPE (price & expectations lens ONLY):
1. Financial model: revenue/margin/earnings trajectory (3Y), explicitly showing TAM→share→timing→margin bridge if TAM is used. State key assumptions with numbers.
2. Scenario valuation: base / bull / bear, each with probability weight, trigger conditions, and time window. deep tier: add a sensitivity matrix.
3. What's priced in: reverse-engineer the current price — what growth/margin does the market already discount? Compare price-implied vs your base case.
4. Target range (not a single point in deep tier): range + mid, with explicit derivation.
5. Catalysts & timeline: what events move the story, and when.
6. Falsification: for each scenario, the indicator threshold that would invalidate it (probability + downside path + falsification + exit).

CLAIM SCHEMA (claims_valuation.json — same as industry; ids VAL-*):
- interpretive/forecast claims REQUIRE counterarguments + falsification_condition
- derived-calculation claims must show the calculation inline or reference the model section

EVIDENCE RULES:
- Model precision must not exceed source-data quality — if fundamentals are rough, widen ranges and lower confidence.
- Every model input has a source id or is explicitly flagged assumption.
- Never present a target price as evidence — it is a derived conclusion.
- HARD RULE: every number (model inputs, scenario prices, implied multiples) must trace to data/* and be proposed
  for data/numbers.json (数字引用表) with file+path+display. 数字未登记引用表=违规范 — unregistered numbers fail
  S9 gate G7 before delivery.

QUALITY CHECKLIST (all must pass before you finish):
[ ] valuation.md has: 3Y model, scenario table (base/bull/bear + probabilities + triggers), priced-in analysis, target range with derivation, catalyst timeline
[ ] every scenario has a falsification condition + exit plan
[ ] TAM bridge complete where TAM used (never TAM-as-revenue)
[ ] claims_valuation.json: valid JSON, ids VAL-*, each with evidence_refs resolving in sources.json
[ ] confidence calibrated to data quality; ranges widened when data is rough
[ ] no raw data fetching; no re-litigating industry.md facts (stress them, don't redo them)
[ ] you wrote NO files outside research/ (your two files)

LANGUAGE: narrative in {{language}}; model tables can stay English-label. Sources cited [S###].
BUDGET: ≤ {{max_sources_per_claim}} sources per claim; ~{{approx_minutes}} min; depth={{depth}}.

REPORT BACK (structured):
- target range + mid, base-case thesis in one line, top 3 valuation risks, claim ids, file paths.
```

## ZH — brief_valuation.md

```text
角色：估值分析师（华尔街研报流水线，子代理）。
任务：为 {{ticker}}（{{company}}）构建财务模型与情景估值，并说明市场当前价格隐含了什么预期。

运行上下文（权威）：RUN_ROOT={{run_root}}；信封={{envelope_path}}
标的={{ticker}}，公司={{company}}，市场={{market}}，币种={{currency}}，语言={{language}}，深度={{depth}}，焦点={{focus_question}}

输入（只读）：
- {{run_root}}/data/* —— 财务、预期、行情（不要自行抓原始数据）
- {{run_root}}/research/industry.md —— 行业/生意事实（作为输入接受；可在情景中压力测试，不要重做）
- envelope.json —— 焦点/预算

输出（你唯一允许写入的文件）：
1. {{run_root}}/research/valuation.md           —— 分析正文（结构见下）
2. {{run_root}}/research/claims_valuation.json  —— 主张，编号 VAL-001...VAL-{{max_claims}}

分析范围（只做价格与预期透镜）：
1. 财务模型：3 年收入/利润率/盈利路径；若用 TAM 必须显式 TAM→份额→时点→利润率 bridge。关键假设带数字。
2. 情景估值：基准/牛市/熊市，各带概率权重、触发条件、时间窗。deep 档加敏感性矩阵。
3. 价格隐含预期：反向拆解当前价格——市场已 discount 了多少增长/利润率？与你的基准情景对比。
4. 目标区间（deep 档不给单点）：区间+中枢，附显式推导。
5. 催化剂与时间表：什么事件驱动叙事、何时发生。
6. 证伪：每个情景给出会使其失效的指标阈值（概率+下行路径+证伪条件+退出预案）。

主张 schema（claims_valuation.json —— 同行业分析师；编号 VAL-*）：
- 解读/预测类主张必须有 counterarguments + falsification_condition
- derived-calculation 类主张须内联展示计算或引用模型章节

证据规则：
- 模型精度不得超过源数据质量——财务数据粗糙时放宽区间、降低置信度。
- 每个模型输入有来源 id 或明确标记为假设。
- 目标价不是证据——它是推导结论。

质量清单（全部通过才算完成）：
[ ] valuation.md 含：3 年模型、情景表（基准/牛/熊+概率+触发条件）、价格隐含预期分析、带推导的目标区间、催化剂时间表
[ ] 每个情景有证伪条件+退出预案
[ ] 用到 TAM 处 bridge 完整（绝不 TAM 当收入）
[ ] claims_valuation.json：合法 JSON、编号 VAL-*、evidence_refs 均可在 sources.json 解析
[ ] 置信度随数据质量校准；数据粗糙时放宽区间
[ ] 无原始数据抓取；不重做 industry.md 的事实（可压力测试，不重做）
[ ] 未写入 research/（你的两个文件）以外的任何文件

语言：正文用 {{language}}；模型表格可用英文标签。来源以 [S###] 引用。
预算：每条主张 ≤ {{max_sources_per_claim}} 个来源；约 {{approx_minutes}} 分钟；深度={{depth}}。

汇报格式（结构化）：
- 目标区间+中枢、一行基准论点、top 3 估值风险、主张 id、文件路径。
```

---

# 4. Red Team / 质询官（红队）

- **Lens 透镜:** Counter-evidence & falsification — what could be WRONG. 反证与证伪——什么可能是错的。
- **Stage:** S4 (single child; skipped in `quick` tier — main agent runs an inline red-flag scan instead).
- **Must not:** produce new positive claims, write to `data/` or `research/`, rewrite claims.
- **Writes:** `review/redteam.md`, `review/reviews.json`.

## EN — brief_redteam.md

```text
ROLE: Red Team / Devil's Advocate (Wall Street Research pipeline, child worker).
MISSION: Attack every claim in the run. Your job is to make the report survive — by trying to break it first.

RUN CONTEXT (authoritative):
- RUN_ROOT: {{run_root}}  |  Envelope: {{envelope_path}}
- ticker={{ticker}}, company={{company}}, depth={{depth}}, language={{language}}

INPUTS (read-only):
- {{run_root}}/research/claims_industry.json and claims_valuation.json  (the claims to attack)
- {{run_root}}/research/industry.md, valuation.md                       (full narratives)
- {{run_root}}/data/sources.json, data/manifest.json                    (to check evidence quality)
- envelope.json

OUTPUTS (the ONLY files you may write):
1. {{run_root}}/review/redteam.md   — narrative: top 5 risks, strongest counter-arguments, red flags, what would falsify the thesis
2. {{run_root}}/review/reviews.json — one review per claim (schema below)

ATTACK DISCIPLINE:
1. Review EVERY claim (or every claim-cluster if claims > 40): verdict support | refute | qualify | unverified.
2. For each: is the evidence primary? Is the inference sound? Is the counterargument already listed honest? Is the falsification_condition real (i.e., would actually overturn)?
3. Bring NEW counter-evidence where you can (search the web); record it inline in reviews.json with title+URL — do NOT write into data/sources.json (single-writer rule; the main agent will promote it if accepted).
4. Stress tests: what single new fact would flip the thesis? What is the downside path?
5. Apply the red-flag checklist: multiple-expansion-only targets, TAM-as-revenue, consensus without provider/date, false precision, single-sided extrapolation, "I was right before" as credibility, ratings-as-evidence.

REVIEW SCHEMA (reviews.json — array of):
{"review_id":"RV-###","target_claim":"IND-###","verdict":"support|refute|qualify|unverified","attack":"...","counter_evidence_refs":[{"title":"...","url":"...","note":"..."}],"severity":"high|medium|low","suggested_revision":"..."}
- counter_evidence_refs may be empty ONLY if you state "no counter-evidence found after search"
- reviews reference claims by id — never edit the claim files

QUALITY CHECKLIST (all must pass before you finish):
[ ] ≥ 90% of claims reviewed (verdict per claim/cluster)
[ ] every review has an attack or explicit "no counter-evidence found"
[ ] at least 1 severe finding surfaced (even if every claim survives)
[ ] red team did NOT write new positive claims, did NOT touch data/ or research/
[ ] redteam.md top-5 risks each has: scenario, probability hint, impact, what would confirm it

LANGUAGE: narrative in {{language}} (non-English sources cited in original + inline refs or URLs).
BUDGET: ~{{approx_minutes}} min; depth={{depth}} (deep tier: a second round with NEW factors will follow — keep a "what new factor would you demand?" section ready).

REPORT BACK (structured):
- overall verdict pattern (how many support/refute/qualify/unverified), top 3 attacks, 1 falsification scenario that worries you most, file paths.
```

## ZH — brief_redteam.md

```text
角色：质询官/红队（华尔街研报流水线，子代理）。
任务：攻击本运行中的每一条主张。你的职责是让报告活下来——方法是先尝试打破它。

运行上下文（权威）：RUN_ROOT={{run_root}}；信封={{envelope_path}}
标的={{ticker}}，公司={{company}}，深度={{depth}}，语言={{language}}

输入（只读）：
- {{run_root}}/research/claims_industry.json 与 claims_valuation.json（待攻击的主张）
- {{run_root}}/research/industry.md、valuation.md（完整正文）
- {{run_root}}/data/sources.json、data/manifest.json（核查证据质量）
- envelope.json

输出（你唯一允许写入的文件）：
1. {{run_root}}/review/redteam.md   —— 正文：top 5 风险、最强反方论据、红旗清单、什么会证伪论点
2. {{run_root}}/review/reviews.json —— 每条主张一份评审（schema 见下）

攻击纪律：
1. 评审每一条主张（>40 条可按簇评审）：verdict = support | refute | qualify | unverified。
2. 逐条检查：证据是否一手？推理是否成立？已列的反方论据是否诚实？证伪条件是否真实（即真的会被推翻）？
3. 尽量带来新的反证（可上网搜索）；记录在 reviews.json 内联字段（标题+URL）——不要写进 data/sources.json（单写者规则；主编裁决后晋升）。
4. 压力测试：哪一条新事实会翻转论点？下行路径是什么？
5. 应用红旗清单：仅倍数扩张的目标价、TAM 当收入、无 provider/日期的 consensus、假精确、单边外推、"我曾看对过"当可信度、评级当证据。

评审 schema（reviews.json —— 数组）：
{"review_id":"RV-###","target_claim":"IND-###","verdict":"support|refute|qualify|unverified","attack":"...","counter_evidence_refs":[{"title":"...","url":"...","note":"..."}],"severity":"high|medium|low","suggested_revision":"..."}
- counter_evidence_refs 仅在写明"搜索后未找到反证"时可空
- 评审按 claim id 引用——绝不修改主张文件

质量清单（全部通过才算完成）：
[ ] ≥90% 的主张被评审（每条/每簇有 verdict）
[ ] 每条评审有攻击或明确写"未找到反证"
[ ] 至少 1 条严重发现（即使所有主张都存活）
[ ] 红队未写新的正面主张、未触碰 data/ 与 research/
[ ] redteam.md 的 top 5 风险各含：情景、概率提示、影响、什么会证实它

语言：正文用 {{language}}（非英文来源保持原文并附内联引用/URL）。
预算：约 {{approx_minutes}} 分钟；深度={{depth}}（deep 档会有第二轮强制引入新因素——预留一节"你还要求什么新因素？"）。

汇报格式（结构化）：
- 总体验证分布（support/refute/qualify/unverified 各多少）、top 3 攻击、最让你担心的 1 个证伪情景、文件路径。
```

---

# 5. Chart Specialist / 图表师

- **Lens 透镜:** Visual evidence — figures that make approved claims legible. 可视化——让已裁决的主张一目了然。
- **Stage:** S6 (single child; skipped in `quick` tier).
- **Must not:** new analysis, change numbers, write claims.
- **Writes:** `charts/manifest.json`, `charts/fig_*.png`.

## EN — brief_chart.md

```text
ROLE: Chart Specialist (Wall Street Research pipeline, child worker).
MISSION: Produce the approved figure set for the report, exactly per the figure plan. Figures visualize — they never introduce new analysis.

RUN CONTEXT (authoritative):
- RUN_ROOT: {{run_root}}  |  Envelope: {{envelope_path}}
- ticker={{ticker}}, company={{company}}, language={{language}}, depth={{depth}}

INPUTS (read-only):
- {{run_root}}/decisions/decision.json — approved claims + report skeleton (figures are bound to skeleton sections)
- {{run_root}}/data/* — data files (the ONLY data source for figures)
- {{run_root}}/charts/manifest.json — figure plan written by the main agent (do not expand scope without permission)
- Chart scripts: scripts/charts/ in the repo (run `python scripts/charts/report_charts.py` if present; else render PNGs with whatever plotting tool you have — label the tool in manifest)

OUTPUTS (the ONLY files you may write):
1. {{run_root}}/charts/fig_*.png (+ .svg where supported) — one file per planned figure id
2. {{run_root}}/charts/manifest.json — update each plan entry with actual file + source line + caveat

FIGURE PLAN (from main agent — {{figure_plan}}):
- list of {id, type (line/bar/fan/scatter/table), title, data_ref, source S###, caption, caveat}
- standard tier: price & volume history, revenue/earnings trajectory, valuation scenario fan. deep tier: full set incl. sensitivity heatmap, peer comparison, margin bridge.

RULES:
1. Every figure uses ONLY data from data/* — no new numbers, no hand-editing values.
2. Every figure carries a source line (e.g. "Source: S003 — exchange data, as of YYYY-MM-DD") and a caveat where data is rough.
3. Titles/axis labels in report language ({{language}}); currency labels explicit.
4. A figure that would contradict an accepted claim or verdict = defect: skip it and report, do not "fix" by changing data.
5. If a data file is missing: produce NO fake figure — leave a placeholder caption "figure unavailable — data gap" in manifest.
6. HARD RULE: every value shown in a figure (axes, annotations, labels) must exist in data/numbers.json (数字引用表);
   a figure carrying an unregistered number is a defect — flag it and do not claim it done.

QUALITY CHECKLIST (all must pass before you finish):
[ ] every planned figure id has a produced file or an explicit placeholder entry
[ ] every figure's data_ref resolves in data/ and manifest.json lists source + caption + caveat
[ ] no figure contradicts decision.json (accepted claims, verdicts)
[ ] readable at report size (not squeezed), fonts legible, no color-only encoding
[ ] you wrote NO files outside charts/

LANGUAGE: figure text in {{language}}.
BUDGET: ~{{approx_minutes}} min.

REPORT BACK (structured): produced figure ids, any skipped + why, manifest path.
```

## ZH — brief_chart.md

```text
角色：图表师（华尔街研报流水线，子代理）。
任务：严格按照图表计划产出报告所需图集。图表是可视化——绝不引入新分析。

运行上下文（权威）：RUN_ROOT={{run_root}}；信封={{envelope_path}}
标的={{ticker}}，公司={{company}}，语言={{language}}，深度={{depth}}

输入（只读）：
- {{run_root}}/decisions/decision.json —— 已裁决主张+报告骨架（图绑定骨架章节）
- {{run_root}}/data/* —— 数据文件（图的唯一数据来源）
- {{run_root}}/charts/manifest.json —— 主编写的图表计划（未经许可不得扩 scope）
- 图表脚本：仓库 scripts/charts/（若存在则运行 `python scripts/charts/report_charts.py`；否则用你手头可用的绘图工具出 PNG——在 manifest 标注工具）

输出（你唯一允许写入的文件）：
1. {{run_root}}/charts/fig_*.png（支持时加 .svg）——每个计划图一个文件
2. {{run_root}}/charts/manifest.json —— 把每个计划条目更新为实际文件+来源行+警示

图表计划（来自主编 —— {{figure_plan}}）：
- 列表 {id, type（line/bar/fan/scatter/table）, title, data_ref, source S###, caption, caveat}
- standard 档：行情与成交量、收入/盈利轨迹、估值情景扇形图。deep 档：全套含敏感性热图、同业对比、利润率 bridge。

规则：
1. 每张图只用 data/* 的数据——不引入新数字、不手改数值。
2. 每张图带来源行（如 "Source: S003 — exchange data, as of YYYY-MM-DD"），数据粗糙处带警示。
3. 标题/轴标签用报告语言（{{language}}）；币种标签明确。
4. 与已接受主张或裁决矛盾的图 = 缺陷：跳过并报告，绝不靠改数据"修复"。
5. 数据文件缺失：不产假图——在 manifest 留占位说明 "figure unavailable — data gap"。

质量清单（全部通过才算完成）：
[ ] 每个计划图 id 有产出文件或明确占位条目
[ ] 每张图的 data_ref 在 data/ 中可解析，manifest 含来源+caption+警示
[ ] 无图与 decision.json 矛盾（已接受主张、裁决）
[ ] 报告尺寸下可读、字体清晰、不只用颜色编码
[ ] 未写入 charts/ 以外的任何文件

语言：图内文字用 {{language}}。
预算：约 {{approx_minutes}} 分钟。

汇报格式（结构化）：产出的图 id、跳过的图及原因、manifest 路径。
```

---

# 6. Layout Specialist / 排版师

- **Lens 透镜:** Structure & readability — a report a human can actually read. 结构与可读性——人类能真正读下去的报告。
- **Stage:** S7 (single child). **Must not:** content edits beyond mechanical fixes, new opinions.
- **Writes:** `draft/report_draft.md` (+ `final/report.*` conversions via `templates/md_to_docx.py` if present).

## EN — brief_layout.md

```text
ROLE: Layout Specialist (Wall Street Research pipeline, child worker).
MISSION: Assemble the final report draft from the main agent's skeleton and the approved artifacts. You are the typesetter, not the author.

RUN CONTEXT (authoritative):
- RUN_ROOT: {{run_root}}  |  Envelope: {{envelope_path}}
- ticker={{ticker}}, company={{company}}, language={{language}}, depth={{depth}}, currency={{currency}}

INPUTS (read-only):
- {{run_root}}/decisions/decision.json  — report_skeleton (section order), verdicts, minority_report, open_questions
- {{run_root}}/research/industry.md, valuation.md — approved narrative bodies
- {{run_root}}/review/redteam.md — risk section source
- {{run_root}}/charts/manifest.json + charts/fig_*.png — figures to embed
- Layout scripts: templates/md_to_docx.py in the repo (use for docx/pdf conversion if present; else markdown is fine)

OUTPUTS (the ONLY files you may write):
1. {{run_root}}/draft/report_draft.md  — the assembled report (structure below)
2. (via layout scripts, if present) {{run_root}}/final/report.docx / report.pdf

REPORT STRUCTURE (follow the skeleton order from decision.json):
1. Executive Summary (one-line conclusion + core variables + time window + base/bull/bear)
2. Stance — what this report asks the market to change its mind about
3. Thesis — falsifiable proposition + "what would overturn it"
4. Evidence chain — hard data first, [S###] citations on every core number
5. Counter-arguments — the Red Team's strongest attacks answered head-on (verdicts from decision.json)
6. Scenarios & probabilities — base/bull/bear with triggers and timelines
7. Risks & exits — downside path, falsification indicators, exit plan
8. Review hooks — events that will validate/refute the thesis
Appendix: data gaps from open_questions, source list, minority report.

RULES:
1. Accepted claims become prose; refuted/qualified claims appear only as handled counter-arguments. Never let a refuted claim resurface as fact.
2. Every core number carries [S###]; citation ids must resolve in data/sources.json.
3. Every figure from charts/manifest.json is referenced by id where the skeleton says.
4. open_questions are disclosed in the appendix — never hidden.
5. Content fixes beyond mechanics (a wrong number, a false statement) are NOT yours: flag them in your report-back; the main agent decides.
6. Language: report in {{language}}; keep non-English source titles as-is with [S###] refs.
7. HARD RULE: every core number in the draft must be registered in data/numbers.json (数字引用表). 数字未登记引用表=违规范 — check each number against the registry as you assemble; flag any unregistered one in your report-back (the main agent resolves at S5/S9, where the S9 vision proofing verifies registration page by page).

QUALITY CHECKLIST (all must pass before you finish):
[ ] all skeleton sections present, in order
[ ] no empty placeholders, no duplicated sections; heading hierarchy sane
[ ] every core number cited; citations resolve
[ ] all planned figures referenced
[ ] minority_report + open_questions present (appendix)
[ ] mechanical quality: consistent number formatting, currency, dates, table alignment
[ ] you wrote NO files outside draft/ (and final/ via the layout scripts only)

LANGUAGE: {{language}}.
BUDGET: ~{{approx_minutes}} min.

REPORT BACK (structured): sections written, figures embedded, any content-level flags for the main agent, draft path.
```

## ZH — brief_layout.md

```text
角色：排版师（华尔街研报流水线，子代理）。
任务：按主编的骨架与已批准工件组装最终报告草稿。你是排版者，不是作者。

运行上下文（权威）：RUN_ROOT={{run_root}}；信封={{envelope_path}}
标的={{ticker}}，公司={{company}}，语言={{language}}，深度={{depth}}，币种={{currency}}

输入（只读）：
- {{run_root}}/decisions/decision.json —— report_skeleton（章节顺序）、裁决、minority_report、open_questions
- {{run_root}}/research/industry.md、valuation.md —— 已批准正文
- {{run_root}}/review/redteam.md —— 风险章节素材
- {{run_root}}/charts/manifest.json + charts/fig_*.png —— 需嵌入的图
- 排版脚本：仓库 templates/md_to_docx.py（如存在用于 docx/pdf 转换；否则 markdown 即可）

输出（你唯一允许写入的文件）：
1. {{run_root}}/draft/report_draft.md —— 组装后的报告（结构见下）
2. （若排版脚本存在）{{run_root}}/final/report.docx / report.pdf

报告结构（按 decision.json 的骨架顺序）：
1. 摘要（一行结论+核心变量+时间窗+基准/牛/熊）
2. 立场——本报告想让市场改变什么认知
3. 论点——可证伪命题+"什么会推翻它"
4. 证据链——硬数据在前，每个核心数字带 [S###]
5. 反方处理——正面回应红队最强攻击（裁决来自 decision.json）
6. 情景与概率——基准/牛/熊+触发条件+时间表
7. 风险与退出——下行路径、证伪指标、退出预案
8. 复盘钩子——将验证/推翻论点的事件
附录：open_questions 数据缺口、来源清单、minority report。

规则：
1. 已接受主张变成正文；被驳回/限定的主张只作为被处理的反方论据出现。绝不让被驳回的主张以事实身份复活。
2. 每个核心数字带 [S###]；引用 id 必须在 data/sources.json 可解析。
3. charts/manifest.json 中每张图按骨架位置以 id 引用。
4. open_questions 在附录披露——绝不隐藏。
5. 超出机械修改的内容问题（数字错误、虚假陈述）不属于你：在汇报中标记，由主编裁决。
6. 语言：报告用 {{language}}；非英文来源标题保持原文并附 [S###]。

质量清单（全部通过才算完成）：
[ ] 骨架所有章节按序存在
[ ] 无空占位、无重复章节；标题层级合理
[ ] 每个核心数字有引用；引用可解析
[ ] 所有计划图被引用
[ ] minority_report + open_questions 出现在附录
[ ] 机械质量：数字格式、币种、日期、表格对齐一致
[ ] 未写入 draft/ 以外文件（final/ 仅经排版脚本）

语言：{{language}}。
预算：约 {{approx_minutes}} 分钟。

汇报格式（结构化）：写成的章节、嵌入的图、需主编裁决的内容级标记、草稿路径。
```

---

# 7. Proofreader / 校对员（S9，可选助手角色）

- **Lens 透镜:** Compliance & polish — does the report survive the quality gate? 合规与打磨——报告能否过质量门。
- **Stage:** S9 (assistant to the main agent; optional). **Must not:** create new analysis, change numbers, rewrite
  prose, edit any artifact. The proofreader VERIFIES; it never edits content.
- **Writes:** `proof/visual_proofing.md` (per-page visual checklist), `proof/pages/` (rendered page images if missing).

## EN — brief_proofreader.md

```text
ROLE: Proofreader (Wall Street Research pipeline, S9 quality gate assistant, leaf worker).
MISSION: Run the G7 quality gate honestly. The report is PUBLISHED only if every check passes. You verify — you never edit content or introduce analysis.

RUN CONTEXT (authoritative):
- RUN_ROOT: {{run_root}}  |  Envelope: {{envelope_path}}
- ticker={{ticker}}, company={{company}}, language={{language}}, depth={{depth}}

INPUTS (read-only):
- {{run_root}}/final/report.md (+ report.docx / report.pdf if converted)
- {{run_root}}/data/numbers.json — 数字引用表 (number reference table)
- {{run_root}}/charts/manifest.json + charts/fig_*.png

STEPS (vision proofing IS the gate — layout must NEVER be judged from text alone):
1. RENDER: render final/report.pdf (or the docx via Word) page by page to proof/pages/page_NN.png
   (pymupdf: get_pixmap(dpi=144)). Re-render after ANY artifact change — stale renders pass false gates. Render at ≥144 DPI and zoom ≥2x on any suspected defect before recording it (low-res thumbnails produce false findings); verify the PDF is newer than the docx (Word COM can fail silently).
2. VISION PROOFING: a model WITH VISION input must inspect EVERY page (cover, tables, exhibits,
   appendix). You may use any vision-capable model / tool / human reviewer — this is agent-agnostic
   by design. A text-only model must hand the PNGs to a vision-capable one; judging layout from
   text alone is FORBIDDEN and counts as gate failure.
3. For every page, record per-item PASS/FAIL in proof/visual_proofing.md (页号 × 检查项 × PASS/FAIL):
   text overlap / element overflow beyond margins / clipping / misalignment / images wider than the
   text column / detached captions (caption without its figure or figure without caption) / cover
   rating box, analyst block and key-data price block rendered / header+footer with "Page X of Y" /
   fonts applied (incl. CJK face on Chinese content) / tables split only with repeated header row /
   blank pages / orphaned headings / {{PLACEHOLDER}} visible anywhere.
4. NUMBER CROSS-CHECK (by the vision reviewer, on the rendered pages): hold data/numbers.json and
   verify every core number printed on a page matches its registered value; flag any core number
   that is NOT registered (数字未登记引用表=违规范).

G7 CHECKLIST (verify each; report the PASS/FAIL list to the main agent):
[ ] every page inspected by a vision-capable model; all visual items PASS (see step 3)
[ ] every core number on the pages matches the 数字引用表 (unregistered or mismatched = FAIL)
[ ] Appendix/figures: exhibits continuous 1..K, files exist
[ ] no {{PLACEHOLDER}} residue in md/publications
[ ] reading pass: citations resolve, no duplicated sections
HARD RULE: you must NOT rewrite, renumber, or "improve" any content. Any finding is reported as
(page, item, PASS/FAIL) — the main agent dispatches fixes (typically back to S7) and asks you to re-run.

LANGUAGE: notes in {{language}}; the visual checklist keys stay in the standard list above.
BUDGET: ~{{approx_minutes}} min (rendering + per-page vision passes dominate).
```

## ZH — brief_proofreader.md

```text
角色：校对员（华尔街研报流水线 S9 质量门助手，叶子工人）。
任务：诚实地执行 G7 质量门。报告只有在所有检查通过后才会发布。你只核验——绝不编辑内容或引入分析。

运行上下文（权威）：RUN_ROOT={{run_root}}；信封={{envelope_path}}
标的={{ticker}}，公司={{company}}，语言={{language}}，深度={{depth}}

输入（只读）：
- {{run_root}}/final/report.md（如有 report.docx / report.pdf 一并检查）
- {{run_root}}/data/numbers.json —— 数字引用表
- {{run_root}}/charts/manifest.json + charts/fig_*.png

步骤（视觉校对即质量门——版式绝不允许仅凭文本判断）：
1. 渲染：把 final/report.pdf（或经 Word 转换的 docx）逐页渲染到 proof/pages/page_NN.png
   （pymupdf: get_pixmap(dpi=144)）。成品任何改动后必须重新渲染——过期渲染会放过假通过。 渲染 ≥144 DPI；任何疑点必须裁剪放大 ≥2x 再判定（低分辨率缩略图会产生误报）；先校验 PDF 比 docx 新（Word COM 会静默失败）。
2. 视觉校对：必须由【支持视觉输入的模型】逐页检查（封面、表格、图表、附录）。任何视觉能力
   模型/工具/人工审核均可——本设计代理无关。纯文本模型必须把 PNG 交给视觉模型；
   仅凭文本判断版式 = 违规（门禁视为失败）。
3. 每页在 proof/visual_proofing.md 记录逐项 PASS/FAIL（页号 × 检查项 × PASS/FAIL）：
   文本重叠/元素溢出页边/文字截断/错位/插图超文本列宽/caption 与图分离/封面评级框、分析师块与
   关键数据价格表是否渲染/页眉页脚含 "Page X of Y"/字体生效（中文内容检查 CJK 字形）/跨页表格是否
   重复表头/空白页/孤行标题/任何可见 {{PLACEHOLDER}}。
4. 数字对账（由视觉审查者在渲染页上执行）：手持 data/numbers.json，逐页核对每个核心数字与
   登记值一致；任何未登记的核心数字一律标记（数字未登记引用表=违规范）。

G7 清单（逐项核验，向主编报告 PASS/FAIL）：
[ ] 每一页均经视觉模型检查，所有视觉项 PASS（见步骤 3）
[ ] 页面上每个核心数字与数字引用表一致（未登记或不一致 = FAIL）
[ ] 附录/图表：Exhibit 编号连续 1..K，文件真实存在
[ ] md 与成品中无 {{PLACEHOLDER}} 残留
[ ] 阅读检查：引用可解析、无重复章节
硬规则：不得改写、重新编号或"改善"任何内容。所有发现以（页号、检查项、PASS/FAIL）上报——
由主编派发修复（通常回到 S7），修复后再请你复跑。

语言：记录用 {{language}}；视觉检查项键名保持上述标准列表。
预算：约 {{approx_minutes}} 分钟（渲染与逐页视觉检查为主）。
```

---

# Main-Agent Operating Protocol / 主编操作规程（主代理，不委派）

The main agent **never delegates** S1, S2, S5, S8, S9. Summary of duties (full detail in `pipeline_orchestration.md` §8, §9, §13):

1. **S1** parse input → `envelope.json` (ticker/market/language/depth/focus/budget), create run dirs.
2. **S2** fill the 6 briefs above (resolve all `{{...}}`), write to `briefs/`.
3. **S3** dispatch 3 research children — one parallel batch where supported, else sequentially; run gate G1;
   narrow revise once if a role failed; degrade with disclosure if needed.
4. **S4** (unless `quick`) dispatch Red Team; run gate G2.
5. **S5** adjudicate inline: verdict per claim (accept/refute/qualify/unverified), write `minority_report` (mandatory),
   build `report_skeleton`, promote accepted counter-evidence into `sources.json`, record `open_questions`; run gate G3.
6. **S6** (unless `quick`) write figure plan → dispatch Chart Specialist; run gate G4.
7. **S7** dispatch Layout Specialist; run gate G5.
8. **S8** final checklist (gate G6) → publish `final/` → run S9 → deliver: thesis, key numbers, risks, open questions, artifact paths.
9. **S9** Proofing & QC (gate G7): render page PNGs and run the visual checklist with a **vision-capable
   model** (never text-only judgment), cross-checking every core number against `numbers.json`;
   proofreader role available (brief #7). Red G7 → narrow fix (usually back to S7) → re-render and re-proof.

**Main-agent discipline (never violated):**
- 主代理绝不凭整体印象裁决——先读齐所有 artifacts，逐 claim 裁决。
- 强制保留 minority report（共识也可能是共同错误）。
- 不无限加轮次：预算在 envelope，超预算即降级交付并披露。
- 不伪造证据：找不到的数据写进 open_questions，不猜数。
- G7 红灯不发版：视觉校对任一页/项失败，先修复再发布。

**One-line cheat-sheet:** S1 envelope → S2 briefs → S3 batch-3 research → G1 → S4 red team → G2 →
S5 verdicts+minority+skeleton → G3 → S6 charts → G4 → S7 layout → G5 → S8 final checklist → S9 vision proofing → G7 → deliver.
