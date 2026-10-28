-- ============================================================
--  Hyprland Lua configuration  (0.56, per wiki.hypr.land docs)
--  qtile/mango parity, OneDark, NO rounded corners.
--  Mirrored from ~/.config/qtile/config.py (qtile-parity keymap)
--  Shell: Noctalia (bar/launcher/session/OSD/notifications/wallpaper)
-- ============================================================

------------------ MONITORS ------------------
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "1",
})

------------------ ENVIRONMENT ------------------
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XDG_MENU_PREFIX", "gnome-")

------------------ AUTOSTART ------------------
-- (qtile autostart minus picom/dunst/xautolock: Noctalia owns those now)
-- Wrapped in `uwsm app --` so each one runs in its own systemd user scope:
-- journal logging, proper cgroup teardown at logout. `uwsm app` also works
-- from the plain non-uwsm "Hyprland" session entry.
hl.on("hyprland.start", function()
    --hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    hl.exec_cmd("uwsm app -- /usr/bin/foot --server")
    hl.exec_cmd("uwsm app -- wl-clip-persist --clipboard regular --reconnect-tries 0")
    hl.exec_cmd("uwsm app -- wl-paste --type text --watch cliphist store")
    hl.exec_cmd("uwsm app -- kdeconnect-indicator")
    hl.exec_cmd("uwsm app -- pypr --config ~/.config/hypr/pyprland.toml")  -- scratchpad daemon (qtile DropDown parity)
    hl.exec_cmd("uwsm app -- noctalia")
    --hl.exec_cmd("foot -server")
end)

------------------ LOOK AND FEEL ------------------
hl.config({
    general = {
        -- qtile layout_theme: margin 10, 1px borders, OneDark colors
        gaps_in      = 10,
        gaps_out     = 10,
        border_size  = 1,
        layout = "master",
    },
    decoration = {
        -- NO rounded corners anywhere
        rounding         = 0,
        active_opacity   = 1,
        inactive_opacity = 1,
        shadow = {
            enabled      = true,
            range        = 10,
            render_power = 3,
        },
        blur = {
		passes = 1,
		noise = 0,
		ignore_opacity = false,
		size = 1,
		contrast = 1,
		brightness = 2,
		new_optimizations = true,
		},

    },

})

------------------ LAYOUTS ------------------
-- master = qtile MonadTall: master left, stack right,
-- new windows join the stack (new_status = "slave")
hl.config({
    master = {
        mfact        = 0.5,
        new_status   = "slave",
        orientation  = "left",
    },
    dwindle = {
        preserve_split = true,  -- only used if mod+Tab cycles to dwindle
    },
    misc = {
        disable_hyprland_logo   = true,
        disable_splash_rendering = true,
        force_default_wallpaper = 0,       -- Noctalia draws the wallpaper
        --background_color        = 0x282c34,
    },
})

------------------ ULTRAWIDE 20/60/20 LAYOUT ------------------
-- Three fixed columns (20% / 60% / 20%), center column is the main window.
-- Registered only -- it does not become your layout until you select it:
--   live/one-off:  hl.config({ general = { layout = "lua:ultrawide" } })
--   permanent:     set general.layout = "lua:ultrawide" in the block above.
-- The "lua:" prefix is required; a bare "ultrawide" parses fine and then
-- silently falls back to dwindle. Window 1 goes center, later windows
-- alternate left/right and stack vertically inside their column.
hl.layout.register("ultrawide", {
    recalculate = function(ctx)
        local n = #ctx.targets
        if n == 0 then return end

        local a  = ctx.area
        local wl = math.floor(a.w * 0.20)
        local wr = math.floor(a.w * 0.20)
        local wm = a.w - wl - wr

        -- column geometry: 1 = left, 2 = center, 3 = right
        local cx = { a.x, a.x + wl, a.x + wl + wm }
        local cw = { wl, wm, wr }

        local col  = { [1] = 2 }
        local side = 1
        for i = 2, n do
            col[i] = side
            side = (side == 1) and 3 or 1
        end

        local total, seen = { 0, 0, 0 }, { 0, 0, 0 }
        for i = 1, n do total[col[i]] = total[col[i]] + 1 end

        for i = 1, n do
            local c = col[i]
            seen[c] = seen[c] + 1
            local h = math.floor(a.h / total[c])
            local y = a.y + (seen[c] - 1) * h
            if seen[c] == total[c] then h = a.y + a.h - y end
            ctx.targets[i]:place({ x = cx[c], y = y, w = cw[c], h = h })
        end
    end,
})

------------------ INPUT ------------------
hl.config({
    input = {
        kb_layout        = "us",
        numlock_by_default = true,
        repeat_rate      = 25,
        repeat_delay     = 600,
        follow_mouse     = 1,
        touchpad = {
            tap_to_click     = true,
            natural_scroll   = false,
        },
    },
})

