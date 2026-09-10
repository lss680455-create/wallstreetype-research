# S1 — Industry Logic Mapping & Direction Check / 产业逻辑梳理与方向确认

> **Pipeline stage: S1** — runs **immediately after S0 (intake)** and **before S2 (envelope)**. It is the last thing
> that happens before any data is fetched or any child is dispatched.
> 流水线第 1 阶段：紧接 S0（意向采集）之后、S2（任务信封）之前——在所有取数与子代理派发之前，先把"逻辑方向"钉死。
>
> **Agent-agnostic / 代理无关:** any AI tool (Claude Code, Codex, Cursor, Hermes, a plain chat model) or a human can
> execute this stage by reading this file. No tool-specific syntax, no vendor hooks.
> 任何 AI 工具或人工都能照做；本文只有流程、问题与文件约定。

- Companion artifacts / 配套产物:
  - `scripts/intake/direction_check.py` — `--skeleton` prints the empty contract; `--check` validates it (gate G0b), stdlib only.
- Output / 产出: **`brief/industry_logic.md`** (the logic map) + **`brief/direction_confirmed.json`** (the direction contract),
  both copied into `{RUN_ROOT}/briefs/` at S2 and consumed through S10.

---

## 1. When this runs / 触发时机

Run S1 at the start of **every new report task**, after the S0 answers exist and before the envelope is built:

1. **Any new run / 任何新一轮.** S0 gives the form (layout, depth, language, chart density); S1 gives the direction.
   Neither alone is enough to write a brief.
2. **The user stated only a ticker / 用户只给了标的.** Then the driver candidates, the competitive set and the
   falsification condition are all unknown — ask (§4). A ticker is not a research question.
3. **The user already stated a thesis / 用户已自带论点.** Still run Part A: map the chain and tag the drivers, then use
   §4 to confirm that the stated thesis is the one the pipeline should spend its budget on (it can be re-worded, narrowed
   or rejected by the user — that is the point of the check).
4. **One direction check per run.** Do not re-ask mid-run; if the user changes their mind, update
   `brief/direction_confirmed.json`, note it in `decision.json → open_questions`, and disclose it in the summary.
5. **The user says "you decide" / 用户说"你定".** Offer the recommended option **with its reason**, require a yes/adjust,
   and record `answered_by: "user-delegated"` — that is an answer. Silently applying a default is not.
6. **The user is unreachable and the run must proceed / 联系不上又必须开跑.** Set `direction_assumed: true`, list every
   assumed value in `assumed_values[]`, and print that list on the report's cover note. Never bury an assumption in the
   body text.

**中文：** 每轮任务在 S0 之后、信封之前必经此环：S0 定形式，S1 定方向。用户只给标的或自带论点时都要跑
（自带论点也要核对，允许被改写/收窄/否决）。每轮只问一次；用户答"你定"须给推荐值+理由并请其确认，记
`answered_by: "user-delegated"`；确实联系不上又必须开跑，置 `direction_assumed: true` 并在报告封面列出全部假设，
不得把假设埋进正文。

---

## 2. How to run it / 执行方式（三种，产物相同）

| Mode | Who | How |
|---|---|---|
| **A. Agent-driven**（推荐） | the agent | Do Part A (§3) with the information at hand, present the driver candidates + chain, then ask the six questions (§4) in chat, echo the answers, and write both artifacts. |
| **B. Skeleton + fill** | agent or human | `python scripts/intake/direction_check.py --skeleton > brief/direction_confirmed.json`, then fill in the six answers by hand; write `brief/industry_logic.md` per the §5 template. |
| **C. Validate** | agent or human | `python scripts/intake/direction_check.py --check brief/direction_confirmed.json` — prints the G0b checklist, exit code 0 = pass. |

All three modes produce the **same two artifacts** — the pipeline only depends on the files, never on how they were made.
**中文：** 三种方式（代理对话式 / 骨架手填 / 校验）产物完全一致，流水线只认文件。

---

## 3. Part A — Industry logic mapping / 产业逻辑梳理（五步）

The output is a **map that can be argued with**, not a summary of the industry. Do it *before* asking the questions,
because the question options (§4) must be derived from it — that is what keeps the questionnaire from degenerating into
"what would you like to hear?".

