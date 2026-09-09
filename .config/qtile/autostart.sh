#!/usr/bin/env bash
# quickshell -p ~/.config/quickshell/bar.qml &
picom -b &
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
dunst &
nm-applet --indicator &
wait -n  &
kdeconnect-indicator &
wait -n & 
blueman-applet &
wait -n  &
DO_NOT_UNSET_QT_QPA_PLATFORMTHEME=1 megasync &
xautolock -time 10 -locker "betterlockscreen -l" &
pactl load-module module-switch-on-connect
 remmina -i &
 
