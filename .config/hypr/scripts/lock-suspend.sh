#!/usr/bin/env bash
# qtile SUPER+L parity: pause all media, then lock AND suspend via Noctalia
# (lock screen shows first; on resume you're locked until unlock, and the
#  browser/player stays paused -- qtile-era betterlockscreen behaviour)
playerctl pause --all-players 2>/dev/null || true
if ! noctalia msg session lock-and-suspend 2>/dev/null; then
    # noctalia unavailable -> plain suspend as a safety net
    systemctl suspend
fi
