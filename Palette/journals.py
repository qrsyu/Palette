"""Figure sizes for each journal, in mm.

To add a journal, add one line to JOURNALS: its name, then its width names and values.
Widths are from each journal's figure guidelines (checked Oct 2026).
"""
import warnings

JOURNALS = {
    "nature":  {"single": 89, "full": 183},
    "science": {"single": 57, "double": 121, "full": 184},
    "cell":    {"single": 85, "full": 174},   # Cell, Neuron
}
DEFAULT_JOURNAL = "nature"     # used when make_figure is not given a journal
MAX_HEIGHT_MM = 170            # warn if taller (Nature's limit; leaves room for the legend)


def figure_size_mm(width="full", height_mm=100, journal=DEFAULT_JOURNAL):
    """Return (width, height) in mm. `width` is a width name for that journal, or a number in mm."""
    widths = JOURNALS[journal]
    if isinstance(width, str) and width not in widths:
        raise ValueError(f"{journal} has no width '{width}'. Use one of {list(widths)} or a number in mm.")
    if height_mm > MAX_HEIGHT_MM:
        warnings.warn(f"Figure height {height_mm} mm is over the {MAX_HEIGHT_MM} mm maximum.")
    return widths.get(width, width), height_mm
