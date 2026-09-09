# S0 — Intake: Template & Focus Questionnaire / 任务前意向采集

> **Pipeline stage: S0** — the first step of every run, immediately **before S1 (envelope)**.
> 流水线第 0 阶段：任何一次研报任务开始前的第一步，先于 S1（任务信封）。
>
> **Agent-agnostic / 代理无关:** any AI tool (Claude Code, Codex, Cursor, Hermes, a plain chat model) or a human
> can execute this stage by following the text below. No tool-specific syntax, no vendor hooks.
> 任何 AI 工具或人工都能照做；本文只有流程、问题与文件约定。

- Companion artifacts / 配套产物:
  - `scripts/intake/intake.py` — one-shot CLI that writes the artifact (stdlib only).
  - `templates/styles/` — the six layout templates (`*.json`) + `README.md` (catalogue & schema).
- Output / 产出: **`brief/intake.json`** (the intake contract consumed by S1 → S9).

---

## 1. When this runs / 触发时机

Run S0 at the start of **every new report task** — before fetching data, before writing any brief:

1. **Any new run.** The first pipeline action is intake, not envelope.
2. **The user has not chosen a layout template.** Ask (Step 1) — never silently pick one.
3. **The user has not stated the research focus.** Ask the questionnaire (Step 2).
4. **One intake per run.** Do not re-ask mid-run; if the user changes their mind, update
   `brief/intake.json` and note the change in `decision.json → open_questions`.
5. **User says "just go" / is unavailable.** Apply the documented defaults, **state them explicitly**
   in the reply and in `brief/intake.json`, and proceed. Never fabricate an answer the user did not give.

**中文：** 每次新任务开始时、用户未指定版式模板时、未说明研究侧重时，都必须先跑 S0。
每轮只问一次；用户不在场或说"直接开始"时，用本文默认值并在回复和 `brief/intake.json` 中明示，
不得替用户编造答案。

---

## 2. How to run it / 执行方式（三种，产物相同）

| Mode | Who | How |
|---|---|---|
| **A. Agent-driven**（推荐） | the agent | Read this file, ask the Step 1 + Step 2 questions in chat, echo the answers, then write `brief/intake.json` (hand-write it, or run the CLI in Mode B). |
| **B. CLI** | agent or human | `python scripts/intake/intake.py --template <id> --focus ... --horizon ... --depth ... --language ... --charts ... --notes "..."` |
| **C. Manual** | human | Copy the JSON skeleton in §4, fill it in, save as `brief/intake.json`. |

All three modes produce the **same artifact** — the pipeline only depends on the file, never on how it was made.
**中文：** 三种执行方式（代理对话式提问 / CLI 一次性写入 / 人工手写）产物完全一致，流水线只认文件。

---

## 3. Step 1 — Choose the layout template / 第一步：选择报告版式模板

Present this table (or run `python scripts/intake/intake.py --list`), then ask the user to pick one.

| # | id | Display name / 显示名 | Style in one line / 风格一句话 | Best for / 适用场景 |
|---|---|---|---|---|
| 1 | `goldman_hardline` | 高盛（硬朗风） / Hardline | Open grid, serif masthead, navy accents, hairline rules, high density — 开放式无框版式；衬线大标题+无衬线正文；深蓝强调；细线分区；高信息密度 | 机构级深度报告、数据密集型；想显得"硬核专业" |
| 2 | `morganstanley_restrained` | 摩根士丹利（克制风） / Restrained | Airy single column, light masthead, one blue accent, wide margins — 大留白单栏；轻字重大标题；单一蓝点缀；宽边距 | 论点驱动、叙事型长文；读者体验优先 |
| 3 | `jpmorgan_heavyset` | 摩根大通（厚重风） / Heavyset | Dense two-column, bold sans headers over serif body, slate-blue — 高密度双栏；粗无衬线标题+衬线正文；灰蓝；紧凑行距 | 信息量最大的全链条报告；附录/表格多 |
| 4 | `barclays_cyanline` | 巴克莱（青蓝风） / Cyan Line | Cyan header band, tinted side rail, cyan table header — 青色页眉带；右侧浅蓝信息栏；青底白字表头 | 要点+侧栏数据；现代感、图表多 |
| 5 | `bernstein_monochrome` | 伯恩斯坦（学术黑白风） / Monochrome | Strict black-and-white, black masthead bar, serif body, dense grid — 纯黑白；黑顶栏；衬线正文；紧凑网格 | 学术/量化研究；黑白打印；去营销感 |
| 6 | `ubs_swissminimal` | 瑞银（瑞士极简风） / Swiss Minimal | Two-tier title bands, deep navy + pale blue, right info rail, wide margins — 双层标题色带；深海军蓝+浅蓝；右侧信息栏；宽边距 | 高端克制的机构风格；中等密度 |

