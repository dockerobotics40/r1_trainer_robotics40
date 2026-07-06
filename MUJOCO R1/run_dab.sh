#!/usr/bin/env bash
set -e

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PKG_DIR"

python3 03_scripts_movimiento/r1_pose_player_mujoco.py 04_rutinas_txt/dab.txt
