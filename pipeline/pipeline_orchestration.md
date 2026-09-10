# Wall Street Research — Multi-Agent Pipeline Orchestration Design

> Part of the **Wall Street Research** skill (portfolio piece + open-source).
> This document defines **how the report pipeline is orchestrated with parallel child agents**.
> Data / charts / layout / methodology modules are built by other workstreams; this doc only defines
> how the pipeline calls them and the **file handoff conventions** between stages.
> 本文只定义编排：数据/图表/排版/范式模块由其他子代理实现，本流水线通过约定文件路径调用它们。

- Version: 2.1.0
- Status: design
- Companion files:
  - [`intake.md`](intake.md) — **S0 intake**: layout-template choice + research-focus questionnaire (bilingual).
  - [`agent_prompts.md`](agent_prompts.md) — copy-paste-ready bilingual briefs for every role.
  - `../scripts/intake/intake.py` — one-shot CLI that writes `brief/intake.json` (stdlib only).
- **Agent-agnostic / 代理无关:** this pipeline runs on **any** AI tooling — Claude Code, Codex, Cursor, OpenAI agents,
  open-source models, or a human following the steps manually. No platform-specific hooks, no vendor lock-in.

---

## 1. Purpose & Scope / 目标与边界

Deliverable: a complete, **agent-agnostic, portable** investment-research pipeline driven by a **main agent** that
delegates well-scoped subtasks to **child agents** (or executes them sequentially when parallelism is unavailable).

**Hard constraints (self-containment):**

| Constraint | Meaning |
|---|---|
| Agent-agnostic | No Hermes/Claude/Codex-specific API, tool syntax, or skill mechanism. The pipeline is described as a **pure workflow** (stages / roles / files / quality standards) any agent — or a careful human — can execute. |
| Plain-text briefs | Every role brief is a plain-text document you copy into any agent. No tool-call syntax, no vendor commands. |
| No hardcoded machine paths | All file references are **relative to a runtime-injected `RUN_ROOT`**. Runs live under `{workspace}/runs/{run_id}/` at runtime. |
| Mechanical work via stdlib Python | Data fetching, chart rendering, and layout conversion are provided as **cross-platform Python scripts** (`scripts/data/`, `scripts/charts/`, `templates/`) that any agent can invoke with `python`, or a human can run directly. |
| Bounded cost | Fixed rounds, fixed worker counts, per-depth budgets. No runaway recursion (children are leaf workers). |
| Auditable | Every claim, review, and verdict is a structured JSON artifact with evidence references. |

**What this document does NOT cover** (other workstreams): data-provider implementation, chart library,
layout/template engine, research methodology content. The pipeline treats them as **modules** reached by convention paths.

---

## 2. How to Run in Any AI Environment / 如何在任意AI环境中运行

The pipeline is a **workflow**, not a program. You drive it in five moves:

0. **Intake (S0).** Ask the user for the two pre-run answers — **layout template** and **research focus** —
   and write `brief/intake.json` (follow [`intake.md`](intake.md); or one-shot it with
   `python scripts/intake/intake.py --template <id> --focus ...`). If the user is unavailable, apply the
   documented defaults and say so. This stage is never skipped silently.
1. **Prepare.** Create a run directory; write `envelope.json` (the input contract, §5) and the six role briefs
   (§ in `agent_prompts.md`) with placeholders filled in. Copy `brief/intake.json` into
   `{RUN_ROOT}/briefs/intake.json` and wire its values into the envelope.
2. **Dispatch children.** Copy the relevant brief (plain text) to a child agent for each research role
   (Data Engineer, Industry Analyst, Valuation Analyst). **If your tool supports parallel child agents, start the
   three research roles at the same time.** If not, run them one after another — the artifacts they write are identical
   either way. The main agent then drives the remaining stages the same way (Red Team → adjudicate → Charts → Layout).
3. **Run the scripts for mechanical work.** Data acquisition (`scripts/data/data_fetcher.py`), chart rendering
   (`scripts/charts/report_charts.py`), and layout conversion (`templates/md_to_docx.py`) are stdlib-Python scripts. Hand them to
   an agent with code-execution, or run them yourself. Agents **never hand-type data** — they call the scripts or fetch
   and save files directly; a human can also fetch/save manually and mark sources.
4. **Adjudicate & deliver.** The **main agent** (never a child) does the final per-claim adjudication, keeps a minority
   report, runs the quality gates, and publishes the final report.

```
 main agent ── S0 intake ── S2 envelope ── S3 briefs ──┬── [child] Data Engineer   ─┐
                                                       ├── [child] Industry Analyst ─┼── parallel (or sequential) ── S6 main-agent adjudication
                                                       └── [child] Valuation Analyst┘        │
                                                S5 [child] Red Team ────────────────────────┘
                                                S7 [child] Chart Specialist ─ S8 [child] Layout Specialist ─ S9 main-agent final QA ─ S10 main-agent Proofing & QC (vision proofing gate) ─ deliver
```

**Key principle:** the pipeline's *correctness* depends on the workflow (files + gates), **not** on any specific agent
runtime. Parallelism is an optimization, never a requirement.

---

## 3. Agent Capabilities Required / 所需代理能力

The pipeline needs only capabilities nearly every AI agent (and a diligent human) has:

| Capability | Used by | Notes / fallback |
|---|---|---|
| Read/write files | all roles | file I/O; JSON + Markdown + CSV |
| Run Python (optional but recommended) | Data/Chart/Layout stages | for the `src/*` scripts; a human can run them instead |
| Web access (optional) | Data Engineer, Red Team | fetching sources; if unavailable, the human supplies sources and the agent works from `data/` |
| Execute the "dispatch" pattern | main agent | start child roles in parallel if supported; otherwise sequential |

**Parallelism policy (agent-agnostic):**
- Preferred: main agent starts the 3 research children **in parallel** in one dispatch batch.
- Fallback: run the same 3 roles **sequentially** — each writes its own files; no stage depends on another role's *in-memory*
  state, only on its files. Results are identical.
- Children are **leaf workers**: they execute their role only and never spawn further agents (keeps cost bounded and
  prevents runaway recursion). The **main agent is the only orchestrator** and the only adjudicator.

---

## 4. Workspace & File Handoff Conventions / 工作区与文件交接约定

The pipeline is **run-root relative**. The main agent creates the run at runtime and injects the absolute path as `RUN_ROOT`.

