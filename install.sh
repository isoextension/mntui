#!/usr/bin/env bash

# install script for mntui
set -e

_color() {
    case "$1" in
        reset) echo "\033[0m" ;;
        black) echo "\033[0;30m" ;;
        red) echo "\033[0;31m" ;;
        green) echo "\033[0;32m" ;;
        yellow) echo "\033[0;33m" ;;
        blue) echo "\033[0;34m" ;;
        magenta) echo "\033[0;35m" ;;
        cyan) echo "\033[0;36m" ;;
        white) echo "\033[0;37m" ;;

        bright_black) echo "\033[0;90m" ;;
        bright_red) echo "\033[0;91m" ;;
        bright_green) echo "\033[0;92m" ;;
        bright_yellow) echo "\033[0;93m" ;;
        bright_blue) echo "\033[0;94m" ;;
        bright_magenta) echo "\033[0;95m" ;;
        bright_cyan) echo "\033[0;96m" ;;
        bright_white) echo "\033[0;97m" ;;

        bold) echo "\033[1m" ;;
        *) echo "" ;;
    esac
}

_paint() {
    printf "$(_color "$2")$1$(_color reset)\n"
}

MNTUI_VENV=/opt/mntui
MNTUI_BIN_DIR=/opt/mntui/main.py
MNTUI_BINCURL=/opt/mntui/main.py
PROFILE_SCRIPT=/etc/profile.d
FISH_SCRIPT=/etc/fish/profile.d

_check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

_compare_var() {
    VARIABLE="$(eval echo "\$$1")"
    TO_COMPARE=$2

    if [ "$VARIABLE" = "$TO_COMPARE" ]; then
        return 0
    else
        return 1
    fi
}

_compare_int () {
    VARIABLE="$(eval echo "\$$1")"
    TO_COMPARE=$2

    if [ "$VARIABLE" -eq "$TO_COMPARE" ]; then
        return 0
    else
        return 1
    fi
}

_install() {
    printf "==> Installing $1...\n"
    if _check_cmd pacman; then
        sudo pacman -S --no-confirm $1
    elif _check_cmd apt; then
        sudo apt install -y $1
    elif _check_cmd dnf; then
        sudo dnf install -y $1
    else
        printf "==> Your package manager is not supported. Install $1 manually\n"
        exit 1
    fi
}

_check_cmd gum || _install gum
_check_cmd python3 || _install python3

gum confirm "Continue setup?"
if [[ $? -ne 0 ]]; then
    printf "aborted.\n"
    exit 130
fi

_paint " -> Creating root venv at $MNTUI_VENV..." blue
sudo python -m venv "$MNTUI_VENV"

_paint " -> Installing PyQt6 in venv..." blue
sudo "$MNTUI_VENV/bin/pip" install --upgrade pip
sudo "$MNTUI_VENV/bin/pip" install PyQt6

_paint " -> Copying mntui script..." blue
sudo cp mntui "$MNTUI_BIN"
sudo chmod +x "$MNTUI_BIN"

_paint " -> Creating system-wide PATH entry..." blue
sudo tee "$PROFILE_SCRIPT" > /dev/null <<EOF
# added by mntui installer
export PATH="\$PATH:$MNTUI_VENV"
EOF

sudo tee "$FISH_SCRIPT" > /dev/null <<EOF
# added by mntui installer
set -gx PATH $PATH /opt/mntui
EOF

sudo chmod +x "$PROFILE_SCRIPT"
sudo chmod +x "$FISH_SCRIPT"

_paint "==> done" green
