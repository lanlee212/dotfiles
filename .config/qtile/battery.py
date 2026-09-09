"""Battery gauge for the qtile bar, styled like the ALSAWidget volume gauge
(filled bar + percent text, level-coloured).

Renders nothing when no battery is present (/sys/class/power_supply/BAT*
missing); config.py also only adds the widget to the bar when a battery
exists, so desktops never see it.
"""

import glob

from libqtile import bar
from libqtile.widget import base

from qtile_extras.widget.mixins import ProgressBarMixin


class BatteryGauge(base._Widget, ProgressBarMixin):
    defaults = [
        ("update_interval", 30, "Battery poll interval (seconds)."),
        ("limit_low", 20, "Max percent drawn red (critical)."),
        ("limit_mid", 40, "Max percent drawn yellow (mid)."),
        ("colour_low", "#e06c75", "Bar colour: critical."),
        ("colour_mid", "#e5c07b", "Bar colour: mid."),
        ("colour_high", "#98c379", "Bar colour: healthy."),
    ]

    def __init__(self, **config):
        base._Widget.__init__(self, bar.CALCULATED, **config)
        self.add_defaults(self.defaults)
        ProgressBarMixin.__init__(self)
        self.add_defaults(ProgressBarMixin.defaults)

    def _read(self):
        """(percent, charging) or None when no battery is present."""
        bats = sorted(glob.glob("/sys/class/power_supply/BAT*"))
        if not bats:
            return None
        try:
            with open(f"{bats[0]}/capacity") as f:
                cap = int(f.read().strip())
            with open(f"{bats[0]}/status") as f:
                status = f.read().strip()
        except (OSError, ValueError):
            return None
        return cap, status in ("Charging", "Full")

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        data = self._read()
        if data is None:
            # no battery: render nothing
            self.draw_at_default_position()
            return
        percent, charging = data
        if percent <= self.limit_low:
            colour = self.colour_low
        elif percent <= self.limit_mid:
            colour = self.colour_mid
        else:
            colour = self.colour_high
        text = f"\u26a1 {percent}%" if charging else f"{percent}%"
        self.draw_bar(
            bar_value=percent / 100.0,
            bar_colour=colour,
            bar_text=text,
            bar_text_foreground=self.bar_text_foreground,
        )
        self.draw_at_default_position()

    def calculate_length(self):
        return self.bar_width + 2 * getattr(self, "padding", 3)

    def _refresh(self):
        self.draw()
        self.bar.draw()
        self.timeout_add(self.update_interval, self._refresh)

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        self.timeout_add(self.update_interval, self._refresh)
