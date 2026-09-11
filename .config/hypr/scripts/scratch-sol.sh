#!/usr/bin/env bash
# sol scratchpad (native, Hyprland 0.56 Lua era)
# Replaces pyprland's [scratchpads.sol] — pyprland shells out classic
# `hyprctl dispatch ...`, which 0.56 rejects under a Lua config provider,
# so its show/hide silently did nothing.
# Behavior: spawn aisleriot if missing, wait until it lands on special:sol,
# then toggle the workspace.

on_special() {
    hyprctl clients -j | jq '[.[] | select(.class == "sol" and .workspace.name == "special:sol")] | length' 2>/dev/null || echo 0
}
any_sol() {
    hyprctl clients -j | jq '[.[] | select(.class == "sol")] | length' 2>/dev/null || echo 0
}

if [ "$(any_sol)" -eq 0 ]; then
    setsid flatpak run org.gnome.Aisleriot >/dev/null 2>&1 &
    for _ in $(seq 1 40); do          # up to 10s for the window to map + be parked
        sleep 0.25
        [ "$(on_special)" -gt 0 ] && break
    done
    sleep 0.3                        # let the special workspace exist before toggling
fi

hyprctl repl 'hl.dispatch(hl.dsp.workspace.toggle_special("sol"))' >/dev/null 2>&1