**Rules / 规则:**

- The style names are **labels only**. No institution logo, wordmark, watermark or text mark appears in the
  rendered report — the templates are style-only reconstructions (see `templates/styles/README.md`).
- **Mix & match is allowed / 允许混搭自定义:** the user may say "base it on X but use Y's tables".
  Record the base id in `template_id`, and describe the override in `special_requests`
  (e.g. `"template mix: base ubs_swissminimal + barclays_cyanline table header"`).
- If the user has no preference, use the default **`goldman_hardline`** and say so.
- Echo the choice back in one line before moving on.

**中文：** 展示六套模板（名称+风格一句话+适用场景）请用户选择；允许混搭/自定义（基础 id 写 `template_id`，
改动写进 `special_requests`）；模板只是版式风格标签，不含任何机构 logo/文字标识；用户无偏好时默认
`goldman_hardline` 并明示。

---

## 4. Step 2 — Focus questionnaire / 第二步：本次研究的侧重方向

Ask all six questions. Each has options **and** a default; mark unanswered items as "default applied".

| # | Question / 问题 | Field | Options / 选项 | Default |
|---|---|---|---|---|
| Q1 | **研究侧重**（多选） | `focus_areas` | `valuation` 估值 · `growth` 成长 · `cyclical` 周期 · `event-driven` 事件驱动 · `defensive` 防御 · `bull-bear` 多空辩论 | `["valuation","growth"]` |
| Q2 | **投资期限** | `horizon` | `short` ≤3 个月 · `medium` 6–12 个月 · `long` >12 个月 | `medium` |
| Q3 | **报告深度** | `depth` | `quick` 快速简报（无红队子代理、无图） · `standard` 标准研报（全链、≥3 图） · `deep` 完整深度（全图集、两轮红队） | `standard` |
| Q4 | **输出语言** | `language` | `en` 英文 · `bilingual` 中英对照 · `zh` 中文 | `en` |
| Q5 | **图表密度** | `chart_density` | `low` 1–2 张 · `standard` 3–5 张 · `high` 全图集（6+） | `standard` |
| Q6 | **特殊要求**（多选/自由文本） | `special_requests` | ESG · 技术面 · 政策面 · 同业对比 · 分红/回购 · 空头论点 · 自定义 | `[]`（无） |

- Q1 accepts multiple tokens, comma-separated on the CLI (`--focus valuation,growth`).
- Q3: `full` is accepted as an alias of `deep` (the CLI normalises it).
- Q6 is free text; each item becomes one entry in `special_requests[]`.
- If the user answers only some questions, apply defaults to the rest and **list them as defaults**.

**中文：** 六个问题（侧重多选 / 期限 / 深度 / 语言 / 图表密度 / 特殊要求），每题都给选项与默认值；
只答一部分时其余用默认值并标注；`--focus` 逗号分隔多选；`--depth full` 等价于 `deep`。

---

## 5. Output artifact — `brief/intake.json` / 落盘格式

Path convention / 路径约定:

- **Repo-level intake area:** `brief/intake.json` (singular `brief/`; the pre-run input area).
- At **S1** the main agent copies it into the run: `{RUN_ROOT}/briefs/intake.json`
  (plural `briefs/` = per-run briefs) so every run is self-contained and auditable.
- The CLI defaults to `<repo_root>/brief/intake.json`; override with `--out PATH`.

JSON shape / 结构（field set is fixed; values must be from the allowed sets above）:

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

| Field | Type | Required | Allowed values / notes |
|---|---|---|---|
| `template_id` | string | yes | one of the six ids in §3 |
| `template_display_name` | string | yes | echo of the template's `display_name` (auto-filled by the CLI) |
| `focus_areas` | array[string] | yes | ≥1 of `valuation` `growth` `cyclical` `event-driven` `defensive` `bull-bear` |
| `horizon` | string | yes | `short` \| `medium` \| `long` |
| `depth` | string | yes | `quick` \| `standard` \| `deep` |
| `language` | string | yes | `en` \| `bilingual` \| `zh` |
| `chart_density` | string | yes | `low` \| `standard` \| `high` |
| `special_requests` | array[string] | yes (may be `[]`) | free text; one entry per request |
| `created_at` | string | yes | ISO-8601 with timezone offset |

