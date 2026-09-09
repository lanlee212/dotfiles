"""
Qtile-native application launcher (rofi-style).

Keyboard-driven popup launcher that:
  - scans .desktop files (system + user + flatpak exports)
  - filters by name / exec as you type (exact > prefix > substring > fuzzy)
  - falls back to running any command found in PATH inside the
    terminal defined in config.py (e.g. "htop")
  - themed from config.py (colors module + font settings)

Usage in config.py:
    from launcher import AppLauncher

    def show_app_launcher(qtile):
        AppLauncher(qtile, colors=colors, font="Cantarell",
                    fontsize=12, terminal=terminal).show(centered=True, qtile=qtile)

    Key([mod], "d", lazy.function(show_app_launcher), desc="App launcher"),
"""

import configparser
import json
import os
import re
import shutil
import time

import xcffib.xproto as xproto
from qtile_extras.popup.toolkit import PopupRelativeLayout, PopupText
from libqtile.backend.x11.xkeysyms import keysyms


class _App:
    """A launchable entry."""

    __slots__ = ("name", "exec", "terminal", "is_cmd")

    def __init__(self, name, exec_, terminal=False, is_cmd=False):
        self.name = name
        self.exec = exec_
        self.terminal = terminal
        self.is_cmd = is_cmd


_FIELD_CODE = re.compile(r"\s*%[a-zA-Z]")


def _clean_exec(exec_line):
    """Strip desktop-entry field codes (%U %F %f etc.) and stray quotes."""
    exec_line = _FIELD_CODE.sub("", exec_line).strip()
    return exec_line.strip('"')


def _match_score(q, s):
    """Match tier of q against s: 0=exact, 1=prefix, 2=substring,
    3=subsequence (letters in order, gaps allowed). None = no match."""
    if q == s:
        return 0
    if s.startswith(q):
        return 1
    if q in s:
        return 2
    it = iter(s)
    if all(c in it for c in q):
        return 3
    return None


_DESKTOP_DIRS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications"),
    "/var/lib/flatpak/exports/share/applications",
    os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
]

_cache = {"t": 0.0, "apps": []}

_MRU_PATH = os.path.expanduser("~/.local/share/qtile/launcher_mru.json")
_MRU_MAX = 30


def _load_mru():
    """Load most-recently-used timestamps {exec: epoch}."""
    try:
        with open(_MRU_PATH) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_mru(mru):
    """Persist the MRU dict, keeping only the newest entries."""
    if len(mru) > _MRU_MAX:
        for k in sorted(mru, key=mru.get)[: len(mru) - _MRU_MAX]:
            del mru[k]
    try:
        os.makedirs(os.path.dirname(_MRU_PATH), exist_ok=True)
        with open(_MRU_PATH, "w") as f:
            json.dump(mru, f)
    except Exception:
        pass


def _load_apps():
    """Scan .desktop files, caching for 30s."""
    global _cache
    if _cache["apps"] and (time.time() - _cache["t"]) < 30:
        return _cache["apps"]

    apps, seen = [], set()
    for d in _DESKTOP_DIRS:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".desktop"):
                continue
            path = os.path.join(d, f)
            try:
                cp = configparser.ConfigParser(interpolation=None)
                cp.read(path)
                if "Desktop Entry" not in cp:
                    continue
                e = cp["Desktop Entry"]
                if e.get("Type", "Application") != "Application":
                    continue
                if e.getboolean("NoDisplay", False) or e.getboolean("Hidden", False):
                    continue
                name = e.get("Name", "").strip()
                exec_ = _clean_exec(e.get("Exec", ""))
                if not name or not exec_ or name in seen:
                    continue
                seen.add(name)
                apps.append(
                    _App(
                        name,
                        exec_,
                        terminal=e.getboolean("Terminal", False),
                    )
                )
            except Exception:
                continue

    apps.sort(key=lambda a: a.name.lower())
    _cache = {"t": time.time(), "apps": apps}
    return apps


