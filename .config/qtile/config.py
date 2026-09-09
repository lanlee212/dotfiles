import glob
import os
import subprocess
from libqtile import bar, layout, qtile
from qtile_extras import widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen,ScratchPad, DropDown
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile import hook
from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupImage,
    PopupText )
from battery import BatteryGauge
from launcher import AppLauncher
from nothistory import HistoryPopup, bell_text
from power_menu import PowerMenu
from volumegauge import VolumeGauge
import colors

# set color theme form colors.py 
colors = colors.OneDark

# battery gauge only exists on machines that have one (laptops)
_has_battery = bool(glob.glob("/sys/class/power_supply/BAT*"))
_battery_gauge = BatteryGauge(
    bar_text_foreground=colors[2],
    colour_low=colors[3],
    colour_mid=colors[5],
    colour_high=colors[4],
) if _has_battery else None

def vol_set(qtile, op):
    """Change volume + refresh the gauge instantly (no poll lag)."""
    qtile.spawn(f"pactl set-sink-volume @DEFAULT_SINK@ {op}")
    gauge = qtile.widgets_map.get("volumegauge")
    if gauge:
        gauge.refresh()


def vol_toggle_mute(qtile):
    """Toggle mute + refresh the gauge instantly."""
    qtile.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")
    gauge = qtile.widgets_map.get("volumegauge")
    if gauge:
        gauge.refresh()


@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.run([home])

def show_app_launcher(qtile):
    """Rofi-style app launcher popup, themed from config.py."""
    AppLauncher(
        qtile,
        colors=colors,
        font=widget_defaults["font"],
        fontsize=widget_defaults["fontsize"],
        terminal=terminal,
    ).show(centered=True, qtile=qtile)

def show_notif_history(qtile):
    """Notification history popup, themed from config.py — just above the bar,
    right-aligned with the bar's right edge."""
    popup = HistoryPopup(
        qtile,
        colors=colors,
        font=widget_defaults["font"],
        fontsize=widget_defaults["fontsize"],
    )
    bar = qtile.current_screen.bottom
    m = bar.margin
    m = m[1] if isinstance(m, (list, tuple)) else m  # right margin
    popup.show(
        x=qtile.current_screen.width - popup.width - m,
        y=qtile.current_screen.height - bar.size - m - popup.height - 4,
        qtile=qtile,
    )


def show_power_menu(qtile):
    """Power menu popup, themed from config.py."""
    PowerMenu(
        qtile,
        colors=colors,
        font=widget_defaults["font"],
        fontsize=widget_defaults["fontsize"],
    ).show(centered=True, qtile=qtile)


mod = "mod4"
terminal = "ghostty"

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    #Special Function Keys
    Key([mod], "left", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "right", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "down", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "up", lazy.layout.up(), desc="Move focus up"),
    Key([], "XF86AudioMute", lazy.function(vol_toggle_mute),),
    Key([], "XF86AudioRaiseVolume", lazy.function(vol_set, "+5%"),),
    Key([], "XF86AudioLowerVolume", lazy.function(vol_set, "-5%"),),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set +5%"),),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 5%-"),),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    Key([mod, "shift"], "n",  lazy.spawn ("brave-origin --incognito"),),
    # Move windows between left/right columns or move up/down in current stack.
	# Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "left", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "right", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "up", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "left", lazy.layout.shrink_main(), desc="Grow window to the left"),
    Key([mod, "control"], "right", lazy.layout.grow_main(), desc="Grow window to the right"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(), desc="Toggle between split and unsplit sides of stack",),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"), 
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "shift"], "q", lazy.function(show_power_menu)),
    Key([mod], "f", lazy.window.toggle_fullscreen(),desc="Toggle fullscreen on the focused window",),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "d", lazy.function(show_app_launcher), desc="App launcher"),
    Key([mod], "grave", lazy.function(show_notif_history), desc="Notification history"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([mod], "l", lazy.spawn("systemctl suspend"), desc="Lock Screen"),
    Key([], "Print", lazy.spawn("scrot -u '%Y-%m-%d-%T.png' -e 'mv $f ~/Pictures/'")),

    ]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )

