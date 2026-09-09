"""
Qtile power menu (Mod+Shift+Q).

OneDark-themed popup with Lock / Sleep / Shutdown actions.
Left/Right select, Return activates, Esc closes; click works too.

Usage in config.py:
    from power_menu import PowerMenu

    def show_power_menu(qtile):
        PowerMenu(qtile, colors=colors, font=widget_defaults["font"],
                  fontsize=widget_defaults["fontsize"]).show(centered=True, qtile=qtile)

    Key([mod, "shift"], "q", lazy.function(show_power_menu)),
"""

import xcffib.xproto as xproto
from libqtile.backend.x11.xkeysyms import keysyms
from qtile_extras.popup.toolkit import PopupRelativeLayout, PopupText

_ICON_FONT = "Symbols Nerd Font"

# Icons: Nerd Font codepoints (lock U+F023, moon U+F186, power-off U+F011).
# cmd None -> qtile.shutdown() (quit session back to the login screen).
_ACTIONS = [
    {"icon": "\uf023", "label": "Lock", "cmd": "betterlockscreen -l"},
    {"icon": "\uf186", "label": "Sleep", "cmd": "systemctl suspend"},
    {"icon": "\uf011", "label": "Shutdown", "cmd":"systemctl poweroff"},
]

_ICON_X = (0.10, 0.44, 0.78)
_ICON_Y = 0.12
_ICON_W = 0.12
_ICON_H = 0.45
_LABEL_Y = 0.62


class PowerMenu(PopupRelativeLayout):
    """Three-button power menu, keyboard and mouse driven."""

    def __init__(self, qtile, colors, font, fontsize):
        self.colors = colors
        self.font = font
        self.fontsize = fontsize
        self.selected = 0

        self.icons = []
        self.labels = []
        controls = []
        for i, a in enumerate(_ACTIONS):
            danger = i == 2  # shutdown gets the red highlight
            hl = colors[3] if danger else colors[6]
            icon = PopupText(
                text=a["icon"],
                pos_x=_ICON_X[i],
                pos_y=_ICON_Y,
                width=_ICON_W,
                height=_ICON_H,
                font=_ICON_FONT,
                fontsize=int(fontsize * 2.4),
                foreground=colors[1],
                foreground_highlighted=colors[0],
                highlight=hl,
                h_align="center",
            )
            label = PopupText(
                text=a["label"],
                pos_x=_ICON_X[i] - 0.04,
                pos_y=_LABEL_Y,
                width=0.2,
                height=0.18,
                font=self.font,
                fontsize=self.fontsize,
                foreground=colors[1],
                foreground_highlighted=colors[0],
                highlight=hl,
                h_align="center",
            )
            self.icons.append(icon)
            self.labels.append(label)
            controls += [icon, label]

        super().__init__(
            qtile,
            width=640,
            height=190,
            controls=controls,
            background=colors[0],
            border=colors[2],
            border_width=1,
            opacity=0.96,
            keyboard_navigation=True,
            initial_focus=None,
        )

        if self.icons:
            self.icons[0]._highlight = True

    # ---------------------------------------------------------------- draw

    def _draw(self):
        for i, (icon, label) in enumerate(zip(self.icons, self.labels)):
            if i == self.selected:
                icon.focus()
                label.focus()
            else:
                icon.unfocus()
                label.unfocus()
        self.draw()

    # ---------------------------------------------------------------- show

    def show(self, *args, **kwargs):
        super().show(*args, **kwargs)
        try:
            self.popup.win.conn.conn.core.GrabKeyboard(
                owner_events=False,
                grab_window=self.popup.win.window.wid,
                time=xproto.Time.CurrentTime,
                pointer_mode=xproto.GrabMode.Async,
                keyboard_mode=xproto.GrabMode.Async,
            )
        except Exception:
            pass
        self._draw()

    def kill(self):
        try:
            self.popup.win.conn.conn.core.UngrabKeyboard(xproto.Time.CurrentTime)
        except Exception:
            pass
        super().kill()

    # ---------------------------------------------------------------- input

    def process_key_press(self, keycode):
        k = keysyms
        if keycode == k["escape"]:
            self.kill()
        elif keycode == k["left"]:
            self.selected = (self.selected - 1) % len(_ACTIONS)
            self._draw()
        elif keycode == k["right"]:
            self.selected = (self.selected + 1) % len(_ACTIONS)
            self._draw()
        elif keycode == k["return"]:
            self._activate(self.selected)

    def process_button_click(self, x, y, button):
        for i in range(len(_ACTIONS)):
            if self.icons[i].mouse_in_control(x, y) or self.labels[i].mouse_in_control(x, y):
                self.selected = i
                self._activate(i)
                return

    # -------------------------------------------------------------- actions

    def _activate(self, i):
        action = _ACTIONS[i]
        self.kill()
        if action["cmd"]:
            self.qtile.spawn(action["cmd"])
        else:
            self.qtile.shutdown()