class AppLauncher(PopupRelativeLayout):
    """Rofi-style app launcher popup."""

    def __init__(self, qtile, colors, font, fontsize, terminal, max_rows=8):
        self.colors = colors
        self.font = font
        self.fontsize = fontsize
        self.terminal = terminal
        self.max_rows = max_rows

        self.query = ""
        self.apps = _load_apps()
        self.mru = _load_mru()
        self.results = self._filter()
        self.selected = 0

        # Seed row text from the initial (empty-query) results. The text
        # setter needs a configured layout, so we pass text via constructors
        # here and only touch .text after the popup has been shown.
        names = [f"  {a.name}" for a in self.results]
        names += [""] * max(0, max_rows - len(names))

        self.input_box = PopupText(
            text="> ",
            pos_x=0.02,
            pos_y=0.02,
            width=0.96,
            height=0.1,
            font=self.font,
            fontsize=self.fontsize,
            foreground=colors[6],
            h_align="left",
        )

        self.rows = [
            PopupText(
                text=names[i],
                pos_x=0.02,
                pos_y=0.14 + i * 0.1,
                width=0.96,
                height=0.09,
                font=self.font,
                fontsize=self.fontsize,
                foreground=colors[1],
                foreground_highlighted=colors[0],
                highlight=colors[6],
                h_align="left",
            )
            for i in range(max_rows)
        ]

        super().__init__(
            qtile,
            width=760,
            height=60 + max_rows * 44,
            controls=[self.input_box] + self.rows,
            background=colors[0],
            border=colors[2],
            border_width=1,
            opacity=0.96,
            keyboard_navigation=True,
            initial_focus=None,
        )

        # Initial selection highlight (draw happens on show())
        if self.rows:
            self.rows[0]._highlight = True

    # ------------------------------------------------------- keyboard grab

    def show(self, *args, **kwargs):
        """Show the launcher and grab the keyboard so all keys reach it."""
        super().show(*args, **kwargs)
        # Active keyboard grab: route every key to the popup regardless of
        # X input focus. Without this, a window behind the popup steals
        # focus (and with it, the keystrokes).
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

    def kill(self):
        """Release the keyboard grab, then close the launcher."""
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
        elif keycode == k["backspace"]:
            self.query = self.query[:-1]
            self._update()
        elif keycode == k["return"]:
            self._launch_selected()
        elif keycode == k["up"]:
            self.selected = max(0, self.selected - 1)
            self._draw_rows()
        elif keycode == k["down"]:
            self.selected = min(len(self.results) - 1, self.selected + 1)
            self._draw_rows()
        elif keycode == k["tab"]:
            n = max(1, len(self.results))
            self.selected = (self.selected + 1) % n
            self._draw_rows()
        elif 0x20 <= keycode <= 0x7E:
            self.query += chr(keycode)
            self._update()

    def process_button_click(self, x, y, button):
        for i, row in enumerate(self.rows):
            if row.mouse_in_control(x, y) and i < len(self.results):
                self.selected = i
                self._launch_selected()
                return

    # -------------------------------------------------------------- actions

    def _filter(self):
        q = self.query.strip().lower()
        if not q:
            # Most-recently-used first, then alphabetical
            apps = sorted(
                self.apps,
                key=lambda a: (-self.mru.get(a.exec, 0), a.name.lower()),
            )
            return apps[: self.max_rows]

        # Fuzzy matching with tiers: exact > prefix > substring > subsequence.
        # Name matches always rank above exec matches; within each group,
        # order by match quality, then MRU recency, then alphabetical.
        name, exe = [], []
        for a in self.apps:
            sc = _match_score(q, a.name.lower())
            if sc is not None:
                name.append((sc, a))
            else:
                ec = _match_score(q, a.exec.lower())
                if ec is not None:
                    exe.append((ec, a))

        mru_key = lambda t: (t[0], -self.mru.get(t[1].exec, 0), t[1].name.lower())
        name.sort(key=mru_key)
        exe.sort(key=mru_key)

        res = [a for _, a in (name + exe)][: self.max_rows]

        # Command fallback: "htop" with no .desktop entry -> run in terminal
        cmd = q.split()[0]
        if cmd and shutil.which(cmd) and len(res) < self.max_rows:
            if not any(a.exec == cmd for a in res):
                res.append(_App(name=f"Run: {q}", exec_=q, terminal=True, is_cmd=True))
        return res

    def _launch_selected(self):
        if not self.results or self.selected >= len(self.results):
            self.kill()
            return
        app = self.results[self.selected]
        # Record in MRU (skip ephemeral "Run:" command entries)
        if not app.is_cmd:
            self.mru[app.exec] = time.time()
            _save_mru(self.mru)
        if app.is_cmd or app.terminal:
            self.qtile.spawn(f"{self.terminal} -e {app.exec}")
        else:
            self.qtile.spawn(app.exec)
        self.kill()

    # ---------------------------------------------------------------- draw

    def _update(self):
        self.results = self._filter()
        self.selected = 0
        self.input_box.text = f"> {self.query}"
        self._draw_rows()

    def _draw_rows(self):
        for i, row in enumerate(self.rows):
            if i < len(self.results):
                row.text = f"  {self.results[i].name}"
                if i == self.selected:
                    row.focus()
                else:
                    row.unfocus()
            else:
                row.text = ""
                row.unfocus()
        self.draw()