```
{workspace}/brief/intake.json         # S0 intake contract (pre-run; written before RUN_ROOT exists)
{workspace}/runs/{run_id}/            # RUN_ROOT (created by main agent at S2)
├── envelope.json                     # task contract (input; S0 intake values wired in)
├── briefs/                           # master brief + per-role briefs (audit trail)
│   ├── intake.json                   # copy of the S0 intake — run self-containment
│   ├── master_brief.md
│   └── brief_<role>.md               # data_engineer | industry | valuation | redteam | chart | layout
├── data/                             # SINGLE WRITER: Data Engineer
│   ├── manifest.json                 # inventory of fetched data (id, path, fetched_at, freshness_tier)
│   ├── sources.json                  # source registry (S001, S002, ...) — single source of truth for citations
│   ├── numbers.json                  # 数字引用表 (number reference table) — every core number the report will
│   │                                 #   carry: label → data file+path → display format. Consumed by the S10
│   │                                 #   vision proofing as its cross-check reference. Numbers NOT registered
│   │                                 #   here are a violation by rule (数字未登记引用表=违规范), caught at S10/G7.
│   ├── fundamentals.json             # financial statements / key metrics (per market)
│   ├── price_history.csv             # price/volume series (for charts)
│   ├── estimates.json                # consensus estimates, guidance, company targets (optional)
│   └── <market_specific>.json        # e.g. hk_announcements.json, cn_announcements.json
├── research/                         # analysts write ONLY their own files
│   ├── industry.md                   # Industry Analyst narrative
│   ├── valuation.md                  # Valuation Analyst narrative
│   ├── claims_industry.json          # ClaimArtifacts (IND-*)
│   └── claims_valuation.json         # ClaimArtifacts (VAL-*)
├── review/                           # SINGLE WRITER: Red Team
│   ├── redteam.md                    # adversarial narrative + top risks
│   └── reviews.json                  # ReviewArtifacts (RV-*)
├── decisions/                        # SINGLE WRITER: main agent (adjudication)
│   └── decision.json                 # per-claim verdicts + minority report + report skeleton
├── charts/                           # SINGLE WRITER: Chart Specialist
│   ├── manifest.json                 # figure plan + produced files
│   └── fig_*.png                     # figures (also .svg where supported)
├── draft/
│   └── report_draft.md               # SINGLE WRITER: Layout Specialist
├── final/                            # SINGLE WRITER: main agent
│   ├── report.md
│   └── report.docx / report.pdf      # via templates/md_to_docx.py, if present
└── proof/                            # SINGLE WRITER: main agent (S10)
    ├── visual_proofing.md            # per-page visual checklist (页号 × 检查项 × PASS/FAIL)
    └── pages/                        # page_*.png renders of report.pdf for vision proofing
```

**Handoff contract for the modules (charts / layout / data):**

| Module | Invoked by | Reads | Writes |
|---|---|---|---|
| Intake module (`scripts/intake/`, `pipeline/intake.md`) | main agent at S0 | — | `brief/intake.json` |
| Data module (`scripts/data/`) | Data Engineer at S4 | — | `data/*` (convention above) |
| Chart module (`scripts/charts/`) | Chart Specialist at S7 | `data/*`, `charts/manifest.json` plan | `charts/fig_*.png` |
| Layout module (`templates/`) | Layout Specialist at S8 | `decisions/decision.json`, `research/*`, `review/*`, `charts/*` | `draft/report_draft.md`, `final/report.*` |
| Methodology (repo `methodology/`, `METH-*` section refs in `methodology/wallstreet_paradigm_manual.md`) | all roles, esp. main agent at S6/S9 | — | — |

**Cross-writing rule (non-negotiable):** a role may write **only** its own output files listed in its brief. Nobody
writes into another role's directory. Data is single-writer (`data/`); the source registry (`data/sources.json`) is
appended to only by the Data Engineer; new sources discovered by other roles are recorded in their own artifact and
**promoted by the main agent after adjudication** (S6).

---

## 5. Input Contract — TaskEnvelope / 输入契约

`envelope.json` is the single input artifact; every brief references it. Fields marked **(S0)** are wired
from `brief/intake.json` (S0); the intake file remains the source of truth for those answers.

```json
{
  "run_id": "ws_20260910_ab12",
  "ticker": "TSLA",
  "company": "Tesla, Inc.",
  "market": "US",
  "language": "en",
  "depth": "standard",
  "template_id": "goldman_hardline",
  "focus_areas": ["valuation", "growth"],
  "horizon": "medium",
  "chart_density": "high",
  "currency": "USD",
  "focus_question": "Is Tesla's energy-storage segment a material re-rating driver over 12 months?",
  "constraints": ["no short-term trading calls", "12-month horizon"],
  "budget": { "max_rounds": 1, "max_sources_per_claim": 5, "max_claims_per_analyst": 25, "approx_minutes": 60 },
  "created_at": "2026-09-10T01:20:00+08:00"
}
```

| Field | Required | Notes |
|---|---|---|
| `run_id` | yes | auto-generated `ws_YYYYMMDD_xxxx` |
| `ticker` / `company` | yes | primary identifiers |
| `market` | yes | US / HK / CN / EU / ... — selects data conventions (currency, filing language, data-script behavior) |
| `language` | yes | `en` (default) / `zh` / `bilingual` — report language; sources may stay in their native language |
| `depth` | yes | `quick` / `standard` / `deep` — see §12; taken from `brief/intake.json` when present |
| `template_id` **(S0)** | no | layout template id from `brief/intake.json`; passed to S8/S9 as `md_to_docx.py --style <id>` |
| `focus_areas` **(S0)** | no | research lenses from intake (`valuation` / `growth` / `cyclical` / `event-driven` / `defensive` / `bull-bear`); weights the briefs, the Red Team and the report skeleton |
| `horizon` **(S0)** | no | `short` / `medium` / `long`; sets the valuation & scenario window |
| `chart_density` **(S0)** | no | `low` / `standard` / `high`; caps/expands the S7 figure plan |
| `focus_question` | no | optional single question the report must answer (derive from `focus_areas` if absent) |
| `budget` | yes | filled from depth-tier defaults; the main agent may tighten for cost control |

---

## 6. Role Roster & Lens Boundaries / 角色与透镜边界

**8 roles (lenses are disjoint; role 8 is optional at S10). Lenses are disjoint — each role owns exactly one layer and must NOT cross into another's.**

