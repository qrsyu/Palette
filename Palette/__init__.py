"""Palette: colours and journal-figure layout.

import Palette
Palette.load_color(1, 5)
fig, ax = Palette.make_figure("AB;CD", height_mm=100)
Palette.save_figure(fig, "fig1")
"""
from .colors import RAMPS, load_color
from .journals import JOURNALS, figure_size_mm
from .figure import mm2in, apply_style, make_figure, add_panel_letter, save_figure, pdf_size_mm
