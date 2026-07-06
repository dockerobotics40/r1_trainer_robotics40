#!/bin/bash
# Visor de cámara R1
# Uso: ./start_camera.sh [modo] [iface]
#   modo : 720p | 360p | 180p | all  (default: 720p)
#   iface: interfaz de red (ej: eth0). Vacío = autodetect
#
# Controles en ventana: 1=720p  2=360p  3=180p  A=todas  ESC=salir

MODE="${1:-720p}"
IFACE="${2:-}"

export CYCLONEDDS_URI="file://$HOME/unitree_ros2/ros_config.xml"

echo "R1 Camera Viewer — modo: $MODE"
echo "Controles: 1=720p  2=360p  3=180p  A=todas  ESC=salir"
python3 "$(dirname "$0")/r1_camera_sdk.py" "$IFACE" "$MODE"