| # | Role | Lens (one line) | Owns | Explicitly NOT allowed |
|---|---|---|---|---|
| 1 | **Data Engineer** 数据工程师 | **Facts & numbers**: what the numbers *are* | acquisition, freshness, source grading, dedup, manifest | interpretation, opinions, valuation, thesis writing |
| 2 | **Industry Analyst** 行业分析师 | **Business & competition**: why the business works or fails | industry structure, moat, demand/supply drivers, regulation | fetching new raw data (uses `data/`), target prices, modeling |
| 3 | **Valuation Analyst** 估值分析师 | **Price & expectations**: what the business is *worth*, what's priced in | financial model, base/bull/bear scenarios, target range, catalysts, risk-adjusted return | re-litigating industry facts, raw data fetching |
| 4 | **Red Team** 质询官 | **Counter-evidence & falsification**: what could be *wrong* | attacks on every claim, stress tests, red flags, falsification conditions | producing new positive claims; writing to `data/` or `research/` |
| 5 | **Main Agent / Editor-in-Chief** 主编（主代理，不委派） | **Synthesis & adjudication**: what the report will *conclude* | briefs, per-claim verdicts, minority report, report skeleton, quality gates, final delivery | fabricating evidence; delegating the adjudication itself |
| 6 | **Chart Specialist** 图表师 | **Visual evidence**: figures that make claims legible | figure selection, data→chart mapping, annotations | new analysis, changing numbers, writing claims |
| 7 | **Layout Specialist** 排版师 | **Structure & readability**: a report a human can actually read | assembly, section order, typography, citations formatting, format conversion | content edits beyond mechanical fixes, new opinions |
| 8 | **Proofreader** 校对员 (S10, optional assistant) | **Compliance & polish**: does the report survive the quality gate | G7 checklist execution: vision-model proofing on per-page renders, number-reference-table cross-check | new analysis content, rewriting prose, changing numbers — the proofreader VERIFIES, never edits content |

Roles 1–4 and 6–7 are **leaf child agents** (8 is an optional S10 assistant, still a leaf). The main agent (Editor, role 5) is the only orchestrator and adjudicator. The main agent also runs **S0 Intake** (template + focus questions → `brief/intake.json`) and **S1 Industry Logic Mapping** (chain map + the six direction questions → `brief/industry_logic.md`, `brief/direction_confirmed.json`); both stages are **never delegated**.

---

## 7. Pipeline Overview / 流水线总览

```
 S0  Intake                  ─ main agent (interactive)  → brief/intake.json (template + focus)
 S1  Industry Logic Mapping  ─ main agent (interactive)  → brief/industry_logic.md, brief/direction_confirmed.json
 S2  Input & Envelope        ─ main agent                → envelope.json, run dir
 S3  Master Brief            ─ main agent                → briefs/*.md
 S4  Parallel Research       ─ 3 leaf children, one batch→ data/*, research/*, claims_*.json
 S5  Red Team Challenge      ─ 1 leaf child              → review/redteam.md, reviews.json
 S6  Editorial Adjudication  ─ main agent                → decisions/decision.json
 S7  Charting                ─ 1 leaf child              → charts/manifest.json, fig_*.png
 S8  Layout & Assembly       ─ 1 leaf child              → draft/report_draft.md
 S9  Final Review            ─ main agent                → final/report.*, run summary
 S10 Proofing & QC           ─ main agent (主编) + vision model → proof/* (visual proofing checklist) — QUALITY GATE G7
```

**11 stages (S0–S10), up to 4 dispatch waves** (all other work is done by the main agent; S0–S3 add no dispatch —
they are the two interactive stages + envelope + briefs, i.e. everything that must be settled *before* the first child
is dispatched):

| Wave | Stage(s) | Dispatch | Parallelism |
|---|---|---|---|
| W1 | S4 | start 3 children in one batch (Data Engineer, Industry, Valuation) | 3 children (fallback: sequential) |
| W2 | S5 | start 1 child (skip in `quick` tier) | 1 child |
| W3 | S7 | start 1 child (skip in `quick` tier) | 1 child |
| W4 | S8 | start 1 child | 1 child |

**S10 is run by the main agent (主编) without a child** — it is the stage that turns soft "quality advice" into a hard gate, judged by a **vision-capable model** on rendered pages. Standard/deep tiers proof every page; `quick` tier may reduce S10 to a spot-check of cover + first content page.

Max concurrent children needed: **3**. If a runtime caps concurrency below 3, run the research roles sequentially —
the workflow is unaffected.

---

## 8. Stage Specifications / 阶段规格

### S0 — Intake 任务前意向采集
- **Who:** main agent, **interactive with the user — never delegated**.
- **Input:** user preferences (or the documented defaults if the user is unavailable).
- **Procedure** (full text: [`intake.md`](intake.md)):
  1. **Template choice** — present the six style-only layout templates (`templates/styles/*.json`), one-line style
     + best-fit for each; the user picks one (mix / custom layout allowed — record the base id and describe the
     override in `special_requests`). List them with `python scripts/intake/intake.py --list`.
  2. **Focus questionnaire** — research focus (multi-select), horizon, depth, language, chart density,
     special requests (ESG / technicals / policy / peer comparison / ...). Every item has options and a default.
- **Output:** `brief/intake.json` (repo-level intake area) — fixed field set:
  `template_id`, `template_display_name`, `focus_areas[]`, `horizon`, `depth`, `language`, `chart_density`,
  `special_requests[]`, `created_at`. Write it by hand or run
  `python scripts/intake/intake.py --template <id> --focus valuation,growth --horizon medium --depth full --language en --charts high --notes "..."`.
- **Quality gate G0:** all nine fields present and valid (`template_id` ∈ the six template ids; `focus_areas`
  non-empty and within the allowed set; `horizon ∈ {short, medium, long}`; `depth ∈ {quick, standard, deep}`;
  `language ∈ {en, bilingual, zh}`; `chart_density ∈ {low, standard, high}`; `created_at` ISO-8601); the answers
  are echoed back to the user; any default applied is explicitly declared.
  **Fail →** ask once more for the missing/invalid item; still unavailable → apply defaults and disclose.
- **Injection:** `template_id` → S8/S9 `--style`; `focus_areas` → S3 brief lens weights + S5 Red Team priorities
  + S6 skeleton order; `horizon` → valuation/scenario window; `depth` → stage trimming (§12); `language` →
  envelope + all writing/chart labels; `chart_density` → S7 figure plan; `special_requests` → briefs, question
  bank, sections, disclosures. Full mapping: `intake.md` §6.

### S1 — Industry Logic Mapping & Direction Check 产业逻辑梳理与方向确认
- **Who:** main agent, **interactive with the user — never delegated.** Same class as S0: it settles a contract, it
  does not produce research. 与 S0 同属契约类阶段，主代理自己做，绝不委派给子代理。
- **Why it is its own stage / 为什么要单列一环:** the most expensive failure in research is a beautifully typeset report
  that answers a question nobody asked, built on a transmission chain that was never stated out loud. S0 fixes the
  *form* (layout template, depth, language, chart density); S1 fixes the **logic direction** before a single data file is
  fetched or a child is dispatched. The two question sets are deliberately separated: **S0 answers may be degraded to
  documented defaults, S1 answers may not** — a form default is a taste, a direction default is a fabricated thesis.