### A1. How the company actually makes money / 靠什么赚钱
Revenue by segment / product / geography **with shares**. If the company has no revenue yet (pre-commercial, just listed),
write **"no revenue yet"** and name the metric that would confirm the business exists (first paid deliveries, first
recurring contract, design-win count). **A narrative is never laundered into revenue.** 未产生收入的标的必须明写，
并指出"什么指标出现才算生意成立"；不接受把故事写成收入。

### A2. Chain position / 产业链定位
Upstream → the company → downstream. For each link: **who holds pricing power**, where the profit pool sits, and whether
the company is a **price-maker or price-taker**. Name the input it must buy and the audience it must sell to.
每一环都要标议价权归属；公司是价格制定者还是价格接受者。

### A3. Demand drivers / 需求驱动变量
Decompose revenue into **volume × price × mix**, then name the **2–3 variables that actually move the equity** and tag each:

| Driver | Tag | Observable proxy |
|---|---|---|
| … | `direct` — moves this company's P&L 直接进本公司损益 | the series that would show it |
| … | `theme` — moves the sector narrative only 只影响板块叙事 | the series that would show it |

**Rule / 硬规则:** a `theme` driver may never be written up as a company revenue driver. Subsidy lists, industry plans,
"national strategy", index inclusion, peer sentiment — these are `theme` unless the company's own P&L line is identifiable.
政策/主题类利好只能标 `theme`，除非能指名到本公司某一条损益科目。**At least one `direct` driver is required** —
a company with no direct driver is a trade, not a research subject, and that is a finding worth stating out loud.

### A4. Transmission chain / 传导链
Write the chain explicitly and give **every hop an observable proxy**:

```
driver → company revenue → margin → multiple
   ↑ proxy      ↑ proxy       ↑ proxy
```

A proxy is a specific, fetchable series: order intake, tenders won, shipments, capacity utilisation, ASP, inventory
cycle, a policy document number with its date, a customer's capex line. **A hop with no proxy is marked `unverifiable`** —
which obliges the report to say "this link is unproven" instead of asserting it. 缺代理指标的那一跳标 `unverifiable`，
报告里写"未证实"。

### A5. Cycle & relative position / 周期与相对位置
The industry's phase (emerging / growth / mature / declining) **with the base rate** for that phase, and the company's
relative position: share, capacity, technology gap against the strongest comparable, and how far the market's implied
expectation sits from the base rate. 行业阶段+基准率，公司相对位置（份额/产能/技术代差）。

---

## 4. Part B — Direction confirmation questions / 方向确认问卷（6 问）

Ask these **after** Part A, in chat, as a numbered block. Options marked ★ are the ones Part A suggests — the agent
recommends, **the user decides**. 六问一次问完（5–6 问，不要拆成审问），★ 为 Part A 推导出的推荐项，由用户拍板。

| # | Question / 问题 | Field | Options / 选项 | Feeds / 影响 |
|---|---|---|---|---|
| Q1 | **视角与期限** — 这份报告替谁、看多久？ | `view` | ★`fundamental` 6–12 个月 · `trade` ≤3 个月 · `trend` 3 年+ | 估值方法权重（倍数 / DCF / 情景中枢）、报告期限口径、催化剂日历 |
| Q2 | **主线变量** — 哪一条驱动是这份报告的论点轴？（可重排、可新增） | `primary_driver` | 来自 A3 的候选：★第一个 · 其余 · 用户自定义 | 全篇论点轴、各分析师的透镜权重、章节顺序 |
| Q3 | **核心假设锚点** — 量/价用哪套假设？ | `assumption_anchor` | ★`consensus` 一致预期 · `company_guidance` 公司指引 · `user_range` 用户给区间 · `historical_extrapolation` 历史外推 | 情景表的中性情形、敏感性矩阵的锚 |
| Q4 | **真正的对手是谁** — 替代品还是同业？（可多选） | `competitive_set` | ★直接同业 · 替代技术 · 相邻巨头跨界 | 同业对比表、相对估值、对比图 |
| Q5 | **什么会让你认输** — 出现什么可观测信号就否决这条逻辑？ | `falsification` | 由 A4 的代理指标生成候选（订单 / 出货 / ASP / 产能利用率 / 毛利 / 政策文件编号） | 红队简报的攻击目标、风险页、监控清单 |
| Q6 | **产出取向** — 要一份什么形态的报告？ | `output_orientation` | ★`valuation-driven` 估值驱动 · `event-driven` 事件驱动 · `thematic` 主题梳理；侧重 `growth` / `risk` / `valuation` | 骨架顺序、图表计划、篇幅分配 |

