#!/bin/bash
# /home/med4to/ProjectAuraOS/gaming-optimizations/optimize-game.sh
# Master script for "otimizar pra jogo" requests.
# Run this or I (Grok) will run detection + research + apply personalized top-tier tweaks.

set -euo pipefail
# Use persistent daemon state if available (preferred when detector is always-on)
if [ -f "$HOME/.cache/gaming/current-game" ]; then
    eval "$(sed "s/^/export /" "$HOME/.cache/gaming/current-game" 2>/dev/null || true)"
fi

DETECTOR=~/bin/detect-running-game.sh
PROFILES_DIR="/home/med4to/ProjectAuraOS/gaming-optimizations/profiles"
TEMPLATES_DIR="/home/med4to/ProjectAuraOS/gaming-optimizations/templates"

echo "=== GAME OPTIMIZATION FRAMEWORK ==="
echo "User setup: Ubuntu + Wayland + AMD RX 6600 (RADV) + Steam + custom Protons (GE, CachyOS etc.)"
echo

if [ ! -x "$DETECTOR" ]; then
  echo "Detector not found. Run the setup first."
  exit 1
fi

# Run detection and capture structured info
echo "Running detection..."
eval "$($DETECTOR | grep -E '^(APPID|GAME_NAME|GAME_DIR|PREFIX)=' )" 2>/dev/null || true

if [ "${APPID:-unknown}" = "unknown" ] || [ "${GAME_NAME:-unknown}" = "unknown" ]; then
  echo "No clear game detected as running."
  echo "Recently played (from earlier detection): check the list or launch the game first."
  echo "You can also pass APPID manually: APPID=883710 GAME_NAME='Resident Evil 2' $0"
  exit 1
fi

echo
echo "=== DETECTED GAME ==="
echo "Name     : $GAME_NAME"
echo "AppID    : $APPID"
echo "Dir      : $GAME_DIR"
echo "Prefix   : $PREFIX"
echo

SANITIZED=$(echo "$GAME_NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/-$//')
PROFILE_DIR="$PROFILES_DIR/$SANITIZED"

echo "Profile dir: $PROFILE_DIR"
mkdir -p "$PROFILE_DIR"

# Create per-game files if not exist
if [ ! -f "$PROFILE_DIR/launch-options.txt" ]; then
  cat > "$PROFILE_DIR/launch-options.txt" << EOF
# Personalized launch options for $GAME_NAME (AppID $APPID)
# Generated for: Ubuntu + Wayland + RX 6600 + Proton

# Recommended base (copy to Steam Properties > Launch Options)
gamescope -e -- gamemoderun %command%

# Advanced / game-specific (research per title):
# RADV_DEBUG=... VKD3D_CONFIG=... PROTON_... etc.
# Example from RE2: RADV_DEBUG=nomeshshader gamescope -e -- gamemoderun %command% -dx12

# Proton recommendation: Usually Proton-GE Latest or Proton-CachyOS Latest.
# Test both. GE often has game-specific fixes.

# Notes:
# - Always enable in-game max graphics / DX12 or best API if available.
# - Use gamescope for Wayland (reduces latency/tearing).
# - Keep quality: we only add workarounds for Linux bugs, never disable RT/high settings unless they are broken on Proton.
EOF
  echo "Created template launch-options.txt"
fi

if [ ! -f "$PROFILE_DIR/notes.md" ]; then
  cat > "$PROFILE_DIR/notes.md" << EOF
# $GAME_NAME (AppID $APPID) - Optimization Notes

## User setup
- OS: Ubuntu (GNOME Wayland)
- GPU: AMD RX 6600 (RADV / amdgpu)
- Launcher: Steam + custom Protons (GE, CachyOS, etc.)
- Goal: Max graphical quality + best Linux/Proton stability & performance.

## Applied tweaks (example style from RE2)
- Launch options with gamescope + gamemoderun + game-specific env vars.
- Config file edits in game dir or prefix (force best API, high settings).
- Proton choice based on ProtonDB reports for this title.
- AMD-specific workarounds only when needed (e.g. mesh shader bugs).

## How to use
1. Set the content of launch-options.txt in Steam > Game Properties > Launch Options.
2. Force the recommended Proton in Compatibility.
3. Launch the game and apply in-game settings for max quality (DX12 if available, RT on, etc.).
4. Run this optimizer again after major updates for fresh research.

## Sources to check when re-optimizing
- https://www.protondb.com/app/$APPID
- Game-specific ini/cfg in $GAME_DIR or $PREFIX/pfx/...
- Recent Reddit r/linux_gaming or Proton GitHub issues for the title.

Last optimized: $(date)
EOF
  echo "Created notes.md"
fi

echo
echo "=== NEXT STEPS FOR THIS GAME ==="
echo "1. I (the AI) will now research the best current tweaks for $GAME_NAME on Proton/AMD/Wayland."
echo "2. I will edit configs, update the launch-options.txt and notes.md with personalized first-class optimizations."
echo "3. Create any needed per-game scripts."
echo "4. Keep max visual quality (enable RT, high textures, best AA etc. whenever the Linux path supports it)."
echo
echo "Profile created/updated at: $PROFILE_DIR"
echo "You can cd there and review the files."
