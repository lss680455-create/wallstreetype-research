# Wall Street Research — Multi-Agent Pipeline Orchestration Design

> Part of the **Wall Street Research** skill (portfolio piece + open-source).
> This document defines **how the report pipeline is orchestrated with parallel child agents**.
> Data / charts / layout / methodology modules are built by other workstreams; this doc only defines
> how the pipeline calls them and the **file handoff conventions** between stages.
> 本文只定义编排：数据/图表/排版/范式模块由其他子代理实现，本流水线通过约定文件路径调用它们。

- Version: 2.0.0
- Status: design
- Companion file: [`agent_prompts.md`](agent_prompts.md) — copy-paste-ready bilingual briefs for every role.
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

The pipeline is a **workflow**, not a program. You drive it in four moves:

1. **Prepare.** Create a run directory; write `envelope.json` (the input contract, §4) and the six role briefs
   (§ in `agent_prompts.md`) with placeholders filled in.
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
 main agent ── S1 envelope ── S2 briefs ──┬── [child] Data Engineer   ─┐
                                          ├── [child] Industry Analyst ─┼── parallel (or sequential) ── S5 main-agent adjudication
                                          └── [child] Valuation Analyst┘        │
                                   S4 [child] Red Team ────────────────────────┘
                                   S6 [child] Chart Specialist ─ S7 [child] Layout Specialist ─ S8 main-agent final QA & delivery
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
{workspace}/runs/{run_id}/            # RUN_ROOT (created by main agent at S1)
├── envelope.json                     # task contract (input)
├── briefs/                           # master brief + per-role briefs (audit trail)
│   ├── master_brief.md
│   └── brief_<role>.md               # data_engineer | industry | valuation | redteam | chart | layout
├── data/                             # SINGLE WRITER: Data Engineer
│   ├── manifest.json                 # inventory of fetched data (id, path, fetched_at, freshness_tier)
│   ├── sources.json                  # source registry (S001, S002, ...) — single source of truth for citations
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
└── final/                            # SINGLE WRITER: main agent
    ├── report.md
    └── report.docx / report.pdf      # via templates/md_to_docx.py, if present