**Rules for asking / 提问纪律:**

1. **Options come from Part A.** Never present a menu that Part A did not derive. 选项必须来自 Part A 的产物。
2. **No leading questions.** Never "you're bullish, right?" — ask which of the candidates wins, and why. 不问引导性问题。
3. **Every option carries a consequence.** State in one clause what changes if the user picks it (e.g. `trade` → no
   long-DCF, the report opens on the catalyst calendar). 每个选项要说清"选了会怎样"。
4. **"你定" is an answer, indifference is not.** If the user declines to choose, give a recommendation **and the reason**,
   take an explicit yes or an adjustment, record `answered_by: "user-delegated"`. 用户不选则给推荐+理由，须得到明确同意或修正。
5. **Do not extend the list.** Six questions, one pass. If something is still unclear, it belongs in
   `decision.json → open_questions`, not in a seventh question. 只有六问；剩余疑问进 open_questions。
6. **The answers outrank the agent.** Once confirmed, they are contract: mid-run changes must update
   `brief/direction_confirmed.json` and be disclosed. 答案一经确认即契约；中途变更须更新文件并披露。

---

## 5. Output artifacts / 落盘格式

### 5.1 `brief/industry_logic.md` — the logic map / 产业逻辑图

```markdown
# Industry logic — <company> (<ticker>)   |   S1

## 1. How it makes money
- <segment> — <share>% of revenue; <one line on the mechanism>
- (or: **no revenue yet** — the business is confirmed when <metric> appears)
- Chain position: <upstream> → <company> → <downstream>; pricing power at this link: <who>; role: price-maker|price-taker

## 2. Driver table
| Driver | Tag | Observable proxy | Source |
|---|---|---|---|
| <driver> | direct | <series to fetch> | <where> |
| <driver> | theme | <series to fetch> | <where> |

## 3. Transmission chain
<driver> → <revenue line> → <margin> → <multiple>
  hop 1 proxy: <series>   hop 2 proxy: <series|unverifiable>   hop 3 proxy: <series|unverifiable>

## 4. Cycle & relative position
- Phase: <emerging|growth|mature|declining>; base rate: <what usually happens>
- Company vs strongest comparable: share <x%> vs <y%>; capacity <…>; technology gap <…>

## 5. What would break this / 这份逻辑的断点
- <the hop most likely to fail, and the proxy that would show it>
```

### 5.2 `brief/direction_confirmed.json` — the direction contract / 方向契约

Field set (validated by `scripts/intake/direction_check.py`):

| Field | Type | Notes |
|---|---|---|
| `ticker`, `as_of` | string | instrument + the date the direction was confirmed |
| `view` | enum | `trade` \| `fundamental` \| `trend` |
| `primary_driver` | string | the thesis axis (Q2); must match one of the `driver_tags` entries |
| `driver_tags[]` | array | `{driver, tag: direct\|theme, proxy}`; ≥1 `direct` |
| `assumption_anchor` | enum | `company_guidance` \| `consensus` \| `user_range` \| `historical_extrapolation` |
| `assumption_note` | string | free text: the range the user gave, or "no override, use consensus" |
| `competitive_set[]` | array[string] | Q4; peers, substitutes, adjacent entrants |
| `falsification` | string | Q5; **must be observable** — "sentiment turns" fails the gate |
| `output_orientation` | object | `{orientation: valuation-driven\|event-driven\|thematic, emphasis: [growth\|risk\|valuation]}` |
| `answers[]` | array | one entry per Q1–Q6: `{q, field, answer, answered_by, note}` |
| `direction_assumed` | bool | `true` only if the user was unreachable and the run proceeded |
| `assumed_values[]` | array | required when `direction_assumed` is `true`; each item is printed on the cover note |
| `created_at` | string | ISO-8601 with timezone offset |

See `pipeline_orchestration.md` §10 for a fully worked example.

---

## 6. How the answers are injected / 答案如何注入后续阶段

