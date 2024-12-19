#!/usr/bin/env bash
# polybar &
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
#/usr/libexec/polkit-gnome-authentication-agent-1 &
#deadd-notification-center &
picom -b &
sleep 1
nm-applet &
kdeconnect-indicator &
blueman-applet &
megasync &
dlauncher &
light-locker &
xautolock -time 5 -locker "/usr/bin/light-locker-command -l" &
#/usr/lib/xfce4/notifyd/xfce4-notifyd &
# xfce4-power-manager &