- **Input:** the user's request (ticker / market / the question they actually want answered) + `brief/intake.json`.
- **Procedure A — industry logic mapping** (full text: [`logic_mapping.md`](logic_mapping.md)); output
  `brief/industry_logic.md`:
  1. **How the company actually makes money** — revenue by segment / product / geography with shares. A company with no
     revenue yet (pre-commercial, newly listed) is stated as exactly that, together with the metric that will confirm the
     business exists. **A story is never laundered into revenue.** 未产生收入的标的必须明写，并指出"什么指标出现才算生意成立"。
  2. **Chain position** — upstream → the company → downstream; who holds pricing power at each link, where the profit pool
     sits, and whether the company is a price-maker or a price-taker. 产业链定位：公司在哪一环、议价权在谁手里、利润池在哪。
  3. **Demand drivers** — decompose revenue into volume × price × mix, then name the 2–3 variables that actually move the
     equity. **Every driver carries a tag: `direct` (moves this company's P&L) or `theme` (moves the sector narrative
     only). A `theme` driver may never be written up as a company revenue driver.** 政策/主题类利好只能标 `theme`，
     不接受"政策利好→公司收入"的跳步。
  4. **Transmission chain** — driver → revenue → margin → multiple, and **every hop carries an observable proxy**: a
     specific series that can be fetched and re-checked (order intake, tenders won, shipments, capacity utilisation, ASP,
     inventory cycle, a policy document number with its date). A hop with no proxy is marked `unverifiable` — which means
     the report must say the link is unproven instead of asserting it. 每一跳都要有可观测代理指标；没有就标
     `unverifiable`，报告里必须写"这一跳未被证实"，不得直接断言。
  5. **Cycle & relative position** — the industry's phase (emerging / growth / mature / declining) with the base rate for
     that phase, and the company's relative position: share, capacity, technology gap against the strongest comparable.
- **Procedure B — direction confirmation questions** (5–6 questions, answered by the user; full text
  [`logic_mapping.md`](logic_mapping.md) §4). They are not "what would you like to hear" — every option is *derived from
  Procedure A*, and the user confirms or overrides:

  | # | Question / 问题 | Field | Feeds / 注入 |
  |---|---|---|---|
  | Q1 | 视角与期限 — `trade` ≤3 个月 · `fundamental` 6–12 个月 · `trend` 3 年+ | `view` | valuation method weight (multiples vs DCF vs scenario centre), report window |
  | Q2 | 主线变量 — which driver is *the* axis (user may reorder or add one) | `primary_driver` | thesis axis, analyst lens weights, section order |
  | Q3 | 核心假设锚点 — `company_guidance` · `consensus` · `user_range` · `historical_extrapolation` | `assumption_anchor` | base case of the scenario table |
  | Q4 | 真正的对手 — direct peer · substitute technology · adjacent giant (multi-select) | `competitive_set` | peer table, relative valuation, comparison figure |
  | Q5 | 证伪条件 — the observable that would make the user drop the thesis | `falsification` | Red Team brief, risk section |
  | Q6 | 产出取向 — `valuation-driven` · `event-driven` · `thematic` ＋ 侧重 `growth`/`risk`/`valuation` | `output_orientation` | report skeleton order (S6), figure plan (S7) |

- **Output:** `brief/industry_logic.md` (the five moves, with the driver tags and the proxy table) +
  `brief/direction_confirmed.json` (the six answers, each with `answered_by ∈ {user, user-delegated}` and a
  run-level `direction_assumed` boolean). Both are copied into `{RUN_ROOT}/briefs/` at S2 so the run stays self-contained.
- **Quality gate G0b:** (1) all six questions answered — **a missing answer may not be silently defaulted**; (2) at least
  one `direct` driver, and every driver tagged; (3) every transmission hop carries an observable proxy or is marked
  `unverifiable`; (4) the chain position names who holds pricing power; (5) the falsification condition is observable
  ("sentiment turns" fails); (6) the file parses — `python scripts/intake/direction_check.py --check brief/direction_confirmed.json`.
  **Fail →** re-ask the unanswered question once, attached to the recommended option; if the user declines to choose,
  record their words as the answer; if the user is unreachable and the run must proceed, set `direction_assumed: true`
  and list every assumption on the report's cover note and in the delivery summary.
  不合格→把没答的那题连同推荐选项再问一次；用户仍不选则原话记录；仍联系不上又必须开跑：置
  `direction_assumed: true`，并在报告封面与交付摘要逐条列出假设——不得静默取默认值。
- **Depth tiers:** in `quick`, Procedure A is compressed (drivers + one-line chain, no full chain map); **Procedure B is
  never compressed or skipped in any tier** — it is the cheapest stage in the pipeline and the one that prevents the most
  waste. 任何档位都不跳过 Procedure B。
- **Injection:** `primary_driver` → S3 role briefs (lens weights) + S4 research scope + S6 skeleton axis; `view` →
  valuation window / multiple choice; `assumption_anchor` → scenario base case; `competitive_set` → peer figure (S7) +
  relative valuation; `falsification` → S5 Red Team brief + risk section; `output_orientation` → skeleton order (S6) +
  figure plan (S7). Full mapping: `logic_mapping.md` §6.

### S2 — Input & Envelope 输入与任务信封
- **Who:** main agent.
- **Input:** user request (ticker/market/language/depth/focus) + `brief/intake.json` — parsed, defaults applied
  (`language=en`, `depth=standard`; intake values override where present); copy the intake file into
  `{RUN_ROOT}/briefs/intake.json`.
- **Output:** `{RUN_ROOT}/envelope.json` with `template_id`, `focus_areas`, `horizon`, `chart_density`,
  `language`, `depth` wired in; creates `{RUN_ROOT}/` and subdirectories; **copies the S1 artifacts in** —
  `brief/industry_logic.md` → `{RUN_ROOT}/briefs/industry_logic.md` and `brief/direction_confirmed.json` →
  `{RUN_ROOT}/briefs/direction_confirmed.json` (the run then carries its own thesis contract, and a child never has to
  reach back to the repo root).
- **Quality gate G0c:** envelope validates (required fields present; `depth ∈ {quick, standard, deep}`; `language ∈ {en, zh, bilingual}`; budget fields filled; intake-derived fields consistent with `brief/intake.json`).

### S3 — Master Brief 简报
- **Who:** main agent.
- **Input:** `envelope.json`; brief templates from this repo (`agent_prompts.md`).
- **Output:** `briefs/master_brief.md` + `briefs/brief_<role>.md` for all 6 child roles — every placeholder
  (`{{run_root}}`, `{{ticker}}`, ...) resolved to concrete values.
- **Quality gate G0d:** every role brief exists and contains: role + lens, input paths, output path, quality checklist,
  budget/rounds, language. A brief missing its checklist is a defect — fix before dispatching.

### S4 — Parallel Research 并行研究
- **Who:** 3 leaf children in **one** dispatch batch: Data Engineer, Industry Analyst, Valuation Analyst.
- **Input (per child):** its filled brief (plain text) + full `envelope.json` + absolute `RUN_ROOT`. Because a child's
  context is fresh, **everything it needs must be inside the brief text** — never "see the conversation above".
