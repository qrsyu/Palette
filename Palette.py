"""Paper palette. idx: 0 grey, 1 blue, 2 rose, 3 olive, 4 amber.

pal = Palette()
pal.load_color(1, 5)           -> 5 hex colors, light -> dark
pal.load_color([1, 4], 3)      -> 7 hex colors: blue (dark -> light), neutral, amber (light -> dark)
pal.load_color(1, np.inf)      -> continuous Colormap (sequential)
pal.load_color([1, 4], np.inf) -> continuous Colormap (diverging)
"""
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_hex


class Palette:
    # Light -> dark, evenly spaced in perceived lightness (OKLab L 0.97 -> 0.26; grey -> 0.18).
    RAMPS = {
        0: ["#f5f5f5", "#d4d4d4", "#b5b5b5", "#969696", "#797979", "#5c5c5c", "#424242", "#282828", "#121212"],
        1: ["#f1f6fc", "#c4daf7", "#97bef1", "#68a2eb", "#3785e2", "#226abe", "#125197", "#08396f", "#032349"],
        2: ["#fbf2f6", "#f2cbdc", "#e8a4c3", "#db7cab", "#cb5293", "#a93c77", "#85295c", "#621a42", "#400e2a"],
        3: ["#f4f6ef", "#d3ddbb", "#b4c486", "#96ab4b", "#7a9000", "#627402", "#4b5903", "#354001", "#202800"],
        4: ["#faf4ee", "#eed2b8", "#e2b081", "#d48e43", "#bc7000", "#985a05", "#754504", "#553000", "#371d00"],
    }
    NEUTRAL = "#ffffff"   # centre of diverging maps
    START = 0.29            # discrete lines skip the near-white end so they stay visible on white paper

    def load_color(self, idx=0, length=5):
        if np.ndim(idx) == 0:                                   # sequential
            cmap = LinearSegmentedColormap.from_list(f"seq{idx}", self.RAMPS[idx])
            t = np.linspace(self.START, 1, int(length)) if np.isfinite(length) else None
        else:                                                   # diverging [neg, pos]
            a, b = idx
            cmap = LinearSegmentedColormap.from_list(f"div{a}{b}", self.RAMPS[a][::-1] + [self.NEUTRAL] + self.RAMPS[b])
            t = np.linspace(0, 1, 2*int(length)+1) if np.isfinite(length) else None
        return cmap if t is None else [to_hex(c) for c in cmap(t)]