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
| [`proof/`](proof) | Page renders used for the S9 visual proofing gate |
| [`data/`](data) | Raw API responses + `numbers.json` |

## Reproduce

```bash
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

# 5. Optional: re-render pages for the S9 visual proofing gate
python -c "import pymupdf; d=pymupdf.open('examples/unitree_vs_nvidia/unitree_vs_nvidia.pdf'); \
[pg.get_pixmap(dpi=144).save(f'examples/unitree_vs_nvidia/proof/page{i+1:02d}.png') \
 for i,pg in enumerate(d)]"
```

Then open [`unitree_vs_nvidia.pdf`](unitree_vs_nvidia.pdf).
