#!/usr/bin/env bash
set -e

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/unitree_mujoco/simulate/mujoco/build/lib:/opt/unitree_robotics/lib"

cd "$HOME/unitree_mujoco/simulate/build"
./unitree_mujoco
