#!/usr/bin/env bash
# qtile mod+Tab: cycle layouts (master <-> dwindle)
# NOTE: lua config provider => `hyprctl keyword` is refused ("keyword can't work
# with non-legacy parsers"); runtime changes go through eval + hl.config merge.
cur=$(hyprctl getoption general.layout -j | jq -r '.str')
if [ "$cur" = "master" ]; then next="dwindle"; else next="master"; fi
hyprctl eval "hl.config({ general = { layout = \"$next\" } })"
