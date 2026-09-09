#!/usr/bin/env bash
dir=~/Pictures
mkdir -p "$dir"
case "$1" in
    full)      grim "$dir/$(date +%Y-%m-%d-%T).png" ;;
    area)      grim -g "$(slurp -b '#2E2A1E55' -c '#fb751bff')" "$dir/$(date +%Y-%m-%d-%T).png" ;;
    annotate)  grim -g "$(slurp -b '#2E2A1E55' -c '#fb751bff')" -t ppm - | satty -f - ;;
esac
