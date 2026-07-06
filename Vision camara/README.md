# R1 Camera Viewer

Visor de cámara para el robot **Unitree R1** sobre ROS2 Foxy. Obtiene frames JPEG de la cámara frontal vía el servicio DDS `videohub` y los muestra en tiempo real con OpenCV.

## Requisitos

- ROS2 Foxy con `rmw_cyclonedds_cpp`
- [`unitree_sdk2_python`](https://github.com/unitreerobotics/unitree_sdk2_python) en `~/unitree_sdk2_python`
- Configuración CycloneDDS en `~/unitree_ros2/ros_config.xml` (interfaz: `enp0s31f6`)
- `python3-opencv`, `python3-numpy`

## Uso

```bash
./start_camera.sh [modo] [iface]
```

| Argumento | Valores | Default |
|-----------|---------|---------|
| `modo`    | `720p` `360p` `180p` `all` | `720p` |
| `iface`   | nombre de interfaz de red (ej: `enp0s31f6`) | autodetect |

Ejemplos:

```bash
./start_camera.sh            # 720p, interfaz automática
./start_camera.sh all        # todas las resoluciones simultáneas
./start_camera.sh 360p enp0s31f6
```

## Controles

| Tecla | Acción |
|-------|--------|
| `1`   | Solo 720p (1280×720) |
| `2`   | Solo 360p (640×360) |
| `3`   | Solo 180p (320×180) |
| `A`   | Todas las resoluciones |
| `ESC` | Salir |

## Modo "all"

Muestra las tres resoluciones del mismo sensor frontal en un único mosaico:

```
┌──────────────────────────┐
│        720p (grande)     │
├────────────┬─────────────┤
│    360p    │  180p+pad   │
└────────────┴─────────────┘
```

## Arquitectura

El script `r1_camera_sdk.py` usa `VideoClient.GetImageSample()` (servicio DDS `videohub`, API ID 1001) para obtener frames JPEG de 1280×720 directamente del robot. Las variantes de menor resolución se generan en cliente por downscale.

> **Nota:** El topic ROS2 `/frontvideostream` existe pero no es usable desde Python por un bug en cyclonedds 0.10.2 con XCDRv2 DataRepresentation QoS (incompatibilidad id=24). El enfoque RPC funciona correctamente.

## Archivos

```
camara_r1_ws/
├── r1_camera_sdk.py   # script principal
├── start_camera.sh    # wrapper de lanzamiento
└── src/
    └── r1_camera_viewer/   # paquete ROS2 (construido, no usado)
```