- **Outputs:**
  - Data Engineer → `data/manifest.json`, `data/sources.json`, `data/*.{json,csv}`
  - Industry Analyst → `research/industry.md`, `research/claims_industry.json`
  - Valuation Analyst → `research/valuation.md`, `research/claims_valuation.json`
- **Quality gate G1 (main agent checks after the wave returns):**
  - [ ] All 3 artifacts exist and are non-empty (headings present; JSON parseable)
  - [ ] `sources.json` has a record for every `evidence_refs` id cited anywhere
  - [ ] Every claim has `type`, `confidence`, `evidence_refs`, and (for interpretive claims) `counterarguments` + `falsification_condition`
  - [ ] No file outside each child's own output path was modified (spot-check)
  - [ ] Analyst narratives do not contain a target price the valuation analyst did not derive, and vice versa no raw-data claims without a source ref
  - **Fail →** one bounded revise round: re-dispatch **only the deficient role** with a narrow "complete items X,Y,Z only" brief. Still failing → proceed degraded, record in `decision.json` → `open_questions`.

### S5 — Red Team Challenge 红队质询
- **Who:** 1 leaf child (Red Team). *Skipped in `quick` tier — the main agent runs an inline red-flag scan instead.*
- **Input:** `data/*`, `research/*`, `claims_*.json` (paths in the brief; child reads files itself).
- **Output:** `review/redteam.md` (narrative: top 5 risks, strongest counter-arguments, red flags) + `review/reviews.json`
  (one `RV-*` entry per claim or claim-cluster; verdicts `support | refute | qualify | unverified`).
- **Rules:** may introduce **new counter-evidence**, recorded inline in `reviews.json` (`counter_evidence_refs` with
  title+URL) — NOT written into `data/sources.json` (single-writer rule). The main agent promotes them after adjudication.
- **Quality gate G2:**
  - [ ] ≥ 90% of claims reviewed (each with a verdict)
  - [ ] Every review has an explicit attack or a stated "no counter-evidence found after search"
  - [ ] At least 1 severe-risk / falsification finding surfaced (even if all claims survive)
  - [ ] No review rewrites a claim — reviews only reference `claim_id`
  - **Fail →** one revise round (deep tier: + one forced new-factors round, anti-groupthink).

### S6 — Editorial Adjudication 主编仲裁
- **Who:** main agent. **Never delegated.**
- **Input:** all artifacts from S4+S5.
- **Output:** `decisions/decision.json`:
  - per-claim verdicts `accept | refute | qualify | unverified` + `editor_note`
  - **mandatory `minority_report`** — at least one dissenting view kept (consensus can be a shared error)
  - `report_skeleton`: ordered sections, each mapped to claims + chart ids + data files
  - `open_questions`: data gaps, unresolved conflicts, things that must be flagged in the report
  - promoted sources: counter-evidence the Red Team brought that passed scrutiny → appended to `data/sources.json`
    (main-agent write — the only exception to the Data-Engineer single-writer rule, done at adjudication time)
- **Quality gate G3:**
  - [ ] Every claim in `claims_*.json` has a verdict (no orphans)
  - [ ] `minority_report` non-empty
  - [ ] `report_skeleton` maps every planned section to artifacts
  - [ ] Red-flag scan (methodology red-flag checklist) performed on the surviving thesis: no unresolvable red flag remains unaddressed
  - [ ] Verdicts never cite a source that doesn't exist in `sources.json`
  - **Fail →** bounded fix loop (max = depth-tier rounds).

### S7 — Charting 图表
- **Who:** 1 leaf child (Chart Specialist). *`quick` tier: skipped — no figures.*
- **Input:** `decisions/decision.json` (skeleton + approved claims), `data/*`, chart scripts `scripts/charts/`.
- **Output:** `charts/manifest.json` (figure plan: id, type, title, data_ref, source, caption, caveat) + `charts/fig_*.png`.
- **Chart plan is written by the main agent into the brief** (S3) so the child does not decide scope itself:
  `standard` ≥ 3 core figures (price history + performance, revenue/earnings trajectory, valuation scenario fan);
  `deep` = full set.
- **Quality gate G4:**
  - [ ] Every planned figure exists; every figure is in `manifest.json`
  - [ ] Each figure has `data_ref` pointing at a file in `data/` and a human-readable source line
  - [ ] No figure contradicts an accepted claim or a verdict in `decision.json`
  - [ ] Axes/labels in report language; captions include caveats (e.g. "consensus as of YYYY-MM-DD")
  - **Fail →** re-dispatch once with the specific missing figure ids; else drop figure with a "figure unavailable — data gap" placeholder (recorded in manifest).

### S8 — Layout & Assembly 排版
- **Who:** 1 leaf child (Layout Specialist).
- **Input:** `decisions/decision.json` (skeleton + verdicts), `research/*`, `review/redteam.md` (risk section), `charts/manifest.json` + figures, layout script `templates/md_to_docx.py`.
- **Output:** `draft/report_draft.md` following the report structure
  (Exec Summary → stance → thesis → evidence chain → counter-arguments → scenarios & probabilities → risks & exits → review hooks),
  with every core number carrying a citation `[S001]` and every figure referenced by id.
- **Quality gate G5:**
  - [ ] All skeleton sections present, in order
  - [ ] Every accepted claim appears in the draft; refuted claims do not resurface as fact
  - [ ] Every core number has a citation; citation ids resolve in `sources.json`
  - [ ] All planned figures referenced; language matches envelope
  - [ ] Mechanical quality: no duplicated sections, no empty placeholders, heading hierarchy sane
  - **Fail →** one bounded fix round (narrow: "fix sections X,Y").

### S9 — Final Review & Delivery 终审与成稿
- **Who:** main agent.
- **Input:** `draft/report_draft.md` + all artifacts.
- **Output:** `final/report.md` (+ `report.docx`/`report.pdf` via `templates/md_to_docx.py` if available), `final/summary.md` (or inline delivery message).
- **Quality gate G6 — final checklist** (each must pass):
  - [ ] Conclusion is falsifiable and states "what would overturn it"
  - [ ] Every core number has source + definition (denominator/date/scope); no bare "consensus" without provider/date
  - [ ] TAM→share→timing→margin bridge complete where TAM appears (never TAM-as-revenue)
  - [ ] Scenarios carry probabilities — not a single optimistic path
  - [ ] Counter-arguments handled head-on, not avoided
  - [ ] Forecasts carry falsification conditions + exit plan; direction and speed separated
  - [ ] Data gaps from `open_questions` are disclosed in the report (not hidden)
  - [ ] Report language matches envelope; non-English sources cited in their original language with `[S###]`
  - [ ] `final/report.md` exists and is non-empty; delivery message summarizes: thesis, key numbers, risks, open questions, and where artifacts live
