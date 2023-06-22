#!/bin/sh
function run {
  if ! pgrep $1 ;
  then
    $@&
  fi
}

/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
#/usr/lib/xfce4/notifyd/xfce4-notifyd &
dex /usr/share/applications/org.kde.kdeconnect.nonplasma.desktop
dunst &
dex --autostart &
sh -c "GDK_BACKEND=x11 pamac-tray" &
#run volumeicon &
numlockx on &
#nm-applet &
#remmina -i &
#megasync &
nitrogen --restore &
run xsettingsd &
#boot picom or compton if it exists
if [ -x "$(command -v picom)" ]; then
  picom &> /dev/null &
elif [ -x "$(command -v compton)" ]; then
  compton &> /dev/null &
fi