**中文：** 产物固定为 `brief/intake.json`（九个字段，见上表）；S1 时复制进 `{RUN_ROOT}/briefs/intake.json`
保证每轮自包含；CLI 默认写到仓库根 `brief/intake.json`，可用 `--out` 覆盖。

---

## 6. How the answers are injected / 答案如何注入后续阶段

| Intake field | Injected at / into | Effect / 作用 |
|---|---|---|
| `template_id` | S7 layout brief, S8 conversion | `python templates/md_to_docx.py final/report.md -o final/report.docx --pdf --style <template_id>` — the report is typeset in the chosen template. |
| `focus_areas` | S2 master brief → analyst briefs; S4 Red Team; S5 adjudication & skeleton | Sets **research-lens weights** (e.g. valuation-heavy vs growth-heavy), which sections come first, which claims get the most evidence; the Red Team prioritises its question bank on these lenses (e.g. `bull-bear` → force a full bear case; `event-driven` → challenge the catalyst calendar). |
| `horizon` | Valuation model, scenario periods, catalyst calendar, report wording | `short` → trading/quarterly framing, no long-DCF; `medium` → 12-month target price & scenarios; `long` → 3–5-year compounding case. |
| `depth` | Whole pipeline | `quick` → skip the Red Team child (inline red-flag scan) and S6 charts; `standard` → full chain, ≥3 figures; `deep` → full figure set, 2 Red Team rounds. Copied into `envelope.depth`. |
| `language` | `envelope.language`; all narratives, chart labels/captions, layout | Report language; source quotes keep their native language with `[S###]` citations. |
| `chart_density` | S6 figure plan | `low` → 1–2 figures (price + one valuation); `standard` → 3–5 core figures; `high` → full set incl. peer comparison / sensitivity. |
| `special_requests` | S2 role briefs, S4 question bank, S5 skeleton, S7 layout, disclosures | Each item becomes an explicit deliverable or evidence requirement (ESG → ESG evidence + section; 技术面 → technical chart + levels; 政策面 → policy scan; 同业对比 → peer table + relative valuation). |
| `created_at` | Audit trail | Provenance of the intake. |

**Envelope wiring (S1):** copy `language`, `depth`, `horizon`, `template_id`, `chart_density`, `focus_areas`
into `envelope.json` (new optional fields, see `pipeline_orchestration.md` §5) and derive
`focus_question` / `constraints` from them. The intake file remains the source of truth for S0 answers.

**中文：** `template_id`→排版阶段 `--style`；`focus_areas`→研究透镜权重、红队质询重点与章节顺序；
`horizon`→估值窗口/情景/催化剂；`depth`→阶段裁剪；`language`→写作与图表语言；`chart_density`→图表选择；
`special_requests`→额外证据与章节要求。S1 把这些字段抄进 `envelope.json`。

---

## 7. S0 quality gate (G0) / 质量门

Before proceeding to S1, all items must pass:

- [ ] Template chosen (or default declared to the user); `template_id` is one of the six ids.
- [ ] All six questionnaire items answered or explicitly defaulted.
- [ ] `brief/intake.json` written, valid JSON, all nine fields present, values inside the allowed sets.
- [ ] The agent echoed the final answers back to the user (one compact block).
- [ ] `template_display_name` matches the template's `display_name`.

**Fail →** ask the user once more for the missing/invalid item; if still unavailable, apply defaults and
disclose them in the delivery summary. Never invent a user preference.

**中文：** 模板已选/已声明默认、六问已回答或明示默认、JSON 九字段合法、答案已回显；
不合格→再问一次，仍无法获得则用默认值并在交付时披露，不得编造。

---

## 8. Discipline / 纪律

1. **Style labels only** — no institution logo, wordmark, watermark or text mark is ever rendered or embedded.
2. **Ask once** — one intake per run; no interrogation loops.
3. **Defaults must be visible** — if the user did not answer, say "default applied" and record it.
4. **Agent-agnostic** — the stage is a text procedure; any agent or human can execute it with file I/O only.
5. **Never block the run** — intake must not stall a run the user has already authorised; degrade to defaults + disclose.

**中文：** 只用品类风格名称、不出现机构标识；每轮只问一次；默认值必须明示；任何代理/人工可执行；
用户已授权时不得因 intake 卡住流程——降级为默认值并披露。