| Answer | Injected at / into | Effect / 作用 |
|---|---|---|
| `primary_driver` | S3 role briefs → S4 research scope → S6 skeleton | Decides the thesis axis: which claims must exist, which section leads, what the analysts weight. The Industry and Valuation analysts must answer the chain in `industry_logic.md` explicitly. |
| `view` | Valuation model, scenario periods, report framing | `trade` → trading framing + catalyst calendar first, no long-DCF; `fundamental` → 12-month target price and scenarios; `trend` → 3–5-year compounding case, penetration math. |
| `assumption_anchor` | Scenario table (base case), sensitivity matrix | `consensus` → base case = consensus band; `company_guidance` → guidance is the base; `user_range` → the user's numbers are the base and get an explicit note; `historical_extrapolation` → the trailing growth rate with a decay assumption stated. |
| `competitive_set` | S7 peer chart, relative valuation, moat section | Defines who "the peer group" is — including substitutes and adjacent giants, which is where most peer tables go wrong. |
| `falsification` | S5 Red Team brief, risk section, monitoring list | The Red Team's job is to attack **this** condition, not to wander; the risk page must restate it in observable terms. |
| `output_orientation` | S6 skeleton order + S7 figure plan | `valuation-driven` → valuation first, multiples-centric figures; `event-driven` → catalyst calendar leads; `thematic` → chain map and penetration leads. Emphasis decides whether growth, risk or valuation sections are budget-heavy. |
| `direction_assumed` | Cover note + delivery summary | Assumed directions must be visible to the reader, not buried. |

**中文：** `primary_driver`→论点轴与透镜权重（行业/估值分析师必须回答产业逻辑图上的问题）；`view`→估值窗口与方法权重；
`assumption_anchor`→情景中性情形；`competitive_set`→同业对比与相对估值（含替代技术与跨界巨头）；`falsification`→红队主攻方向与风险页；
`output_orientation`→骨架顺序与图表计划；`direction_assumed`→封面与交付摘要必须列明。

---

## 7. S1 quality gate (G0b) / 质量门

Before proceeding to S2, every item must pass
(`python scripts/intake/direction_check.py --check brief/direction_confirmed.json`):

- [ ] All **six** questions answered in `answers[]`; `answered_by ∈ {user, user-delegated}`.
      **No `agent-default` filling.** 六问全答；不得由代理自填默认值。
- [ ] `view`, `assumption_anchor`, `output_orientation` are inside their allowed sets.
- [ ] `driver_tags[]` non-empty, every driver tagged `direct|theme`, **≥1 `direct`**.
- [ ] Every transmission hop carries an observable proxy, or is marked `unverifiable` in `industry_logic.md`.
- [ ] The chain position names **who holds pricing power**; the company's role (price-maker/taker) is stated.
- [ ] `falsification` is **observable** (a series or an event that can be checked), not a mood.
- [ ] `direction_assumed` is `false`, or it is `true` **and** `assumed_values[]` is non-empty and will be printed on the cover.
- [ ] Both artifacts written; answers echoed back to the user (one compact block).

**Fail →** re-ask the unanswered question once, attached to the recommended option; if the user still declines, record
their words verbatim as the answer; if the user is unreachable and the run must proceed, apply the recommendation with
`direction_assumed: true` and full disclosure. **Never invent a direction the user did not give.**
不合格→把没答的那题连同推荐项再问一次；用户仍不选则原话记录；联系不上又必须开跑：用推荐值 + `direction_assumed: true`
+ 封面披露。**绝不编造用户没给过的方向。**

---

## 8. Discipline / 纪律

1. **Two kinds of questions, two kinds of default.** S0 may degrade to documented defaults (a form default is a taste).
   S1 may not (a direction default is a fabricated thesis). 形式可默认，方向不可默认。
2. **`theme` ≠ driver.** Policy/theme tailwinds are tagged `theme` until a company P&L line can be named. 政策主题只算 theme。
3. **No hop without a proxy.** Mark it `unverifiable` and say so in the report. 缺代理指标就标未证实。
4. **Six questions, one pass.** Ask everything at once, never drip-feed. 一次问完六问。
5. **The contract is visible.** Confirmed answers, and any assumed ones, appear in the run artifacts and the summary.
6. **Agent-agnostic.** This stage is a text procedure plus one stdlib script; any agent or human can execute it.

**中文：** 形式可默认、方向不可默认；政策主题≠收入驱动；每一跳要代理指标；六问一次问完；答案与假设都要可见；
任何代理或人工都能执行。
