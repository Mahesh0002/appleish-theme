#!/usr/bin/env bash
set -euo pipefail

# install.sh — Install Appleish GTK theme as a user theme.
#
# Copies theme/ into $XDG_DATA_HOME/themes/Appleish/ (default
# ~/.local/share/themes/Appleish/). Backs up any previous install first.

DEST="${XDG_DATA_HOME:-$HOME/.local/share}/themes/Appleish"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -e "$DEST" ]]; then
    if grep -q 'Name=Appleish' "$DEST/index.theme" 2>/dev/null; then
        TS="$(date +%Y%m%d-%H%M%S)"
        mv "$DEST" "$DEST.bak-$TS"
        echo "Backed up previous install to $DEST.bak-$TS"
    else
        echo "Refusing: $DEST exists but is not an Appleish install" >&2
        exit 1
    fi
fi

mkdir -p "$DEST"
cp -r "$REPO_DIR/theme/index.theme" \
      "$REPO_DIR/theme/gtk-3.0" \
      "$REPO_DIR/theme/gtk-4.0" \
      "$DEST"/

echo "Installed Appleish to $DEST"
echo ""
echo "Next steps:"
echo "  GTK_THEME=Appleish gtk3-demo    # test GTK3 apps"
echo "  GTK_THEME=Appleish gtk4-demo    # test GTK4 apps"
echo "  # Or select 'Appleish' in nwg-look / gnome-tweaks / lxappearance"