```

**Handoff contract for the modules (charts / layout / data):**

| Module | Invoked by | Reads | Writes |
|---|---|---|---|
| Data module (`scripts/data/`) | Data Engineer at S3 | — | `data/*` (convention above) |
| Chart module (`scripts/charts/`) | Chart Specialist at S6 | `data/*`, `charts/manifest.json` plan | `charts/fig_*.png` |
| Layout module (`templates/`) | Layout Specialist at S7 | `decisions/decision.json`, `research/*`, `review/*`, `charts/*` | `draft/report_draft.md`, `final/report.*` |
| Methodology (repo `skill/references/`, `wall-street-research-methodology`) | all roles, esp. main agent at S5/S8 | — | — |

**Cross-writing rule (non-negotiable):** a role may write **only** its own output files listed in its brief. Nobody
writes into another role's directory. Data is single-writer (`data/`); the source registry (`data/sources.json`) is
appended to only by the Data Engineer; new sources discovered by other roles are recorded in their own artifact and
**promoted by the main agent after adjudication** (S5).

---

## 5. Input Contract — TaskEnvelope / 输入契约

`envelope.json` is the single input artifact; every brief references it.

```json
{
  "run_id": "ws_20260910_ab12",
  "ticker": "TSLA",
  "company": "Tesla, Inc.",
  "market": "US",
  "language": "en",
  "depth": "standard",
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
| `depth` | yes | `quick` / `standard` / `deep` — see §11 |
| `focus_question` | no | optional single question the report must answer |
| `budget` | yes | filled from depth-tier defaults; the main agent may tighten for cost control |

---

## 6. Role Roster & Lens Boundaries / 角色与透镜边界

**7 roles. Lenses are disjoint — each role owns exactly one layer and must NOT cross into another's.**

| # | Role | Lens (one line) | Owns | Explicitly NOT allowed |
|---|---|---|---|---|
| 1 | **Data Engineer** 数据工程师 | **Facts & numbers**: what the numbers *are* | acquisition, freshness, source grading, dedup, manifest | interpretation, opinions, valuation, thesis writing |
| 2 | **Industry Analyst** 行业分析师 | **Business & competition**: why the business works or fails | industry structure, moat, demand/supply drivers, regulation | fetching new raw data (uses `data/`), target prices, modeling |
| 3 | **Valuation Analyst** 估值分析师 | **Price & expectations**: what the business is *worth*, what's priced in | financial model, base/bull/bear scenarios, target range, catalysts, risk-adjusted return | re-litigating industry facts, raw data fetching |
| 4 | **Red Team** 质询官 | **Counter-evidence & falsification**: what could be *wrong* | attacks on every claim, stress tests, red flags, falsification conditions | producing new positive claims; writing to `data/` or `research/` |
| 5 | **Main Agent / Editor-in-Chief** 主编（主代理，不委派） | **Synthesis & adjudication**: what the report will *conclude* | briefs, per-claim verdicts, minority report, report skeleton, quality gates, final delivery | fabricating evidence; delegating the adjudication itself |
| 6 | **Chart Specialist** 图表师 | **Visual evidence**: figures that make claims legible | figure selection, data→chart mapping, annotations | new analysis, changing numbers, writing claims |
| 7 | **Layout Specialist** 排版师 | **Structure & readability**: a report a human can actually read | assembly, section order, typography, citations formatting, format conversion | content edits beyond mechanical fixes, new opinions |

Roles 1–4 and 6–7 are **leaf child agents**. The main agent (Editor, role 5) is the only orchestrator and adjudicator.

---

## 7. Pipeline Overview / 流水线总览

```
 S1  Input & Envelope        ─ main agent                → envelope.json, run dir
 S2  Master Brief            ─ main agent                → briefs/*.md
 S3  Parallel Research       ─ 3 leaf children, one batch→ data/*, research/*, claims_*.json
 S4  Red Team Challenge      ─ 1 leaf child              → review/redteam.md, reviews.json
 S5  Editorial Adjudication  ─ main agent                → decisions/decision.json
 S6  Charting                ─ 1 leaf child              → charts/manifest.json, fig_*.png
 S7  Layout & Assembly       ─ 1 leaf child              → draft/report_draft.md
 S8  Final Review & Delivery ─ main agent                → final/report.*, run summary
```

**8 stages, up to 4 dispatch waves** (all other work is done by the main agent):

| Wave | Stage(s) | Dispatch | Parallelism |
|---|---|---|---|
| W1 | S3 | start 3 children in one batch (Data Engineer, Industry, Valuation) | 3 children (fallback: sequential) |
| W2 | S4 | start 1 child (skip in `quick` tier) | 1 child |
| W3 | S6 | start 1 child (skip in `quick` tier) | 1 child |
| W4 | S7 | start 1 child | 1 child |

Max concurrent children needed: **3**. If a runtime caps concurrency below 3, run the research roles sequentially —
the workflow is unaffected.

---

## 8. Stage Specifications / 阶段规格

### S1 — Input & Envelope 输入与任务信封
- **Who:** main agent.
- **Input:** user request (ticker/market/language/depth/focus) — parsed, defaults applied (`language=en`, `depth=standard`).
- **Output:** `{RUN_ROOT}/envelope.json`; creates `{RUN_ROOT}/` and subdirectories.
- **Quality gate G0:** envelope validates (required fields present; `depth ∈ {quick, standard, deep}`; `language ∈ {en, zh, bilingual}`; budget fields filled).

### S2 — Master Brief 简报
- **Who:** main agent.
- **Input:** `envelope.json`; brief templates from this repo (`agent_prompts.md`).
- **Output:** `briefs/master_brief.md` + `briefs/brief_<role>.md` for all 6 child roles — every placeholder
  (`{{run_root}}`, `{{ticker}}`, ...) resolved to concrete values.
- **Quality gate G0b:** every role brief exists and contains: role + lens, input paths, output path, quality checklist,
  budget/rounds, language. A brief missing its checklist is a defect — fix before dispatching.

### S3 — Parallel Research 并行研究
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

### S4 — Red Team Challenge 红队质询
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

### S5 — Editorial Adjudication 主编仲裁
- **Who:** main agent. **Never delegated.**
- **Input:** all artifacts from S3+S4.
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

### S6 — Charting 图表
- **Who:** 1 leaf child (Chart Specialist). *`quick` tier: skipped — no figures.*
- **Input:** `decisions/decision.json` (skeleton + approved claims), `data/*`, chart scripts `scripts/charts/`.
- **Output:** `charts/manifest.json` (figure plan: id, type, title, data_ref, source, caption, caveat) + `charts/fig_*.png`.
- **Chart plan is written by the main agent into the brief** (S2) so the child does not decide scope itself:
  `standard` ≥ 3 core figures (price history + performance, revenue/earnings trajectory, valuation scenario fan);
  `deep` = full set.
- **Quality gate G4:**
  - [ ] Every planned figure exists; every figure is in `manifest.json`
  - [ ] Each figure has `data_ref` pointing at a file in `data/` and a human-readable source line
  - [ ] No figure contradicts an accepted claim or a verdict in `decision.json`
  - [ ] Axes/labels in report language; captions include caveats (e.g. "consensus as of YYYY-MM-DD")
  - **Fail →** re-dispatch once with the specific missing figure ids; else drop figure with a "figure unavailable — data gap" placeholder (recorded in manifest).

### S7 — Layout & Assembly 排版
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

### S8 — Final Review & Delivery 终审与成稿
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
W1  start Data Engineer + Industry Analyst + Valuation Analyst (one batch, or sequential fallback)
    → wait for all → G1 check → optional narrow revise
W2  start Red Team (skip if depth=quick) → wait → G2 check
S5  main agent adjudicates inline (NO child)
W3  start Chart Specialist (skip if depth=quick) → wait → G4 check
W4  start Layout Specialist → wait → G5 check
S8  main agent final QA → publish → deliver
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

All JSON artifacts validate against these shapes (JSON Schema files ship with the repo under `skill/schemas/`).

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
   counter-evidence into `sources.json` at S5). Analysts **read**, never fetch-and-write — no duplicate scraping.
2. **Own-file rule:** each role writes only its own output files; cross-references use ids (`claim_id`, `S###`), never file edits.
3. **One source registry:** `data/sources.json` is the only citation namespace. A source fetched twice = one record.
   Same-day same-source different content gets a suffix (`S001a`) — never overwrite silently.
4. **Conflict handling:** conflicting facts between analysts are recorded as claims with `counterarguments`; the main agent
   adjudicates explicitly. No silent merging.
5. **Knowledge reuse across runs:** the repo may keep an optional `skill/references/run_knowledge.md` where the main agent
   appends durable facts + reusable data-fetch recipes after each run (opt-in; keeps the skill self-improving).
6. **Fixed budget per run:** rounds/claims/sources are bounded in the envelope — no unbounded loops.

---

## 12. Depth Tiers / 深度档位

| | `quick` | `standard` | `deep` |
|---|---|---|---|
| Stages | S1, S2, S3, S5, S7, S8 | S1–S8 | S1–S8 |
| Red team | main-agent inline red-flag scan | 1 child round | 2 rounds (2nd round forces **new factors** — anti-groupthink) |
| Charts | none | ≥ 3 core figures | full figure set |
| Revise rounds | 0 | 1 per gate | 2 per gate |
| Claims/analyst | ≤ 12 | ≤ 25 | ≤ 40 |
| Sources/claim | ≤ 3 | ≤ 5 | ≤ 8 |
| Scenarios | base only (single thesis) | base/bull/bear | base/bull/bear + sensitivity matrix |
| Approx. time | 10–20 min | 45–75 min | 2–4 h |
| Use case | screening, quick sanity | standard research note | deep-dive / portfolio-grade |

---

## 13. Main-Agent Operating Protocol / 主代理操作规程

1. **Parse input → S1.** Build `envelope.json`; create run dirs. Validate G0.
2. **S2.** Fill all 6 role briefs from templates (`agent_prompts.md`); resolve `{{...}}`; write `briefs/`. Validate G0b.
3. **S3.** Dispatch 3 research children (one batch, or sequential). On return, run G1. If a role failed → one narrow
   re-dispatch ("complete items X only"). Degrade if needed.
4. **S4.** If depth ≠ quick: dispatch Red Team. Run G2.
5. **S5.** Adjudicate **inline**: read all claims → verdict each → write `minority_report` → build `report_skeleton` →
   promote accepted counter-evidence sources → record `open_questions`. Run G3.
6. **S6.** If depth ≠ quick: write the figure plan into the chart brief, dispatch Chart Specialist. Run G4.
7. **S7.** Dispatch Layout Specialist with skeleton + chart manifest. Run G5.
8. **S8.** Final checklist (G6) → publish `final/` → deliver summary (thesis, key numbers, risks, open questions,
   artifact paths). Optionally append durable facts to `run_knowledge.md`.

**Main-agent discipline (never violated):**
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
  - `scripts/data/data_fetcher.py` — unified data acquisition (quotes/history/financials for US & CN; `--json` for structured output).
  - `scripts/charts/report_charts.py` — render research-style figures (kline / PE band / financials / scenario / peer comparison → PNG).
  - `templates/md_to_docx.py` — assemble the Markdown master → Word `.docx` (and PDF via `--pdf`, requires MS Word + docx2pdf).
  - Any agent with code execution (or any human with a shell) can run them; the pipeline works even without them
    (agents or humans fetch and save files directly, and mark sources).
- **No machine-specific paths anywhere:** briefs contain only `RUN_ROOT`-relative conventions
  (`runs/{run_id}/...`); `RUN_ROOT` is injected at runtime.
- **Installation for a clone:**
  1. This repo already ships `pipeline/` (orchestration + briefs), `scripts/` (data/charts) and `templates/` (layout) — keep the tree intact; all internal references are relative.
  2. `SKILL.md` frontmatter references them; the skill body's "Run pipeline" section points at this design doc.
  3. Optional: give your main agent the 3 child-brief files and this doc — nothing else to configure.
- **Language:** reports default to English; `language=zh|bilingual` switches the layout language and brief language
  (templates ship bilingual). Sources remain in their native language with `[S###]` citations.

**Out of scope for this design (other workstreams):** actual data-provider code (`scripts/data/`), chart library
(`scripts/charts/`), layout engine (`templates/md_to_docx.py`), methodology references, sample reports, GitHub packaging.
