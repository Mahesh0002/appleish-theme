#!/usr/bin/env bash
set -euo pipefail

# uninstall.sh — Remove the Appleish GTK theme user install.
#
# Only removes $DEST if it contains a valid Appleish index.theme.
# With --restore, restores the newest $DEST.bak-* backup instead.

DEST="${XDG_DATA_HOME:-$HOME/.local/share}/themes/Appleish"

restore=0
if [[ "${1:-}" == "--restore" ]]; then
    restore=1
fi

if [[ "$restore" -eq 1 ]]; then
    backup="$(ls -1dt "$DEST".bak-* 2>/dev/null | head -1 || true)"
    if [[ -z "$backup" ]]; then
        echo "No $DEST.bak-* backup found to restore" >&2
        exit 1
    fi
    rm -rf "$DEST"
    mv "$backup" "$DEST"
    echo "Restored $DEST from $backup"
    exit 0
fi

if [[ ! -e "$DEST" ]]; then
    echo "$DEST does not exist; nothing to remove"
    exit 0
fi

if ! grep -q 'Name=Appleish' "$DEST/index.theme" 2>/dev/null; then
    echo "Refusing: $DEST is not an Appleish install" >&2
    exit 1
fi

rm -rf "$DEST"
echo "Removed Appleish theme from $DEST"
