#!/bin/bash

rofi_command="rofi -theme ~/.config/qtile/rofi/powermenu.rasi"

#### Options ###
shutdown=''
reboot=''
lock=''
suspend='󰒲'
logout='󰍃'


options="$shutdown\n$reboot\n$lock\n$suspend\n$logout"

chosen="$(echo -e "$options" | $rofi_command -dmenu -selected-row 2)"
case $chosen in
    $lock)
	    amixer set Master mute
        betterlockscreen -l dim
	      ;;    
    $shutdown)
        systemctl poweroff
        ;;
    $reboot)
        systemctl reboot
        ;;
    $suspend)
	    mpc -q pause
	    amixer set Master mute
	    systemctl suspend
        ;;
    $logout)
        loginctl terminate-session ${XDG_SESSION_ID-}	
	;;
esac