- **Fail →** main agent fixes mechanical issues directly or dispatches one narrow layout fix; content-level failures go back to the affected stage (bounded by depth-tier rounds).

### S10 — Proofing & QC 校对质检（视觉校对质量门）

- **Who:** main agent (主编) — never delegated to a leaf child. *Proofreader 校对员 is an optional assistant role (brief in `agent_prompts.md`); the main agent drives the gate either way.*
- **Input:** `final/report.md` (+ `report.docx`/`report.pdf` if converted), `data/numbers.json` (数字引用表), `charts/manifest.json` + figures.
- **Output:** `proof/` directory:
  - `proof/visual_proofing.md` — per-page visual checklist (page × check item × PASS/FAIL), see below.
  - `proof/pages/page_*.png` — PDF rendered page by page (pymupdf: `python -c "import pymupdf; ... get_pixmap(dpi=144) ..."`; any renderer a vision-capable model can read works).
- **Steps:**
  1. **Render.** Render `final/report.pdf` (or the docx) page by page to `proof/pages/page_NN.png`. **Re-render after ANY change to the artifacts — a stale render passes a false gate** (an old PNG can look clean while the current PDF is broken). **Trust freshness, not the exporter:** Word/COM PDF export can fail silently and leave an OLD pdf in place — verify `PDF mtime ≥ docx mtime` before rendering (`templates/md_to_docx.py` now retries and refuses to report success on a stale file). **Render at ≥144 DPI:** thin serif strokes, dark table headers on white text and pale zebra fills are unreadable below that and generate false findings.
  2. **Vision proofing — this IS the gate.** **A model with VISION input must inspect every page** against the checklist below — judgment on layout from text alone is FORBIDDEN (agent-agnostic: any vision-capable model, multimodal CLI, or a human reviewer passes; a text-only model must pass the PNGs to one). The vision reviewer holds `data/numbers.json` (数字引用表) as the cross-check reference and verifies every core number printed on a page against its registered value. Record a per-page table: 页号 × 检查项 × PASS/FAIL in `proof/visual_proofing.md`. **Any page FAIL → back to S8 (Layout Specialist) to re-typeset, then re-render and re-proof.**
  3. **Zoom before you judge (疑点先放大复核).** Any suspected defect on a page must be re-checked on a ≥2x cropped zoom before it is recorded. At thumbnail resolution a black header with white text reads as "white background", a pale zebra fill reads as "missing", and `Fiscal` reads as `Fical` — three false findings in one pass on this project. Record only what survives the zoom.
  3. **Proofreading pass (reading, still no content edits):** citations resolve, language consistency, no duplicated sections, no orphaned captions/headings.
- **Quality gate G7 — 视觉校对单 (all items must PASS):**
  - [ ] every page inspected by a vision-capable model; cover rating box (评级框) / analyst block (分析师块) / key-data price block rendered
  - [ ] no text overlap, no element overflow beyond margins, no clipping, no misalignment, no image exceeding page width, no detached captions, no blank pages, no orphaned headings
  - [ ] tables split only with a repeated header row; header/footer present with "Page X of Y"; Chinese glyphs render (CJK-capable face when language=zh)
  - [ ] every core number on the pages matches the 数字引用表 — **数字未登记引用表 = 违规范 (unregistered or mismatched core number = FAIL)**
  - [ ] 无 {{PLACEHOLDER}} 残留 (visible in report md + docx/PDF)
  - [ ] Any FAIL → documented reason + stage the fix returns to; gate re-opened until all PASS
- **Fail →** one bounded fix round (fixes return to S8 with the specific page + item). Never publish on a red gate; publish only after **G7 all green**.

---

## 9. Orchestration Mechanics / 编排机制

### 9.1 Dispatch protocol (tool-agnostic)

For every child, the main agent sends **one self-contained brief** containing:

1. **Role + lens** (one line) and **mission**.
2. **RUN_ROOT** (absolute) and **envelope JSON** (inline — not just a path).
3. **Inputs** (read paths) and **Outputs** (the only write paths).
4. **Steps**, **evidence rules**, **quality checklist**, **language**, **budget**.

```
TO:   <child role name> (leaf worker)
FROM: main agent
SUBJECT: <run_id> — <role>

<the filled brief text — nothing above this line is visible to the child>
```

Dispatch order:

```
S0  main agent intake: template + focus questionnaire → brief/intake.json → G0 check
S2  main agent writes envelope.json (intake values wired in) → G0c
S3  main agent writes briefs (intake answers injected) → G0d
W1  start Data Engineer + Industry Analyst + Valuation Analyst (one batch, or sequential fallback)
    → wait for all → G1 check → optional narrow revise
W2  start Red Team (skip if depth=quick) → wait → G2 check
S6  main agent adjudicates inline (NO child)
W3  start Chart Specialist (skip if depth=quick) → wait → G4 check
W4  start Layout Specialist → wait → G5 check
S9  main agent final QA (G6) → publish final/
S10  main agent Proofing & QC: render pages → vision proofing (per-page checklist) → G7
    → if G7 red: dispatch narrow fix (back to S8 typically) → re-render + re-proof → publish
```

### 9.2 Rules that keep the pipeline honest

1. **Context completeness:** children start with fresh context — pass brief + envelope JSON + absolute RUN_ROOT inside
   the brief text. Never rely on a child "seeing the conversation".
2. **One batch per wave:** if your runtime supports it, start all 3 research children in a single dispatch batch.
   Splitting into multiple staggered calls risks partial-run state and wasted tokens.
3. **Leaf-only children:** children never spawn further agents. Prevents runaway cost. If a child "needs to spawn",
   that's a design error — split the role instead.
4. **Bounded retries:** revise rounds capped by depth tier (quick 0, standard 1, deep 2). After that: **degrade, don't loop** —
   record the gap in `open_questions` and deliver with disclosure.
5. **Degradation ladder:** missing data → assumptions flagged `type=assumption`; missing figure → placeholder caption;
   failed child (empty/error) → one narrow re-dispatch; still failing → proceed without that artifact, disclose.
6. **Freshness discipline (cache metadata):** every `data/` file records `fetched_at` + `freshness_tier`
   (行情/price ≤ 1 day; 财报/filings ≤ 7 days; 政策/policy — re-check at run time; 结构/structural ≤ 30 days).
   Analyst briefs say: "if data is stale per its tier, say so in the report — do not silently reuse."
7. **Cost awareness:** every child consumes tokens independently. Budgets in the envelope are per-depth; the main agent
   should tighten `max_sources_per_claim`/`max_claims_per_analyst` for long ticker lists.

---

## 10. Artifact Schemas / 结构化工件

All JSON artifacts validate against these shapes (the shapes below are the normative ones; `direction_confirmed.json`
has a runnable validator — `scripts/intake/direction_check.py --check`).

### intake (IntakeArtifact) — written by the main agent at S0 (from user answers)

