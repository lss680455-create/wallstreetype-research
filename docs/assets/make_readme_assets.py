"""Generate the README's visual assets (hero banner + pipeline architecture figure).

Same discipline as the rest of the repo: the stage names, actors and artifacts
below mirror pipeline/pipeline_orchestration.md — no numbers or claims are
invented here.

    python docs/assets/make_readme_assets.py

Outputs: docs/assets/hero.png, docs/assets/architecture.png
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "charts"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

import chart_style as cs  # noqa: E402

# --------------------------------------------------------------------------
# Content (single source of truth for the figures)
# --------------------------------------------------------------------------
STAGES = [
    ("S0", "Intake", "Editor", "brief/intake.json", "G0"),
    ("S1", "Industry Logic", "Editor", "brief/industry_logic.md", "G0b"),
    ("S2", "Input & Envelope", "Editor", "envelope.json", "G0c"),
    ("S3", "Master Brief", "Editor", "briefs/master_brief.md", "G0d"),
    ("S4", "Parallel Research", "3 children", "data · industry · valuation", "G1"),
    ("S5", "Red Team Challenge", "1 child", "review/redteam.md", "G2"),
    ("S6", "Adjudication", "Editor", "decisions/decision.json", "G3"),
    ("S7", "Charting", "1 child", "charts/manifest.json", "G4"),
    ("S8", "Layout & Assembly", "1 child", "draft/report_draft.md", "G5"),
    ("S9", "Final Review", "Editor", "final/report.md", "G6"),
    ("S10", "Proofing & QC", "Editor + vision", "proof/visual_proofing.md", "G7"),
]

FEATURES = ["US + A-share", "zero API keys", "5 chart families", "6 layouts", "S0-S10 pipeline"]


# --------------------------------------------------------------------------
# 1) Hero banner
# --------------------------------------------------------------------------
def hero(out: Path = HERE / "hero.png") -> Path:
    cs.apply_theme()
    fig = plt.figure(figsize=(12.6, 3.15), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.patch.set_facecolor("white")

    ax.add_patch(Rectangle((0, 0), 0.024, 1, color=cs.NAVY_DARK, zorder=2))

    ax.text(0.055, 0.745, "wallstreetype-research", fontsize=30,
            color=cs.NAVY_DARK, va="center", ha="left",
            fontproperties=cs.font_prop(30, weight="bold"))
    ax.text(0.055, 0.545, "Sell-side research, built like an engineering pipeline",
            fontsize=13, color=cs.GRAY, va="center", ha="left",
            fontproperties=cs.font_prop(13))
    ax.text(0.055, 0.385, "You can work for Wall Street.",
            fontsize=11.5, color=cs.GOLD, va="center", ha="left",
            fontproperties=cs.font_prop(11.5), style="italic")
    ax.plot([0.055, 0.325], [0.30, 0.30], color=cs.GOLD, lw=1.6, zorder=3)

    # Measure the chip labels, then size the boxes to fit the available width.
    left, right, gap = 0.055, 0.975, 0.014
    pads = [0.030, 0.022, 0.014]
    meas = []
    for f in FEATURES:
        t = ax.text(0, -1, f, fontsize=8.6, fontproperties=cs.font_prop(8.6))
        meas.append(t.get_window_extent(renderer=fig.canvas.get_renderer()).width
                    / fig.bbox.width)
        t.remove()

    total = sum(meas) + gap * (len(FEATURES) - 1)
    for pad in pads:
        if total + pad * len(FEATURES) <= right - left:
            break
    avail = right - left
    if total + pad * len(FEATURES) > avail:            # last resort: shrink the gap
        gap = max(0.006, (avail - total - pad * len(FEATURES)) / max(1, len(FEATURES) - 1))
        total = sum(meas) + gap * (len(FEATURES) - 1)

    x, y0, hgt = left, 0.10, 0.135
    for f, w in zip(FEATURES, meas):
        w += pad
        ax.add_patch(FancyBboxPatch((x, y0), w, hgt,
                                    boxstyle="round,pad=0.006,rounding_size=0.03",
                                    linewidth=0.9, edgecolor=cs.NAVY, facecolor="#F2F5F9",
                                    zorder=2))
        ax.text(x + w / 2, y0 + hgt / 2, f, fontsize=8.6, color=cs.NAVY_DARK,
                ha="center", va="center", fontproperties=cs.font_prop(8.6))
        x += w + gap

    fig.savefig(out, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------
# 2) Pipeline architecture
# --------------------------------------------------------------------------
def architecture(out: Path = HERE / "architecture.png") -> Path:
    cs.apply_theme()
    n = len(STAGES)
    fig = plt.figure(figsize=(12.6, 6.4), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.patch.set_facecolor("white")

    ax.text(0.02, 0.952, "Eleven-stage research pipeline", fontsize=16,
            color=cs.NAVY_DARK, va="center", fontproperties=cs.font_prop(16, weight="bold"))
    ax.text(0.02, 0.908, "Gates G0–G7 sit between stages; failing a gate sends the stage back.",
            fontsize=9.2, color=cs.GRAY, va="center", fontproperties=cs.font_prop(9.2))

    top, bot = 0.845, 0.075
    h = (top - bot) / n
    col_id, col_name, col_who, col_art = 0.032, 0.088, 0.355, 0.495
    head_y = top + 0.014

    for label, x in (("STAGE", col_name), ("WHO", col_who), ("ARTIFACT", col_art)):
        ax.text(x, head_y, label, fontsize=8.4, color=cs.GRAY,
                va="bottom", ha="left", fontproperties=cs.font_prop(8.4, weight="bold"))
    ax.plot([0.02, 0.965], [head_y - 0.014, head_y - 0.014], color=cs.NAVY, lw=1.1)

    for i, (sid, name, who, art, gate) in enumerate(STAGES):
        y = top - (i + 1) * h
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.02, y), 0.945, h, facecolor="#F5F7FA",
                                   edgecolor="none", zorder=0))
        ax.add_patch(Rectangle((0.02, y), 0.005, h, facecolor=cs.NAVY, edgecolor="none", zorder=1))

        ax.text(col_id + 0.012, y + h / 2, sid, fontsize=10,
                color=cs.GOLD if i in (3, 6) else cs.NAVY_DARK, va="center",
                fontproperties=cs.font_prop(10, weight="bold"))
        ax.text(col_name, y + h / 2, name, fontsize=10.2, color=cs.TEXT, va="center",
                fontproperties=cs.font_prop(10.2))
        ax.text(col_who, y + h / 2, who, fontsize=9.2, color=cs.NAVY, va="center",
                fontproperties=cs.font_prop(9.2))
        ax.text(col_art, y + h / 2, art, fontsize=8.6, color=cs.GRAY, va="center",
                fontproperties=cs.font_prop(8.6))

        if gate:
            ax.text(0.962, y + h / 2, gate, fontsize=8.2, color=cs.NAVY_DARK, ha="right",
                    va="center", fontproperties=cs.font_prop(8.2, weight="bold"))

    ax.plot([0.02, 0.965], [0.050, 0.050], color=cs.GRID, lw=0.9)
    ax.text(0.02, 0.026, "Editor = main agent (contract, adjudication, sign-off)"
                         "   ·   children = delegated subagents   ·   vision = visual QC model",
            fontsize=8.2, color=cs.GRAY, va="center", fontproperties=cs.font_prop(8.2))

    fig.savefig(out, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    return out


if __name__ == "__main__":
    for p in (hero(), architecture()):
        print(f"[readme-assets] wrote {p} ({p.stat().st_size / 1024:.0f} KB)")
