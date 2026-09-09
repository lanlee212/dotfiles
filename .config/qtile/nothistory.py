"""
Qtile notification-history widget popup.

Click the bell in the bar -> themed popup listing dunst's history
(the last notifications, newest first, paged). Up/Down navigate,
Enter or click re-pops a notification via `dunstctl history-pop <id>`.
Esc closes.

Usage in config.py:
    from nothistory import HistoryPopup, bell_text

    def show_notif_history(qtile):
        HistoryPopup(qtile, colors=colors, font="Cantarell",
                     fontsize=12).show(centered=True, qtile=qtile)

    widget.GenPollText(
        func=bell_text, update_interval=15,
        mouse_callbacks={"Button1": lazy.function(show_notif_history)},
    ),
"""

import json
import subprocess

import xcffib.xproto as xproto
from libqtile.backend.x11.xkeysyms import keysyms
from qtile_extras.popup.toolkit import PopupRelativeLayout, PopupText

_ROWS = 8
_MAX_LABEL = 48
_BELL = "\U0001F514"  # bell emoji


def _history_entries():
    """dunst history as list of dicts {id, appname, summary, body, ts}, newest first."""
    try:
        out = subprocess.check_output(["dunstctl", "history"], timeout=3)
        data = json.loads(out.decode())["data"]
        notifs = data[0] if data else []
    except Exception:
        return []

    def g(n, key):
        v = n.get(key, {})
        return v.get("data", "") if isinstance(v, dict) else v

    entries = []
    for n in notifs:
        try:
            entries.append(
                {
                    "id": int(g(n, "id")),
                    "appname": str(g(n, "appname")),
                    "summary": str(g(n, "summary")),
                    "ts": int(g(n, "timestamp")),
                }
            )
        except Exception:
            continue
    entries.sort(key=lambda e: -e["ts"])
    return entries


def bell_text():
    """Bar label: bell + number of notifications in history."""
    try:
        entries = _history_entries()
        return f"  {_BELL} {len(entries)}  " if entries else f"  {_BELL}  "
    except Exception:
        return f"  {_BELL}  "


class HistoryPopup(PopupRelativeLayout):
    """Paged, keyboard-navigable list of recent notifications."""

    def __init__(self, qtile, colors, font, fontsize, rows=_ROWS):
        self.colors = colors
        self.font = font
        self.fontsize = fontsize
        self.rows_n = rows
        self.entries = _history_entries()
        self.selected = 0

        labels, title = self._layout()

        self.title = PopupText(
            text=title,
            pos_x=0.02,
            pos_y=0.02,
            width=0.96,
            height=0.08,
            font=self.font,
            fontsize=self.fontsize,
            foreground=colors[6],
            h_align="left",
        )
        self.rows = [
            PopupText(
                text=labels[i],
                pos_x=0.02,
                pos_y=0.12 + i * 0.105,
                width=0.96,
                height=0.09,
                font=self.font,
                fontsize=self.fontsize,
                foreground=colors[1],
                foreground_highlighted=colors[0],
                highlight=colors[6],
                h_align="left",
            )
            for i in range(rows)
        ]

        super().__init__(
            qtile,
            width=380,
            height=50 + rows * 44,
            controls=[self.title] + self.rows,
            background=colors[0],
            border=colors[2],
            border_width=1,
            opacity=0.96,
            keyboard_navigation=True,
            initial_focus=None,
        )

        if self.rows and self.entries:
            self.rows[0]._highlight = True

    # ---------------------------------------------------------------- layout

    def _layout(self):
        """(row_labels, title) for the current selection/page. Safe pre-show."""
        if not self.entries:
            return [""] * self.rows_n, "No notifications in history"

        page = self.selected // self.rows_n
        pages = max(1, -(-len(self.entries) // self.rows_n))
        start = page * self.rows_n
        labels = []
        for i in range(self.rows_n):
            idx = start + i
            if idx < len(self.entries):
                e = self.entries[idx]
                label = f"  {e['appname']}: {e['summary']}" if e["appname"] else f"  {e['summary']}"
                labels.append(label[:_MAX_LABEL])
            else:
                labels.append("")
        title = f"History ({len(self.entries)}) — page {page + 1}/{pages}"
        return labels, title

    def _refresh(self):
        labels, title = self._layout()
        self.title.text = title
        start = (self.selected // self.rows_n) * self.rows_n
        for i, row in enumerate(self.rows):
            row.text = labels[i]
            if start + i == self.selected and self.entries:
                row.focus()
            else:
                row.unfocus()
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
        self._refresh()

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
        elif keycode == k["up"]:
            if self.entries:
                self.selected = (self.selected - 1) % len(self.entries)
                self._refresh()
        elif keycode in (k["down"], k["tab"]):
            if self.entries:
                self.selected = (self.selected + 1) % len(self.entries)
                self._refresh()
        elif keycode == k["return"]:
            self._pop_selected()

    def process_button_click(self, x, y, button):
        if not self.entries:
            return
        start = (self.selected // self.rows_n) * self.rows_n
        for i, row in enumerate(self.rows):
            if row.mouse_in_control(x, y) and start + i < len(self.entries):
                self.selected = start + i
                self._pop_selected()
                return

    # --------------------------------------------------------------- actions

    def _pop_selected(self):
        if not self.entries:
            return
        entry = self.entries[self.selected]
        try:
            subprocess.Popen(["dunstctl", "history-pop", str(entry["id"])])
        except Exception:
            pass
        self.entries = _history_entries()
        if not self.entries:
            self.kill()
        else:
            self.selected = min(self.selected, len(self.entries) - 1)
            self._refresh()
