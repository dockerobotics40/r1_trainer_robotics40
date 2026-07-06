#!/usr/bin/env bash
set -e

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$HOME/unitree_mujoco}"

echo "[INFO] Paquete: $PKG_DIR"
echo "[INFO] Target unitree_mujoco: $TARGET"

if [ ! -d "$TARGET" ]; then
  echo "[ERROR] No existe $TARGET"
  echo "Uso opcional:"
  echo "  ./instalar_archivos_r1_en_unitree_mujoco.sh /ruta/a/unitree_mujoco"
  exit 1
fi

mkdir -p "$TARGET/unitree_robots"
mkdir -p "$TARGET/simulate"

TS="$(date +%Y%m%d_%H%M%S)"

if [ -d "$TARGET/unitree_robots/r1" ]; then
  cp -a "$TARGET/unitree_robots/r1" "$TARGET/unitree_robots/r1.backup_$TS"
  echo "[OK] Backup creado: $TARGET/unitree_robots/r1.backup_$TS"
fi

if [ -f "$TARGET/simulate/config.yaml" ]; then
  cp "$TARGET/simulate/config.yaml" "$TARGET/simulate/config.yaml.backup_$TS"
  echo "[OK] Backup creado: $TARGET/simulate/config.yaml.backup_$TS"
fi

rm -rf "$TARGET/unitree_robots/r1"
cp -a "$PKG_DIR/01_modelo_r1_final/unitree_robots/r1" "$TARGET/unitree_robots/"
cp "$PKG_DIR/02_config_simulador/config.yaml" "$TARGET/simulate/config.yaml"

echo "[OK] Archivos R1 finales instalados en $TARGET"
echo "[INFO] Ahora ejecuta:"
echo "  cd $TARGET/simulate/build"
echo "  ./unitree_mujoco"
