"""Journal figures built at their final printed size.

fig, ax = make_figure("AAB;CDE", width="full", height_mm=110, placeholders="E")
ax["A"].plot(x, y)
save_figure(fig, "fig1", png=True)
"""
import re
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.transforms import Bbox

from .colors import RAMPS
from .journals import DEFAULT_JOURNAL, figure_size_mm

# =============================================================================
# CONFIG: every number you may want to change lives here.
# palette.mplstyle is rebuilt from these values each time apply_style() runs.
# =============================================================================
# Figure widths and max height per journal are in journals.py.
SPACE_MM = 2                              # padding around each panel; gap between panels = 2 x this

FONT = ["Arial", "Helvetica"]                       # first one installed is used, else generic sans-serif
LETTER_FONT = ["Times New Roman", "Times"]          # panel letters; else generic serif
SIZE_PT = {"tick": 7, "label": 7, "title": 8, "legend": 6, "annotation": 6, "letter": 8}
LINE_PT = {"axes": 0.5, "data": 1.0}
TICK_DIRECTION = "out"
TICK_LENGTH_PT = 2
LETTER_OFFSET_MM = (0, 0.5)               # panel letter position from the top-left of the panel's full area
                                          # (axes + tick labels + axis labels + title), (x, y)

COLORS = [RAMPS[i][5] for i in (1, 2, 3, 4, 0)]   # default line colours: blue, rose, olive, amber, grey
PNG_DPI = 600
# =============================================================================

STYLE_FILE = Path(__file__).with_name("palette.mplstyle")


def mm2in(mm):
    return mm / 25.4


def _first_font(names):
    """Return the first font in `names` that is installed, or None."""
    for name in names:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            return name
        except ValueError:
            pass
    return None


def _style_text():
    s, w = SIZE_PT, LINE_PT
    return f"""# Palette figure style. Built from CONFIG in Palette/figure.py: edit the numbers there, not here.
font.family: sans-serif
font.sans-serif: {", ".join(FONT)}, DejaVu Sans
font.size: {s["annotation"]}
mathtext.default: regular

xtick.labelsize: {s["tick"]}
ytick.labelsize: {s["tick"]}
axes.labelsize: {s["label"]}
axes.titlesize: {s["title"]}
figure.titlesize: {s["title"]}
legend.fontsize: {s["legend"]}
legend.title_fontsize: {s["legend"]}

axes.linewidth: {w["axes"]}
lines.linewidth: {w["data"]}
axes.spines.top: False
axes.spines.right: False
axes.prop_cycle: cycler(color=[{", ".join(repr(c.lstrip("#")) for c in COLORS)}])

xtick.direction: {TICK_DIRECTION}
ytick.direction: {TICK_DIRECTION}
xtick.major.size: {TICK_LENGTH_PT}
ytick.major.size: {TICK_LENGTH_PT}
xtick.minor.size: {TICK_LENGTH_PT / 2}
ytick.minor.size: {TICK_LENGTH_PT / 2}
xtick.major.width: {w["axes"]}
ytick.major.width: {w["axes"]}
xtick.minor.width: {w["axes"]}
ytick.minor.width: {w["axes"]}

pdf.fonttype: 42
ps.fonttype: 42
savefig.bbox: standard
"""


def apply_style():
    """Apply the Palette style (rewrites palette.mplstyle first if CONFIG changed)."""
    text = _style_text()
    try:
        if not STYLE_FILE.exists() or STYLE_FILE.read_text() != text:
            STYLE_FILE.write_text(text)
    except OSError:
        warnings.warn(f"Could not update {STYLE_FILE}; using the saved copy.")
    plt.style.use(STYLE_FILE)
    if _first_font(FONT[:1]) is None:
        warnings.warn(f"Arial not found; using {_first_font(FONT) or 'a generic sans-serif'} instead.")


def make_figure(layout, width="full", height_mm=100, journal=DEFAULT_JOURNAL, width_ratios=None,
                height_ratios=None, space_mm=SPACE_MM, letters=True, placeholders=""):
    """Make a figure at its final printed size. Returns (fig, axes_dict).

    layout        mosaic string, e.g. "AAB;CDE" (one character per panel, "." = empty)
    width         a width name for the journal (e.g. "full", "single"), or a number in mm
    journal       a journal name from journals.py (e.g. "nature", "cell")
    letters       True (all panels), False (none), or the panels to label, e.g. "ACD"
    placeholders  panels left blank (letter only) for Keynote images, e.g. "E"
    """
    apply_style()
    width_mm, height_mm = figure_size_mm(width, height_mm, journal)

    fig, axes = plt.subplot_mosaic(layout, figsize=(mm2in(width_mm), mm2in(height_mm)),
                                   width_ratios=width_ratios, height_ratios=height_ratios,
                                   layout="constrained")
    pad = mm2in(space_mm)
    fig.get_layout_engine().set(w_pad=pad, h_pad=pad, wspace=0, hspace=0)

    for name in placeholders:
        axes[name].set_axis_off()
    if letters is True:
        letters = list(axes)
    for name in letters or []:
        add_panel_letter(axes[name], name)
    return fig, axes


def add_panel_letter(ax, letter):
    """Bold uppercase letter just above the top-left corner of the panel's full area
    (axes plus tick labels, axis labels and title), so it never overlaps the axis.
    The position is worked out at draw time, after constrained_layout has placed everything."""
    font = _first_font(LETTER_FONT)
    if font is None:
        warnings.warn("Times New Roman not found; panel letters use a generic serif.")

    def panel_box(renderer):            # axes + axis decorations + titles (legends etc. sit inside the axes)
        parts = [ax.get_window_extent(renderer)]
        if ax.axison:
            parts += [axis.get_tightbbox(renderer) for axis in (ax.xaxis, ax.yaxis)]
        parts += [t.get_window_extent(renderer) for t in (ax.title, ax._left_title, ax._right_title)
                  if t.get_visible() and t.get_text()]
        return Bbox.union([b for b in parts if b is not None and b.width and b.height])

    dx, dy = LETTER_OFFSET_MM
    ax.annotate(letter.upper(), xy=(0, 1), xycoords=panel_box,
                       xytext=(dx * 72 / 25.4, dy * 72 / 25.4), textcoords="offset points",
                       ha="left", va="bottom", fontsize=SIZE_PT["letter"], fontweight="bold",
                       family=font or "serif")


def save_figure(fig, path, png=False):
    """Save a vector PDF at exactly the figure size (plus an optional 600 dpi PNG)."""
    path = Path(path).with_suffix(".pdf")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, transparent=True)    # never bbox_inches="tight": it changes the size
    if png:
        fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI, transparent=True)

    want = fig.get_size_inches() * 25.4
    got = pdf_size_mm(path)
    print(f"Saved {path}: {got[0]:.1f} x {got[1]:.1f} mm (requested {want[0]:.1f} x {want[1]:.1f} mm)")
    if abs(got[0] - want[0]) > 0.1 or abs(got[1] - want[1]) > 0.1:
        warnings.warn("Saved PDF size does not match the requested size.")
    return path


def pdf_size_mm(path):
    """Page size (width, height) in mm, read from the PDF's MediaBox."""
    box = re.search(rb"/MediaBox\s*\[([^\]]+)\]", Path(path).read_bytes())
    x0, y0, x1, y1 = map(float, box.group(1).split())
    return (x1 - x0) * 25.4 / 72, (y1 - y0) * 25.4 / 72