```json
{
  "template_id": "goldman_hardline",
  "template_display_name": "高盛（硬朗风） / Hardline",
  "focus_areas": ["valuation", "growth"],
  "horizon": "medium",
  "depth": "deep",
  "language": "en",
  "chart_density": "high",
  "special_requests": ["focus on FCF inflection and buyback capacity"],
  "created_at": "2026-09-10T05:23:30+08:00"
}
```
- Produced by `scripts/intake/intake.py` or hand-written per [`intake.md`](intake.md); copied into
  `{RUN_ROOT}/briefs/intake.json` at S2; consumed by every later stage per the injection table.

### direction_confirmed (DirectionArtifact) — written by the main agent at S1 (from user answers)

```json
{
  "ticker": "688836.SH",
  "as_of": "2026-09-10",
  "view": "fundamental",
  "primary_driver": "humanoid shipment volume × realised ASP",
  "driver_tags": [
    {"driver": "shipment volume × ASP", "tag": "direct", "proxy": "quarterly shipment + disclosed ASP"},
    {"driver": "state robotics subsidies", "tag": "theme", "proxy": "policy document number + date"}
  ],
  "assumption_anchor": "consensus",
  "assumption_note": "use the consensus revenue band; no user override",
  "competitive_set": ["dedicated humanoid peers", "industrial robot incumbents"],
  "falsification": "two consecutive quarters with shipment volume below the level implied by the base case",
  "output_orientation": {"orientation": "valuation-driven", "emphasis": ["growth", "risk"]},
  "answers": [
    {"q": "Q1", "field": "view", "answer": "fundamental", "answered_by": "user", "note": ""},
    {"q": "Q2", "field": "primary_driver", "answer": "shipment volume × ASP", "answered_by": "user", "note": "user reordered the driver list"},
    {"q": "Q3", "field": "assumption_anchor", "answer": "consensus", "answered_by": "user-delegated", "note": "user said \"you pick, just label it\""},
    {"q": "Q4", "field": "competitive_set", "answer": ["dedicated humanoid peers"], "answered_by": "user", "note": ""},
    {"q": "Q5", "field": "falsification", "answer": "two quarters below base-case shipments", "answered_by": "user", "note": ""},
    {"q": "Q6", "field": "output_orientation", "answer": {"orientation": "valuation-driven", "emphasis": ["growth"]}, "answered_by": "user", "note": ""}
  ],
  "direction_assumed": false,
  "created_at": "2026-09-10T06:10:00+08:00"
}
```
- Validated by `python scripts/intake/direction_check.py --check brief/direction_confirmed.json` — gate **G0b**.
  `--skeleton` prints an empty template with the six questions.
- `answers[]` must carry one entry per question (Q1–Q6) with `answered_by ∈ {user, user-delegated}` and a non-empty
  answer. A default filled in by the agent with `answered_by: "agent-default"` **fails G0b**.
- `direction_assumed: true` is legal only when the user was unreachable and the run had to proceed; every assumed value
  must then appear on the report's cover note and in the delivery summary.

### industry_logic.md (prose artifact, S1) — the logic map

Required blocks, in order: ① revenue mix (segment/product/geography shares, or an explicit "no revenue yet" + the metric
that would confirm the business) ② chain position + who holds pricing power at each link ③ driver table with a
`direct|theme` tag and the observable proxy per driver ④ transmission chain, one proxy per hop or `unverifiable`
⑤ cycle phase + the company's relative position. Copied into `{RUN_ROOT}/briefs/` at S2; consumed by the S4 role briefs
(the Industry and Valuation analysts must answer it, the Red Team attacks it).

### claim (ClaimArtifact) — written by analysts

```json
{
  "id": "IND-001",
  "author": "industry",
  "type": "fact | reported-metric | guidance | forecast | assumption | interpretation | opinion | market-pricing | derived-calculation",
  "statement": "Company X's gross margin recovered to 22.4% in FY2025.",
  "confidence": 0.8,
  "evidence_refs": ["S001", "S002"],
  "counterarguments": ["Margin recovery partly driven by one-off inventory gains."],
  "falsification_condition": "Q1 next FY gross margin < 20% would overturn this.",
  "created_at": "2026-09-10T01:30:00+08:00"
}
```
- `counterarguments` required for interpretive/forecast claims; optional for pure facts.
- `evidence_refs` must resolve in `data/sources.json` (main agent enforces at G1/G3).

### review (ReviewArtifact) — written by Red Team

```json
{
  "review_id": "RV-012",
  "target_claim": "IND-001",
  "verdict": "support | refute | qualify | unverified",
  "attack": "The recovery is concentrated in one quarter; run-rate basis shows no improvement.",
  "counter_evidence_refs": [{"title": "...", "url": "...", "note": "promote to sources.json if accepted"}],
  "severity": "high | medium | low",
  "suggested_revision": "Qualify the claim to 'one-off assisted recovery'."
}
```

### decision (DecisionArtifact) — written by main agent

```json
{
  "run_id": "ws_...",
  "decisions": [
    {"claim_id": "IND-001", "verdict": "qualify", "editor_note": "...", "final_confidence": 0.6}
  ],
  "minority_report": "Dissenting view kept: ...",
  "report_skeleton": [{"section": "3. Business & Competition", "claims": ["IND-001"], "charts": ["fig2"], "data": ["data/fundamentals.json"]}],
  "open_questions": ["FY2025 segment split not disclosed; assumption flagged."],
  "promoted_sources": ["S014"],
  "created_at": "..."
}
```

### charts/manifest.json — written by Chart Specialist

```json
{
  "figures": [
    {"id": "fig1", "title": "Price & volume, 24M", "type": "line", "data_ref": "data/price_history.csv",
     "source": "S003", "caption": "...", "caveat": "...", "file": "charts/fig1.png"}
  ]
}
```

---

## 11. Dedup & Shared-Knowledge Rules / 去重与共享知识

1. **Single-writer data:** `data/` is written only by the Data Engineer (one exception: the main agent promotes accepted
   counter-evidence into `sources.json` at S6). Analysts **read**, never fetch-and-write — no duplicate scraping.
2. **Own-file rule:** each role writes only its own output files; cross-references use ids (`claim_id`, `S###`), never file edits.
3. **One source registry:** `data/sources.json` is the only citation namespace. A source fetched twice = one record.
   Same-day same-source different content gets a suffix (`S001a`) — never overwrite silently.
4. **Conflict handling:** conflicting facts between analysts are recorded as claims with `counterarguments`; the main agent
   adjudicates explicitly. No silent merging.
5. **Knowledge reuse across runs:** the repo may keep an optional `methodology/run_knowledge.md` where the main agent
   appends durable facts + reusable data-fetch recipes after each run (opt-in; keeps the skill self-improving).
6. **Fixed budget per run:** rounds/claims/sources are bounded in the envelope — no unbounded loops.

