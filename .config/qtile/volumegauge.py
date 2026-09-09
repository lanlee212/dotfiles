"""Volume gauge for the qtile bar, styled like ALSAWidget — pactl-backed.

Works on the image where pyalsaaudio isn't available in Fedora. Shows a
filled bar + percent text (or X when muted), level-coloured.
"""

import re
import subprocess

from libqtile import bar
from libqtile.widget import base

from qtile_extras.widget.mixins import ProgressBarMixin

_RE_PERCENT = re.compile(r"(\d+)%")


class VolumeGauge(base._Widget, ProgressBarMixin):
    defaults = [
        ("update_interval", 2, "Poll interval (seconds)."),
        ("limit_normal", 70, "Max percent drawn normal."),
        ("limit_high", 90, "Max percent drawn high."),
        ("colour_normal", "#98c379", "Bar colour: normal."),
        ("colour_high", "#e5c07b", "Bar colour: high."),
        ("colour_loud", "#e06c75", "Bar colour: loud."),
        ("colour_mute", "#5c6370", "Bar colour: muted."),
    ]

    def __init__(self, **config):
        base._Widget.__init__(self, bar.CALCULATED, **config)
        self.add_defaults(self.defaults)
        ProgressBarMixin.__init__(self)
        self.add_defaults(ProgressBarMixin.defaults)

    def _pactl(self, args):
        try:
            return subprocess.check_output(
                ["pactl"] + args, stderr=subprocess.DEVNULL, timeout=2
            ).decode()
        except Exception:
            return ""

    def _read(self):
        """(percent, muted) from the default sink."""
        vol = self._pactl(["get-sink-volume", "@DEFAULT_SINK@"])
        m = _RE_PERCENT.search(vol)
        percent = int(m.group(1)) if m else 0
        muted = "yes" in self._pactl(["get-sink-mute", "@DEFAULT_SINK@"])
        return percent, muted

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        percent, muted = self._read()
        if muted or percent == 0:
            colour = self.colour_mute
            text = "X"
        else:
            if percent <= self.limit_normal:
                colour = self.colour_normal
            elif percent <= self.limit_high:
                colour = self.colour_high
            else:
                colour = self.colour_loud
            text = f"{percent}%"
        self.draw_bar(
            bar_value=percent / 100.0,
            bar_colour=colour,
            bar_text=text,
            bar_text_foreground=self.bar_text_foreground,
        )
        self.draw_at_default_position()

    def calculate_length(self):
        return self.bar_width + 2 * getattr(self, "padding", 3)

    def refresh(self):
        """Redraw now (also called from keybinds for instant feedback)."""
        self.draw()
        self.bar.draw()
        self.timeout_add(self.update_interval, self._refresh)

    def _refresh(self):
        self.draw()
        self.bar.draw()
        self.timeout_add(self.update_interval, self._refresh)

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        self.timeout_add(self.update_interval, self._refresh)