------------------ WINDOW RULES ------------------
-- floats (qtile floating_layout + mango rule.conf)
hl.window_rule({ match = { class = "^xdg-desktop-portal-gtk$" },           float = true })
hl.window_rule({ match = { class = "^megasync$" },                         float = true })
hl.window_rule({ match = { class = "^blueman-manager$" },                  float = true })
hl.window_rule({ match = { class = "^yesplaymusic$" },                     float = true })
hl.window_rule({ match = { class = "^clash-verge$" },                      float = true })
hl.window_rule({ match = { class = "^baidunetdisk$" },                     float = true })
hl.window_rule({ match = { class = "^pot$", title = "^Recognize$" },       float = true })
hl.window_rule({ match = { class = "^Rofi$" },                             float = true })
hl.window_rule({ match = { class = "^python3$", title = "^qxdrag$" },      float = true })

------------------ KEYBINDS ------------------
local mainMod = "SUPER"

-- reload & quit (qtile: mod+ctrl+r / mod+ctrl+q)
hl.bind(mainMod .. " + CTRL + R", hl.dsp.exec_cmd("hyprctl reload"))
hl.bind(mainMod .. " + CTRL + Q", hl.dsp.exit())

-- terminal & launchers (qtile: mod+Return ghostty, mod+d launcher)
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd("footclient"))
hl.bind(mainMod .. " + D",      hl.dsp.exec_cmd("noctalia msg panel-toggle launcher"))
hl.bind(mainMod .. " + W",      hl.dsp.exec_cmd("noctalia msg panel-toggle wallpaper"))


-- focus movement (qtile: mod+arrows / mod+space next)
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + space", hl.dsp.layout("cyclenext"))
-- mod+Tab: cycle layout master <-> dwindle (script flips general:layout)
hl.bind(mainMod .. " + Tab",   hl.dsp.exec_cmd("noctalia msg plugin maddingo/hypr-layout-switcher:poller all cycle"))
-- mod+Tab+A: switch to the ultrawide 20/60/20 layout (registered above).
-- Longer chord on the same prefix, so plain mod+Tab now fires on key release.
hl.bind(mainMod .. " + Tab + A", function()
    hl.config({ general = { layout = "lua:ultrawide" } })
end)
hl.bind("ALT + TAB", hl.dsp.exec_cmd("noctalia msg window-switcher hold"))
-- move window (qtile: mod+shift+arrows = shuffle)
hl.bind(mainMod .. " + SHIFT + left",  hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + up",    hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + down",  hl.dsp.window.move({ direction = "down" }))

-- master pane size (qtile: mod+ctrl+left/right = shrink/grow main)
hl.bind(mainMod .. " + CTRL + left",  hl.dsp.layout("mfact -0.05"))
hl.bind(mainMod .. " + CTRL + right", hl.dsp.layout("mfact +0.05"))

-- window state (qtile keys kept)
hl.bind(mainMod .. " + Q",        hl.dsp.window.close())              -- qtile mod+q: kill window
hl.bind(mainMod .. " + SHIFT + Q", hl.dsp.exec_cmd("noctalia msg panel-toggle session")) -- qtile power popup
hl.bind(mainMod .. " + F",        hl.dsp.window.fullscreen())         -- qtile mod+f
hl.bind(mainMod .. " + T",        hl.dsp.window.float())              -- qtile mod+t
hl.bind(mainMod .. " + L",        hl.dsp.exec_cmd("~/.config/hypr/scripts/lock-suspend.sh")) -- qtile mod+l: pause media + lock & suspend

-- apps (qtile: mod+shift+n = brave incognito)
hl.bind(mainMod .. " + SHIFT + N", hl.dsp.exec_cmd("brave-origin --incognito"))

-- scratchpads (qtile: F12 term / mod+a fm / mod+w sol / mod+g gam)
-- handled by pyprland (qtile DropDown parity, see pyprland.toml)
hl.bind("F12",             hl.dsp.exec_cmd("pypr toggle term"))
hl.bind(mainMod .. " + A", hl.dsp.exec_cmd("pypr toggle fm"))
hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("pypr toggle sol"))
hl.bind(mainMod .. " + G", hl.dsp.exec_cmd("pypr toggle gam"))


-- volume & brightness (Noctalia OSD, mango parity)
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd("noctalia msg volume-up"))
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd("noctalia msg volume-down"))
hl.bind("XF86AudioMute",         hl.dsp.exec_cmd("noctalia msg volume-mute"))
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("noctalia msg brightness-up"))
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("noctalia msg brightness-down"))

-- screenshots (mango parity: Print full / shift+Print area / ctrl+alt+a annotate)
hl.bind("Print",          hl.dsp.exec_cmd("noctalia msg screenshot-fullscreen"))


-- mouse (qtile: mod+drag move, mod+right-drag resize)
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- tags 1-5 (qtile/mango: mod+N switch, mod+shift+N move+switch)
for i = 1, 5 do
    hl.bind(mainMod .. " + " .. i,         hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. i, hl.dsp.window.move({ workspace = i }))
end
-- persistent workspaces
hl.workspace_rule({ workspace = "1", persistent = true })
hl.workspace_rule({ workspace = "2", persistent = true })
hl.workspace_rule({ workspace = "3", persistent = true })
hl.workspace_rule({ workspace = "4", persistent = true })
hl.workspace_rule({ workspace = "5", persistent = true })

-- For Noctalia Color templates
-- For Noctalia Color templates
require("noctalia").apply_theme()