groups = [Group (i) for i in "12345"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
    ])
# scratch pad and key binds below
groups.append(
    ScratchPad("scratchpad", [
        DropDown('terminal',terminal, match=Match(wm_class='com.mitchellh.ghostty'),height = 0.45,width = 0.8,x = 0.1,y = 0.01,on_focus_lost_hide = False, warp_pointer = False, ),
        # DropDown('fm','thunar',height = 0.8,width = 0.8,x = 0.1,y = 0.1,on_focus_lost_hide = False, warp_pointer = False, ),
        DropDown('fm','nemo',height = 0.8,width = 0.8,x = 0.1,y = 0.1,on_focus_lost_hide = False, warp_pointer = False, ),
        DropDown('sol','sol',height = 0.5,width = 0.5,x = 0.25,y = 0.3,on_focus_lost_hide = True, warp_pointer = False, ),
        DropDown('gam','faugus-launcher',x = 0.4,y = 0.2,on_focus_lost_hide = True, warp_pointer = False, ),
    ]),
)
keys.extend(
    [
        Key([], 'F12', lazy.group['scratchpad'].dropdown_toggle('terminal')),
        Key([mod], 'a', lazy.group['scratchpad'].dropdown_toggle('fm')),
        Key([mod], 'w', lazy.group['scratchpad'].dropdown_toggle('sol')),
        Key([mod], 'g', lazy.group['scratchpad'].dropdown_toggle('gam')),
    
    ]
)



# layout defaults 
layout_theme = {"border_width": 1,
                "margin": 10,
                "border_focus": colors[8],
                "border_normal": colors[0]
                }

layouts = [
    # layout.Columns(**layout_theme),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    layout.MonadTall(**layout_theme),
    layout.Max(**layout_theme ),
    layout.MonadThreeCol(**layout_theme),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]


widget_defaults = dict(
    font="Cantarell",
    fontsize=12,
    padding=3,
    boarder=1,
    foreground=colors[1],
    background=colors[0],
    active=colors[1],
    inactive=colors[2],
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
         bottom=bar.Bar(
            [
                widget.GroupBox(this_current_screen_border = colors[6], urgent_border = colors[3], urgent_text = colors[6] ),
                widget.CurrentLayoutIcon (scale = 0.55),
                widget.Prompt(),
                #widget.WindowName(),
                #widget.WindowTabs(),
                widget.TaskList (border = colors[6]),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                VolumeGauge(update_interval=2, bar_text_foreground=colors[2], colour_normal=colors[4], colour_high=colors[5], colour_loud=colors[3], mouse_callbacks={"Button1": lazy.function(vol_toggle_mute)}),
                *([_battery_gauge] if _has_battery else []),
                #widget.StatusNotifier(icon_size = 16, icon_theme ="Papirus-Dark"),
                widget.Systray(icon_size = 16,icon_theme ="Papirus-Dark"),
                widget.GenPollText(func=bell_text, update_interval=15, mouse_callbacks={"Button1": lazy.function(show_notif_history)}, foreground=colors[1]),
                widget.Clock(format="%Y-%m-%d %a %I:%M %p"),
            ],
            30,
            #border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            #border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
            margin = [0,10,10,10],
            background = colors[0],
        
        ),
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        x11_drag_polling_rate = 60,
        wallpaper='~/.config/qtile/background.png',
        wallpaper_mode='stretch',

   ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    border_focus = colors[7],
    border_normal = colors[1],
    border_width = 1,
    margin = 10, 
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class="thunar"),
        Match(wm_class="megasync"),
        Match(wm_class="sol"),
        Match(wm_class="pop-up"),
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
