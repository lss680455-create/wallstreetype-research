# -*- coding: utf-8 -*-
"""
chart_style.py — Wall Street Research report chart theme.

Central theme (deep-navy, print-ready, Wall Street sell-side paradigm),
Chinese font auto-detection with fallback, and shared rendering helpers
(footer, axes styling, high-DPI PNG export).

Usage
-----
    import chart_style as cs
    cs.apply_theme()                 # once, before any plotting
    fig, ax = plt.subplots(...)
    ... draw ...
    cs.add_footer(fig, source="Wind, Company filings, Analyst estimates",
                  left="Wall Street Research", right="2026-09-10")
    cs.save_fig(fig, "out.png", dpi=500)

Design tokens follow the standard investment-bank visual language:
deep navy primary, gold accent, light grid, white print background.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Palette (Wall Street research paradigm)
# --------------------------------------------------------------------------
NAVY       = "#0F2A43"   # primary: deep institutional navy
NAVY_DARK  = "#0A1D31"   # darkest navy (title, bars)
NAVY_MID   = "#1F4E79"   # medium navy (lines, secondary series)
SKY        = "#3D7EA6"   # light navy-blue (secondary lines)
GOLD       = "#C9A227"   # accent: muted institutional gold
GOLD_LIGHT = "#E8C766"   # light gold (fills, highlights)
UP_GREEN   = "#1E8449"   # up / bull (US convention; see UP_COLOR)
DOWN_RED   = "#C0392B"   # down / bear
GRAY       = "#7F8C99"   # muted gray (annotation text)
GRID       = "#E4E9EF"   # faint grid lines
TEXT       = "#1B2A38"   # body text
BG         = "#FFFFFF"   # print background (white)

# Market convention switch: US style green-up/red-down; A-share users may set
# UP_COLOR = DOWN_RED and DOWN_COLOR = UP_GREEN (red-up). Default: US/Wall St.
UP_COLOR   = UP_GREEN
DOWN_COLOR = DOWN_RED

# --------------------------------------------------------------------------
# Fonts — detect a real CJK font (SimHei / Microsoft YaHei / DengXian / SimSun)
# --------------------------------------------------------------------------
_WIN_FONT_CANDIDATES = [
    ("Microsoft YaHei", "msyh.ttc"),   # Windows 10/11 default UI font
    ("SimHei",          "simhei.ttf"),  # bold sans, classic for charts
    ("DengXian",        "Deng.ttf"),    # Win10+ elegant sans
    ("SimSun",          "simsun.ttc"),  # serif fallback
    ("KaiTi",           "simkai.ttf"),  # last-resort CJK
]

_detected_font: str | None = None


def _system_font_dirs() -> list[Path]:
    dirs = []
    windir = os.environ.get("WINDIR") or r"C:\Windows"
    dirs.append(Path(windir) / "Fonts")
    if os.name == "posix":  # Linux/macOS common paths
        dirs += [Path("/usr/share/fonts"), Path("/System/Library/Fonts")]
    return dirs


def detect_cjk_font(verbose: bool = False) -> str | None:
    """Return the family name of the best available CJK font, or None.

    Priority: Microsoft YaHei > SimHei > DengXian > SimSun > KaiTi.
    Searches the OS font directories directly, then matplotlib's registry.
    """
    global _detected_font
    if _detected_font:
        return _detected_font

    # 1) Direct file search in system font dirs (most reliable on Windows).
    for family, fname in _WIN_FONT_CANDIDATES:
        for d in _system_font_dirs():
            p = d / fname
            if p.is_file():
                try:
                    fm.fontManager.addfont(str(p))
                except Exception:
                    pass  # already registered or unreadable; keep probing
                _detected_font = family
                if verbose:
                    print(f"[chart_style] CJK font -> {family} ({p})")
                return family

    # 2) Fallback: ask matplotlib's registry.
    wanted = [fam for fam, _ in _WIN_FONT_CANDIDATES]
    installed = {f.name for f in fm.fontManager.ttflist}
    for fam in wanted:
        if fam in installed:
            _detected_font = fam
            if verbose:
                print(f"[chart_style] CJK font -> {fam} (matplotlib registry)")
            return fam

    _detected_font = None
    if verbose:
        print("[chart_style] WARNING: no CJK font found; CJK glyphs may be tofu")
    return None


def font_family() -> str:
    """Return the resolved font family, falling back to DejaVu Sans."""
    return detect_cjk_font() or "DejaVu Sans"


def font_prop(size: float = 10, weight: str = "normal"):
    """Build a FontProperties for a single text element (titles etc.).

    NOTE: color is NOT a FontProperties attribute in matplotlib 3.x — set it
    on the text artist instead (e.g. fig.text(..., color=...) ).
    """
    return fm.FontProperties(family=font_family(), size=size, weight=weight)


# --------------------------------------------------------------------------
# Theme application
# --------------------------------------------------------------------------
def apply_theme(verbose: bool = False) -> None:
    """Apply the Wall Street theme to matplotlib's global rcParams.

    Safe to call multiple times. Must be called before mplfinance plots too
    (mplfinance inherits matplotlib rcParams; pass rc=theme_rc() to be sure).
    """
    fam = detect_cjk_font(verbose=verbose)

    mpl.rcParams.update({
        # Fonts
        "font.family": [fam, "DejaVu Sans"] if fam else "DejaVu Sans",
        "font.sans-serif": ([fam] if fam else []) + [
            "Microsoft YaHei", "SimHei", "DengXian", "DejaVu Sans"],
        "axes.unicode_minus": False,          # CRITICAL: CJK fonts lack U+2212
        "mathtext.fontset": "dejavusans",

        # Figure / axes
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.7,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": NAVY_DARK,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "axes.labelweight": "normal",
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",
        "grid.alpha": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": True,

        # Ticks
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "xtick.direction": "out",
        "ytick.direction": "out",

        # Legend / text
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "legend.facecolor": BG,
        "text.color": TEXT,

        # Output
        "savefig.dpi": 500,
        "savefig.facecolor": BG,
        "savefig.bbox": "tight",
        "figure.dpi": 110,
    })


def theme_rc() -> dict:
    """mplfinance-compatible rc block (call apply_theme() first)."""
    return {
        "font.family": mpl.rcParams["font.family"],
        "font.sans-serif": mpl.rcParams["font.sans-serif"],
        "axes.unicode_minus": False,
    }


# --------------------------------------------------------------------------
# Shared rendering helpers
# --------------------------------------------------------------------------
def style_axes(ax, grid_axis: str = "y", grid: bool = True) -> None:
    """Light-touch axes cleanup: faint grid, no top/right spines."""
    ax.grid(visible=grid, axis=grid_axis, color=GRID, linewidth=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_axisbelow(True)


def add_header(fig, title: str, subtitle: str | None = None,
               ax: plt.Axes | None = None, title_x: float = 0.02,
               title_y: float = 0.985) -> None:
    """Draw the research-report header (bold navy title + gray subtitle)."""
    fig.text(title_x, title_y, title, fontproperties=font_prop(15, "bold"),
             color=NAVY_DARK, ha="left", va="top")
    if subtitle:
        fig.text(title_x, title_y - 0.042, subtitle,
                 fontproperties=font_prop(9.5), color=GRAY, ha="left", va="top")


def add_footer(fig, source: str = "Data source: Company filings, Wind, analyst estimates",
               left: str = "Wall Street Research", right: str | None = None,
               disclaimer: str = "For research purposes only. Not investment advice.") -> None:
    """Research-report footer: source line + left/right meta + disclaimer.

    All three rows are tiny and gray so they stay out of the chart's way.
    """
    import datetime as _dt
    if right is None:
        right = _dt.date.today().isoformat()
    y0 = 0.012
    fig.text(0.02, y0, source, fontproperties=font_prop(7),
             color=GRAY, ha="left", va="bottom")
    fig.text(0.02, y0 + 0.022, disclaimer,
             fontproperties=font_prop(6), color=GRAY, ha="left", va="bottom")
    fig.text(0.98, y0, f"{left}  |  {right}",
             fontproperties=font_prop(7), color=GRAY, ha="right", va="bottom")


def save_fig(fig, out_path: str | Path, dpi: int = 500) -> Path:
    """Export to high-res PNG, white background, tight bbox."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    return out_path


def load_apply() -> tuple[str, str]:
    """Convenience: apply theme and return (font_family, detected_cjk)."""
    apply_theme()
    return font_family(), detect_cjk_font() or "NONE"