---

## 12. Depth Tiers / 深度档位

| | `quick` | `standard` | `deep` |
|---|---|---|---|
| Stages | S0, S1, S2, S3, S4, S6, S8, S9, S10 (vision proofing; cover + first page spot-check) | S0–S10 | S0–S10 |
| Red team | main-agent inline red-flag scan | 1 child round | 2 rounds (2nd round forces **new factors** — anti-groupthink) |
| Charts | none | ≥ 3 core figures | full figure set |
| Revise rounds | 0 | 1 per gate | 2 per gate |
| Claims/analyst | ≤ 12 | ≤ 25 | ≤ 40 |
| Sources/claim | ≤ 3 | ≤ 5 | ≤ 8 |
| Scenarios | base only (single thesis) | base/bull/bear | base/bull/bear + sensitivity matrix |
| Approx. time | 10–20 min | 45–75 min | 2–4 h |
| Use case | screening, quick sanity | standard research note | deep-dive / portfolio-grade |

**S0 intake may override the tier and the figure count:** `brief/intake.json.depth` is authoritative for stage
trimming, and `chart_density` sets the figure plan inside the tier (`low` 1–2, `standard` 3–5, `high` full set).
The envelope records both; a change mid-run must update `brief/intake.json` and be disclosed.

---

## 13. Main-Agent Operating Protocol / 主代理操作规程

0. **S0.** Ask the template + focus questions per [`intake.md`](intake.md); write `brief/intake.json`;
   validate **G0**. Never delegate this stage.
1. **S1.** Map the industry logic (**five moves**) and put the **5–6 direction questions** to the user per
   [`logic_mapping.md`](logic_mapping.md); write `brief/industry_logic.md` + `brief/direction_confirmed.json`;
   validate **G0b**. Never delegate this stage, and never answer the direction questions on the user's behalf.
2. **Parse input → S2.** Build `envelope.json` (wire in intake values); create run dirs; copy the intake file
   **and the two S1 artifacts** into `briefs/`. Validate **G0c**.
3. **S3.** Fill all 6 role briefs from templates (`agent_prompts.md`) — inject the intake answers (lens
   weights, horizon, language, chart density, special requests) **and the S1 direction answers (primary driver,
   view, assumption anchor, competitive set, falsification condition, output orientation)**; resolve `{{...}}`;
   write `briefs/`. Validate **G0d**.
4. **S4.** Dispatch 3 research children (one batch, or sequential). On return, run G1. If a role failed → one narrow
   re-dispatch ("complete items X only"). Degrade if needed.
5. **S5.** If depth ≠ quick: dispatch Red Team. Run G2.
6. **S6.** Adjudicate **inline**: read all claims → verdict each → write `minority_report` → build `report_skeleton` →
   promote accepted counter-evidence sources → record `open_questions`. Run G3.
7. **S7.** If depth ≠ quick: write the figure plan into the chart brief, dispatch Chart Specialist. Run G4.
8. **S8.** Dispatch Layout Specialist with skeleton + chart manifest. Run G5.
9. **S9.** Final checklist (G6) → publish `final/` → run S10 → deliver summary (thesis, key numbers, risks,
   open questions, artifact paths). Optionally append durable facts to `run_knowledge.md`.
10. **S10.** Proofing & QC: (1) render `proof/pages/page_*.png` from the PDF. (2) Have a **vision-capable
   model** inspect every page on the G7 visual checklist — layout is never judged from text alone — and
   verify every core number against `numbers.json` (数字引用表), recording `proof/visual_proofing.md`.
   **Gate G7** (all green) before delivery; any red → narrow fix (usually back to S8) → re-render and re-proof.

**Main-agent discipline (never violated):**
- S0 答案（模板/侧重/期限/深度/语言/图表密度）一经确认即注入全链，不得中途静默更改；变更须更新 `brief/intake.json` 并披露。
- S1 的方向答案归用户，不归主代理：五到六问必须真的问出去；用户答"你定"时给推荐值并请其确认（记 `answered_by: "user-delegated"`），
  不得静默套默认值；确实无法取得答案又必须开跑时，置 `direction_assumed: true` 并在报告封面逐条列出假设。
- `theme` 级驱动不得写成公司收入驱动；传导链缺可观测代理的那一跳必须标 `unverifiable`（宁可写"未证实"，不许断言）。
- 主代理绝不凭整体印象裁决——先读齐所有 artifacts，逐 claim 裁决。
- 强制保留 minority report（共识也可能是共同错误）。
- 不无限加轮次：预算在 envelope，超预算即降级交付并披露。
- 不伪造证据：找不到的数据写进 open_questions，不猜数。

---

## 14. Portability & Installation / 可移植性与安装

**The pipeline is agent-agnostic and self-contained.**

- **No platform hooks:** no `delegate_task`, no skill mechanism, no vendor CLI, no MCP servers, no proprietary APIs.
  Execution is: copy briefs → children read/write files → run stdlib-Python scripts for mechanical work.
- **Mechanical work = Python stdlib (cross-platform):**
  - `scripts/intake/intake.py` — S0 intake (`--list` templates; write `brief/intake.json`; no third-party deps).
  - `scripts/intake/direction_check.py` — S1 direction contract (`--skeleton` template; `--check` validates the six
    answers and the driver/proxy rules → gate G0b; no third-party deps).
  - `scripts/data/data_fetcher.py` — unified data acquisition (quotes/history/financials for US & CN; `--json` for structured output).
  - `scripts/charts/report_charts.py` — render research-style figures (kline / PE band / financials / scenario / peer comparison → PNG).
  - `templates/md_to_docx.py` — assemble the Markdown master → Word `.docx` (and PDF via `--pdf`, requires MS Word + docx2pdf).
  - Any agent with code execution (or any human with a shell) can run them; the pipeline works even without them
    (agents or humans fetch and save files directly, and mark sources).
- **No machine-specific paths anywhere:** briefs contain only `RUN_ROOT`-relative conventions
  (`runs/{run_id}/...`); `RUN_ROOT` is injected at runtime.
- **Installation for a clone:**
  1. This repo already ships `pipeline/` (intake + industry-logic mapping + orchestration + briefs), `scripts/` (intake/data/charts) and `templates/` (layout + styles) — keep the tree intact; all internal references are relative.
  2. `SKILL.md` frontmatter references them; the skill body's "Run pipeline" section points at this design doc.
  3. Optional: give your main agent the 3 child-brief files and this doc — nothing else to configure.
- **Language:** reports default to English; `language=zh|bilingual` switches the layout language and brief language
  (templates ship bilingual). Sources remain in their native language with `[S###]` citations.

**Out of scope for this design (other workstreams):** actual data-provider code (`scripts/data/`), chart library
(`scripts/charts/`), layout engine (`templates/md_to_docx.py`), methodology references, sample reports, GitHub packaging.
