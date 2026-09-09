---
name: wallstreet-research
description: >
  Use when 需要生成华尔街风格股票研报/深度投研报告/投资研究流水线。
  Full-chain, agent-agnostic equity research: 100-report-derived paradigm manual,
  multi-agent pipeline briefs (EN+ZH), dual-market real data scripts (US Yahoo / CN Tencent-Eastmoney),
  institutional charts, Wall Street docx/PDF layout. Works with any AI tool or manually.
version: 1.0.0
author: Wall Street Research contributors
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [equity-research, research-report, multi-agent, wall-street, methodology, data, charts, layout]
    related_skills: [wall-street-research-methodology, equity-research]
---

# Wall Street Research（华尔街研报全链路）

自包含、agent 无关的研报流水线：输入标的/市场/语言/深度档位 → 出华尔街风格研报（Markdown→Word/PDF）。
方法论源自 **100 篇华尔街研报**（10 组 × 10 篇凝练），数字走**真实双市场数据**，图表为机构风格，版式为卖方范式。

**核心文件（本 skill 目录内）：**

| 资产 | 路径 | 用途 |
|---|---|---|
| 范式手册 | `methodology/wallstreet_paradigm_manual.md` | 7章：论证骨架/方法总库/行文范式/图表规范/证据纪律/红旗清单/红队质询库 |
| 100篇清单 | `methodology/report_list_100.md` | 可溯源的方法论种子库 |
| 组凝练 | `methodology/digests/group1..10.md` | 每篇五维凝练（方法/行文/图表/动作/教训） |
| 流水线设计 | `pipeline/pipeline_orchestration.md` | 8阶段全链路（envelope→简报→并行研究→红队→仲裁→图表→排版→交付） |
| 角色brief | `pipeline/agent_prompts.md` | 6角色 × 中英双语 直接复制的 prompt，含质量门 |
| 数据层 | `scripts/data/` | 美股 Yahoo / A股 腾讯+东财，纯 requests，`python data_fetcher.py <us|cn> <代码> <quote|history|financials|all>` |
| 图表层 | `scripts/charts/` | 五类机构图表（K线+量+MACD / PE band / 财务趋势 / 情景 / 同业对比），500dpi，中文自动字体 |
| 排版层 | `templates/` | `report_template.md`（华尔街母版）+ `md_to_docx.py`（→docx/PDF） |
| 示例 | `examples/layout_demo/` | 完整填充示例 + 验证过的 docx/pdf |

## 快速使用

```bash
pip install -r requirements.txt
python scripts/data/data_fetcher.py us NVDA all --json     # 取数
python scripts/charts/report_charts.py                      # 出图（样例入 sample_pngs/）
python templates/md_to_docx.py examples/layout_demo/example_report.md -o report.docx --pdf  # 排版
```

## 跑一条完整研报流水线

1. 选深度档位：`quick`（无图1页）/ `standard` / `deep`（全链）。
2. 主 agent 按 `pipeline/pipeline_orchestration.md` 的 8 阶段驱动；每个子角色 brief 在
   `pipeline/agent_prompts.md`（中英双语，直接复制）。
3. 机械工作（取数/绘图/排版）交给 `scripts/` 与 `templates/` 的独立 Python 脚本——agent 不手打数据。
4. 主编仲裁必须保留 minority report；红队结论写进风险章节；每张图带 Exhibit 编号与来源脚注。

## 关键纪律（来自范式手册，写进每个 brief）

- 结论可证伪，写明"什么证据会推翻我"；观点=可证伪假设+仓位。
- 每个核心数字有来源+口径（分母/时点/定义）；禁止无 provider/日期的 "consensus"。
- 证据分级：fact > reported-metric > guidance > forecast > assumption > opinion。
- TAM 必须拆到 份额×时点×margin bridge，不能当公司收入。
- 评级/目标价不是证据本身；情景带概率权重；反方正面处理。
- 红旗清单与红队质询库见范式手册 Chapter 6-7，直接复制给质询官角色。
