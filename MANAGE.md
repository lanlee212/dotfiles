# Dotfiles — How To Manage

Setup: ~/.config/{qtile,hypr,dunst} are SYMLINKS into this repo (~/dotfiles).
Editing a config = editing the repo. No copying, ever.

## Machines on the farm
- Desktop (Arch, this one): live symlinks, git repo here
- dora (laptop, Fedora 44, 192.168.7.111): same repo cloned at ~/dotfiles,
  same symlinks. Keep it updated with `git -C ~/dotfiles pull`

## Normal workflow
1. Edit configs as usual (they're already in the repo via symlinks)
2. `git -C ~/dotfiles add -A .config`  (never `add -A` bare — Qqsp/ junk is untracked on purpose)
3. `git -C ~/dotfiles commit -m "what changed"`
4. `git -C ~/dotfiles push`  (auth via gh CLI — no tokens in URLs!)
5. On dora: `git -C ~/dotfiles pull`
6. Restart the app (Hyprland/qtile/dunst pick up changes on next start)

## Adding a new config dir to the farm
    rsync -a ~/.config/<app>/ ~/dotfiles/.config/<app>/   # bring live files in
    mv ~/.config/<app> ~/.dotfile-swap-backup/            # safety copy (or rm)
    ln -s ~/dotfiles/.config/<app> ~/.config/<app>
    git -C ~/dotfiles add .config/<app> && commit && push

## Rules / gotchas
- Machine-specific stuff (monitor layouts, per-host autostart) does NOT belong
  in shared files — guard it with a hostname check or keep it out of the repo
- .gitignore covers __pycache__, *.pyc, *.save backups — git history replaces
  those old backup files
- Anything in Qqsp/ is untracked build junk, leave it alone
- Pre-swap backups of old configs may sit in ~/.dotfile-swap-backup on either
  machine — delete once everything works after a reboot
- Config sanity checks: `python3 -m py_compile ~/.config/qtile/config.py`
  and `Hyprland --verify-config`

Not tracked (yet): waybar, rofi, alacritty — same one-liner as above adds them.
