# Example — Unitree Robotics vs NVIDIA

End-to-end run of the pipeline. Everything below was produced by the scripts in
this folder; nothing is hand-typed.

## Artifacts

| File | What it is |
|---|---|
| [`unitree_vs_nvidia.pdf`](unitree_vs_nvidia.pdf) | Finished report, 7 pages — cover, rating box, key data, six figures |
| [`unitree_vs_nvidia.docx`](unitree_vs_nvidia.docx) | Same report as an editable Word file |
| [`unitree_vs_nvidia.md`](unitree_vs_nvidia.md) | Markdown source with YAML front matter |
| [`figures/`](figures) | The six exhibit PNGs |
| [`brief/industry_logic.md`](brief/industry_logic.md) | S1 industry-logic map (five moves) — written by `make_logic_brief.py` from `data/numbers.json` |
| [`brief/direction_confirmed.json`](brief/direction_confirmed.json) | S1 direction contract — the six answers that gate G0b checks |
| [`proof/`](proof) | Page renders used for the S10 visual proofing gate |
| [`data/`](data) | Raw API responses + `numbers.json` |

## Reproduce

```bash
# 0. S1 direction contract: the five-move industry map, then the six questions and gate G0b
python scripts/intake/direction_check.py --questions                 # what the run asks before it starts
python examples/unitree_vs_nvidia/make_logic_brief.py                # → brief/industry_logic.md
python scripts/intake/direction_check.py --check examples/unitree_vs_nvidia/brief/direction_confirmed.json

# 1. Fetch raw data (A-share: Tencent + East Money; US: Yahoo Finance)
python scripts/data/data_fetcher.py cn 688836 all --json
python scripts/data/data_fetcher.py us NVDA   all --json

# 2. Compute every number used in the report → data/numbers.json
python examples/unitree_vs_nvidia/compute_numbers.py

# 3. Draw the six exhibits → figures/
python examples/unitree_vs_nvidia/make_case_charts.py

# 4. Export the report in the goldman_hardline layout
python templates/md_to_docx.py examples/unitree_vs_nvidia/unitree_vs_nvidia.md \
    --style goldman_hardline --pdf --toc

# 5. Optional: re-render pages for the S10 visual proofing gate
python -c "import pymupdf; d=pymupdf.open('examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf'); \
[pg.get_pixmap(dpi=144).save(f'examples/unitree_vs_nvidia/proof/page{i+1:02d}.png') \
 for i,pg in enumerate(d)]"
```

Then open [`unitree_vs_nvidia.pdf`](unitree_vs_nvidia.pdf).

`brief/` is a retrofit: the report was produced before the S1 ring existed, so those two files are a
*filled sample* of the direction contract rather than the answers that drove this report. Their numbers
still come from `data/numbers.json` — nothing in them is hand-typed.
