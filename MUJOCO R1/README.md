# MUJOCO R1 - Librería de poses Unitree R1

Este paquete contiene la versión funcional y corregida para trabajar poses del robot Unitree R1 en Unitree MuJoCo.

## Contenido

```text
MUJOCO R1/
├── 01_modelo_r1_final/
│   └── unitree_robots/r1/
│       ├── r1.xml
│       ├── scene.xml
│       └── meshes / assets del modelo R1
│
├── 02_config_simulador/
│   └── config.yaml
│
├── 03_scripts_movimiento/
│   ├── r1_pose_player_mujoco.py
│   └── r1_capture_pose.py
│
├── 04_rutinas_txt/
│   ├── test_hold_actual.txt
│   ├── dab.txt
│   └── siuu.txt
│
├── 05_config_r1/
│   ├── r1_joint_map_final.json
│   └── r1_safe_pose_final.json
│
├── 06_herramientas_diagnostico/
│   └── scripts auxiliares de prueba
│
├── 07_instalacion/
│   └── instalar_archivos_r1_en_unitree_mujoco.sh
│
├── run_simulador_r1.sh
├── run_dab.sh
├── run_siuu.sh
└── capturar_pose_r1.sh
