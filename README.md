# Wall Street Research — Full-Chain Equity Research Skill

> **"You can work for Wall Street."** A self-contained, agent-agnostic equity research pipeline that produces
> sell-side-grade research reports — methodology distilled from **100 Wall Street research reports**,
> powered by **real market data**, rendered with **institutional charts** and **Wall Street typography**.
> Works with **any AI agent** (Claude Code, Codex, Cursor, Hermes, plain LLM chat) **or fully manually**.

[English](#english) · [中文](#chinese)

---

## English

### What this is

A complete, portable "research department in a box." Give it a ticker, a market, a language, a depth
tier, a **layout template** and a **research focus** (both asked up front by the S0 intake) — it runs a
disciplined multi-agent pipeline (data engineer → analysts → red team → editor-in-chief →
chart specialist → layout specialist), grounds every number in **live fetched data** (never invented),
challenges its own conclusions with a dedicated adversarial role, and ships a Wall Street-style report
(Markdown master → Word/PDF).

It is **agent-agnostic by design**: no platform-specific runtime, no proprietary CLI. The `pipeline/`
briefs are plain copy-paste prompts; `scripts/` are standalone Python; anyone — a human, any AI tool —
can drive the whole chain.

### Why it stands out

| | Typical "research skill" | This repo |
|---|---|---|
| Methodology | prompt template + generic advice | **7-chapter paradigm manual distilled from 100 real Wall Street reports** (10 groups × 10 reports, each digested across 5 dimensions) |
| Numbers | often invented by the LLM | **real dual-market data** (US: Yahoo Finance; CN: Tencent/Eastmoney), fetched by reusable scripts |
| Red team | none | **dedicated adversarial role** that attacks every claim against a red-flag checklist |
| Charts | none / screenshots | **5 institutional chart families** (K-line+volume+MACD, PE band, financial trends, scenario tree, peer comparison), 500 dpi, Wall Street navy theme |
| Layout | plain markdown | **sell-side typography**: cover page, rating box, Exhibit-numbered figures, FINRA-style disclosures, Page X of Y |
| Layout choice | one fixed style | **6 selectable style presets** (`--style goldman_hardline`, `bernstein_monochrome`, …) + an **S0 intake** that asks the user which one and what to focus on |
| Portability | locked to one platform | **agent-agnostic**: runs on any AI tool or by hand |

### Quick start

```bash
# 1) Install dependencies
pip install -r requirements.txt

# 2) S0 intake — pick a layout template + answer the focus questionnaire → brief/intake.json
python scripts/intake/intake.py --list
python scripts/intake/intake.py --template goldman_hardline --focus valuation,growth \
    --horizon medium --depth full --language en --charts high --notes "focus on FCF inflection"

# 3) Fetch real data (US NVDA + CN 600519 examples)
python scripts/data/data_fetcher.py us NVDA all --json
python scripts/data/data_fetcher.py cn 600519 all --json

# 4) Generate the five institutional chart families (sample PNGs land in scripts/charts/sample_pngs/)
python scripts/charts/report_charts.py

# 5) Convert a Wall Street Markdown report to Word + PDF, typeset in the chosen template
python templates/md_to_docx.py examples/layout_demo/example_report.md -o report.docx --pdf --style goldman_hardline
```

### Repository layout

```
wallstreet-research/
├── README.md                     ← you are here — how to run the whole chain anywhere
├── SKILL.md                      ← skill-loader entry (Hermes / Claude-style skills) — optional adapter
├── requirements.txt              ← single dependency manifest
├── methodology/                  ← the intellectual core (agent-agnostic)
│   ├── report_list_100.md        ← 100 Wall Street reports, 10 groups, all with verifiable sources
│   └── digests/                  ← 10 group digests (10 reports × 5 dimensions each) + seed 30
│   └── wallstreet_paradigm_manual.md   ← 7-chapter paradigm manual (assembled from the digests)
├── pipeline/                     ← the workflow (agent-agnostic)
│   ├── intake.md                 ← S0 intake: layout-template choice + research-focus questionnaire (EN/ZH)
│   ├── pipeline_orchestration.md ← 10-stage full-chain design (S0 intake → envelope → brief → research → red team → adjudicate → charts → layout → delivery → proofing)
│   └── agent_prompts.md          ← 6 roles × (EN + ZH) copy-paste briefs, with quality gates
├── scripts/                      ← mechanical work = standalone Python (no agent required)
│   ├── intake/                   ← S0 intake CLI: --list templates / write brief/intake.json
│   ├── data/                     ← dual-market data layer (Yahoo US / Tencent+Eastmoney CN)
│   ├── charts/                   ← institutional chart families + Wall Street theme + CJK font handling
│   └── layout/                   ← layout engineering notes (README)
├── templates/                    ← Wall Street Markdown master + python-docx renderer
│   └── styles/                   ← 6 layout style presets (*.json) + catalogue/README + SOURCES.md
└── examples/
    └── layout_demo/              ← a fully filled sample report + verified .docx/.pdf outputs
```

### Using it with any AI agent

1. **Run S0 intake** — `pipeline/intake.md`: ask the user to pick one of the six layout templates and
   answer the focus questionnaire (focus / horizon / depth / language / chart density / special requests),
   then write `brief/intake.json`. One-shot it with
   `python scripts/intake/intake.py --template <id> --focus valuation,growth --depth full ...`.
2. **Read** `pipeline/agent_prompts.md`. It contains copy-paste briefs for all six roles (Data Engineer,
   Industry Analyst, Valuation Analyst, Red Team, Chart Specialist, Layout Specialist), bilingual EN+ZH.
3. **Start the pipeline**: paste the *Editor-in-Chief* instructions (or the "how to run" section of
   `pipeline/pipeline_orchestration.md`) into your agent of choice. It will fan out the roles, run the
   `scripts/` for mechanical work, adjudicate, and assemble — injecting the intake answers (focus lens
   weights, horizon, depth, language, chart density, template id) at each stage.
4. **Depth tiers** are built in: `quick` (no figures, 1-page), `standard`, `deep` (full chain).
5. Everything the agents produce is plain files — swap agents mid-run freely; nothing is locked in.

### How the methodology was built

- **100 Wall Street reports** (Goldman, Morgan Stanley, J.P. Morgan, UBS, BofA, Bridgewater, Muddy Waters,
  Hindenburg, Burry/Scion, Einhorn, Chanos, ARK, AQR, …) were catalogued across 10 theme groups
  (`methodology/report_list_100.md`), each with verifiable sources.
- **10 parallel sub-agents** each digested one group — research method / writing paradigm / chart usage /
  reusable moves / lessons & red flags — into `methodology/digests/groupN.md`.
- A **synthesizer** merged the 10 digests into the **7-chapter Wall Street Paradigm Manual**
  (`methodology/wallstreet_paradigm_manual.md`): report architecture, methods catalog, writing canon,
  chart canon, evidence discipline, red-flag checklist, and a red-team question bank.

### Data sources & ethics

- **US**: Yahoo Finance v8 chart / v7 quote / v10 quoteSummary (OHLCV, pre/post market, snapshot, fundamentals).
  From mainland China this requires a SOCKS5 proxy (see `scripts/data/README.md`).
- **CN**: Tencent `qt.gtimg.cn` realtime (GBK), Tencent K-line (前复权), Eastmoney datacenter fundamentals.
- Every figure in the pipeline traces to a live API response. The agents **never hand-type data**.
- All scripts are read-only public-data fetchers — no keys, no trading, no write endpoints.
- The methodology is *pattern-level* (how great research argues), not republished copyrighted text.

### License

MIT — reuse freely, attribute if you like. The methodology digests are analytical notes on public reports.
Market data is provided by the cited public APIs under their own terms.
