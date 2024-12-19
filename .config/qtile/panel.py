import os

from libqtile import qtile
from libqtile.configs import PanelConfig, Panel

class MyPanel(Panel):
    defaults = [
        ("width", 200),
        ("height", 20),
        ("x", 0),
        ("y", 0)
    ]

    def __init__(self):
        super().__init__()

    def resize(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def widget(self):
        return os.system("dmenu -l 20")

panel = MyPanel()