# Documentación Técnica: Librería de Poses MuJoCo para Unitree R1

**Paquete técnico MUJOCO R1 para simulación, captura y ejecución de rutinas**

| Campo | Detalle |
|---|---|
| Paquete / Script | MUJOCO R1; script principal `r1_pose_player_mujoco.py` |
| Versión | 1.0 |
| Plataforma | Ubuntu 20.04 recomendado; Python 3; Unitree MuJoCo |
| Robot / Hardware | Unitree R1 en simulación MuJoCo |
| SDK / Framework | Unitree SDK2 Python; DDS; LowCmd / LowState |
| Script base | `unitree_mujoco` con modelo R1 corregido |
| Autor | Robotics 4.0 |
| Fecha | Julio de 2026 |

---

## 0. Contenido

1. [Descripción General](#1-descripción-general)
   - [1.1 Componentes desarrollados](#11-componentes-desarrollados)
   - [1.2 Usuarios previstos](#12-usuarios-previstos)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
   - [2.1 Capas funcionales](#21-capas-funcionales)
   - [2.2 Comunicación](#22-comunicación)
   - [2.3 Diagrama textual de flujo](#23-diagrama-textual-de-flujo)
3. [Requisitos y Dependencias](#3-requisitos-y-dependencias)
   - [3.1 Requisitos principales](#31-requisitos-principales)
   - [3.2 Verificación de `unitree_sdk2py`](#32-verificación-de-unitree_sdk2py)
   - [3.3 Variable `LD_LIBRARY_PATH`](#33-variable-ld_library_path)
4. [Organización de Archivos](#4-organización-de-archivos)
   - [4.1 Estructura esperada](#41-estructura-esperada)
   - [4.2 Archivos obligatorios](#42-archivos-obligatorios)
   - [4.3 Rutas recomendadas](#43-rutas-recomendadas)
5. [Formato de Entrada](#5-formato-de-entrada)
   - [5.1 Campos de una rutina](#51-campos-de-una-rutina)
   - [5.2 Índices válidos](#52-índices-válidos)
   - [5.3 Pose segura obligatoria](#53-pose-segura-obligatoria)
   - [5.4 Ejemplo mínimo funcional](#54-ejemplo-mínimo-funcional)
6. [Código Fuente y Funcionamiento Interno](#6-código-fuente-y-funcionamiento-interno)
   - [6.1 Script principal: `r1_pose_player_mujoco.py`](#61-script-principal-r1_pose_player_mujocopy)
   - [6.2 Script de captura: `r1_capture_pose.py`](#62-script-de-captura-r1_capture_posepy)
   - [6.3 Modelo corregido: `r1.xml`](#63-modelo-corregido-r1xml)
7. [Flujo de Ejecución](#7-flujo-de-ejecución)
   - [7.1 Paso 1: ubicar la carpeta descargada](#71-paso-1-ubicar-la-carpeta-descargada)
   - [7.2 Paso 2: verificar Unitree MuJoCo](#72-paso-2-verificar-unitree-mujoco)
   - [7.3 Paso 3: instalar archivos R1 finales dentro de Unitree MuJoCo](#73-paso-3-instalar-archivos-r1-finales-dentro-de-unitree-mujoco)
   - [7.4 Paso 4: verificar `unitree_sdk2py`](#74-paso-4-verificar-unitree_sdk2py)
   - [7.5 Paso 5: abrir el simulador R1](#75-paso-5-abrir-el-simulador-r1)
   - [7.6 Paso 6: ejecutar una rutina](#76-paso-6-ejecutar-una-rutina)
   - [7.7 Paso 7: validar sintaxis de una rutina](#77-paso-7-validar-sintaxis-de-una-rutina)
   - [7.8 Paso 8: capturar una nueva pose](#78-paso-8-capturar-una-nueva-pose)
8. [Seguridad Operacional](#8-seguridad-operacional)
   - [8.1 Condiciones antes de ejecutar](#81-condiciones-antes-de-ejecutar)
   - [8.2 Qué no debe modificarse sin precaución](#82-qué-no-debe-modificarse-sin-precaución)
   - [8.3 Detención en simulación](#83-detención-en-simulación)
   - [8.4 Consideraciones para robot físico](#84-consideraciones-para-robot-físico)
9. [Guía de Uso Rápido](#9-guía-de-uso-rápido)
   - [9.1 Ejecución rápida de `siuu`](#91-ejecución-rápida-de-siuu)
   - [9.2 Ejecución rápida de `dab`](#92-ejecución-rápida-de-dab)
10. [Problemas Conocidos y Soluciones](#10-problemas-conocidos-y-soluciones)
11. [Extensión y Mantenimiento](#11-extensión-y-mantenimiento)
   - [11.1 Agregar una nueva rutina](#111-agregar-una-nueva-rutina)
   - [11.2 Recomendaciones para rutinas nuevas](#112-recomendaciones-para-rutinas-nuevas)
   - [11.3 Validaciones después de modificar](#113-validaciones-después-de-modificar)
12. [Correcciones Técnicas Realizadas](#12-correcciones-técnicas-realizadas)
13. [Resumen de Actividades](#13-resumen-de-actividades)
14. [Cierre técnico](#cierre-técnico)

---

## 1. Descripción General

El paquete **MUJOCO R1** es una entrega técnica organizada para ejecutar, capturar y extender rutinas de movimiento de cintura, brazos y cabeza del robot **Unitree R1** dentro del entorno **Unitree MuJoCo**. Esta documentación parte de un escenario concreto: el usuario recibe una carpeta llamada `MUJOCO R1` y ya cuenta, o debe instalar previamente, con una copia funcional del repositorio `unitree_mujoco` y del paquete `unitree_sdk2py`.

La herramienta permite ejecutar rutinas de ejemplo como `dab.txt` y `siuu.txt`, capturar nuevas poses desde el simulador y crear nuevas rutinas en archivos `.txt` con formato JSON. El flujo está pensado para equipos técnicos que necesitan replicar el entorno R1 sin revisar todo el repositorio de Unitree, que contiene también otros robots y recursos no necesarios para esta entrega.

Durante el desarrollo se corrigieron tres fallas críticas:

1. El modelo R1 no tenía sensores articulares suficientes para que `LowState` entregara posiciones, velocidades y torques estimados en el orden esperado por el bridge.
2. Los actuadores heredaban inicialmente un `ctrlrange` demasiado bajo, por lo que los brazos no alcanzaban poses amplias.
3. Al ampliar la autoridad de control sin amortiguación, el robot presentaba oscilaciones rápidas. Esto se estabilizó con límites por grupo y rampa progresiva de ganancias.

### 1.1 Componentes desarrollados

| Componente | Tipo | Descripción | Estado |
|---|---|---|---|
| `r1_pose_player_mujoco.py` | Script Python | Ejecuta rutinas TXT/JSON sobre el R1 mediante `LowCmd`. Incluye mapeo por `Actuator_index`, interpolación y rampa de ganancias. | Final |
| `r1_capture_pose.py` | Script Python | Captura la pose actual desde `LowState` y genera un bloque JSON listo para pegar en una rutina. | Final |
| `r1.xml` | Modelo MuJoCo | Modelo R1 corregido con sensores articulares y límites de control ajustados. | Final |
| `config.yaml` | Configuración | Selecciona robot R1, interfaz `lo`, dominio `0` y `elastic_band`. | Final |
| `dab.txt` | Rutina TXT | Rutina de ejemplo tipo dab. Inicia y termina en pose segura. | Validada |
| `siuu.txt` | Rutina TXT | Rutina de ejemplo con dos movimientos y sostenimiento de pose. | Validada |
| `r1_safe_pose_final.json` | Configuración | Define la pose segura estándar para iniciar y finalizar rutinas. | Final |
| `r1_joint_map_final.json` | Referencia | Documenta índices válidos para cintura, brazos y cabeza. | Final |

### 1.2 Usuarios previstos

- Ingenieros o técnicos que deban entregar un entorno R1 reproducible.
- Usuarios que ya tengan instalado `unitree_mujoco` y quieran ejecutar poses R1.
- Desarrolladores que necesiten crear nuevas rutinas de brazos, cabeza y cintura.
- Equipos que quieran usar `dab.txt` y `siuu.txt` como ejemplos base.

---

## 2. Arquitectura del Sistema

La arquitectura se basa en un computador local ejecutando Unitree MuJoCo y scripts Python que publican comandos de bajo nivel mediante DDS. El simulador representa el robot R1 y expone tópicos compatibles con el flujo `LowCmd` / `LowState`. El script principal lee rutinas desde archivos `.txt`, interpola posiciones objetivo y envía comandos articulares al simulador.

### 2.1 Capas funcionales

| Capa / Módulo | Función | Entrada | Salida |
|---|---|---|---|
| Modelo R1 MuJoCo | Representa cinemática, dinámica, actuadores y sensores del R1. | `r1.xml`, `scene.xml`, meshes | Estado físico simulado |
| Simulador Unitree MuJoCo | Carga el robot, ejecuta la simulación y conecta DDS. | `config.yaml` | Tópicos `LowState` / `LowCmd` |
| Script de ejecución | Lee rutinas, interpola pasos y publica comandos. | `dab.txt`, `siuu.txt` u otra rutina | Movimiento del R1 en MuJoCo |
| Script de captura | Lee la pose actual desde `LowState`. | Pose actual del robot en simulador | Bloque JSON de posiciones |
| Rutinas TXT | Definen secuencias temporales de posiciones articulares. | JSON en archivo `.txt` | Objetivos articulares en radianes |

### 2.2 Comunicación

| Canal / Interfaz | Uso | Entorno | Observación |
|---|---|---|---|
| DDS sobre `lo` | Comunicación local entre Python y MuJoCo. | Simulación local | Puede mostrar advertencia de multicast en `lo`; no necesariamente bloquea el flujo local. |
| `rt/lowcmd` | Envío de comandos articulares al simulador. | Unitree SDK2 / MuJoCo | El script publica posiciones, ganancias y amortiguamiento. |
| `rt/lowstate` | Lectura de estados articulares. | Unitree SDK2 / MuJoCo | Requiere sensores `jointpos`, `jointvel` y `actuatorfrc`. |
| `config.yaml` | Define robot, escena, dominio e interfaz. | Simulador | Debe apuntar a `robot: "r1"` e `interface: "lo"`. |

### 2.3 Diagrama textual de flujo

```text
MUJOCO R1/
|
|-- 04_rutinas_txt/dab.txt
|-- 04_rutinas_txt/siuu.txt
|
v
03_scripts_movimiento/r1_pose_player_mujoco.py
|
|-- lee rutina
|-- valida indices 12 a 25
|-- interpola posiciones
|-- aplica rampa de ganancias
v
Unitree SDK2 Python / DDS
|
|-- publica: rt/lowcmd
|-- recibe: rt/lowstate
v
Unitree MuJoCo
|
v
Modelo R1 corregido: r1.xml
```

---

## 3. Requisitos y Dependencias

El paquete presupone que el computador ya cuenta con una instalación funcional de Unitree MuJoCo. La carpeta `MUJOCO R1` no reemplaza todo el repositorio original de Unitree; entrega los archivos R1 finales y los scripts de poses.

### 3.1 Requisitos principales

| Requisito | Versión / Valor | Verificación |
|---|---|---|
| Sistema operativo | Ubuntu 20.04 recomendado | `lsb_release -a` |
| Python | Python 3 | `python3 --version` |
| Unitree MuJoCo | Repositorio funcional en `$HOME/unitree_mujoco` | `ls $HOME/unitree_mujoco` |
| Unitree SDK2 Python | Paquete `unitree_sdk2py` importable | `python3 -c "import unitree_sdk2py; print('OK')"` |
| MuJoCo library path | Ruta a `libmujoco.so.3.2.7` | `find $HOME/unitree_mujoco -name "libmujoco*"` |
| Interfaz local | `lo` para simulación local | `ip link show lo` |
| Modelo R1 corregido | `r1.xml` final del paquete | `grep -n "jointpos" r1.xml` |
| Config simulador | `robot: "r1"` y `enable_elastic_band: 1` | `cat simulate/config.yaml` |

### 3.2 Verificación de `unitree_sdk2py`

Ejecutar:

```bash
python3 --version
python3 -c "import unitree_sdk2py; print('unitree_sdk2py OK')"
```

Si aparece:

```text
ModuleNotFoundError: No module named 'unitree_sdk2py'
```

Instalar o exponer correctamente el paquete de Unitree SDK2 Python. Una instalación típica desde el repositorio local se realiza así:

```bash
cd ~/unitree_sdk2_python
pip3 install -e .
```

Si el repositorio está en otra ruta, cambiar `~/unitree_sdk2_python` por la ruta real.

### 3.3 Variable `LD_LIBRARY_PATH`

Para evitar errores de librería MuJoCo, ejecutar:

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/unitree_mujoco/simulate/mujoco/build/lib:/opt/unitree_robotics/lib
```

Para dejarlo permanente:

```bash
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/unitree_mujoco/simulate/mujoco/build/lib:/opt/unitree_robotics/lib' >> ~/.bashrc
source ~/.bashrc
```

---

## 4. Organización de Archivos

La entrega debe iniciar desde una carpeta llamada `MUJOCO R1`. Esta carpeta contiene los archivos específicos y finales del flujo R1.

### 4.1 Estructura esperada

```text
MUJOCO R1/
|-- 01_modelo_r1_final/
|   `-- unitree_robots/
|       `-- r1/
|           |-- r1.xml
|           |-- scene.xml
|           `-- meshes y assets del modelo R1
|
|-- 02_config_simulador/
|   `-- config.yaml
|
|-- 03_scripts_movimiento/
|   |-- r1_pose_player_mujoco.py
|   `-- r1_capture_pose.py
|
|-- 04_rutinas_txt/
|   |-- test_hold_actual.txt
|   |-- dab.txt
|   `-- siuu.txt
|
|-- 05_config_r1/
|   |-- r1_joint_map_final.json
|   `-- r1_safe_pose_final.json
|
|-- 06_herramientas_diagnostico/
|   `-- scripts auxiliares de prueba
|
|-- 07_instalacion/
|   `-- instalar_archivos_r1_en_unitree_mujoco.sh
|
|-- run_simulador_r1.sh
|-- run_dab.sh
|-- run_siuu.sh
|-- capturar_pose_r1.sh
`-- README.md
```

### 4.2 Archivos obligatorios

| Archivo | Uso | Obligatorio |
|---|---|---|
| `01_modelo_r1_final/unitree_robots/r1/r1.xml` | Modelo R1 corregido. | Sí |
| `01_modelo_r1_final/unitree_robots/r1/scene.xml` | Escena principal del R1. | Sí |
| `02_config_simulador/config.yaml` | Configuración final para abrir R1 en MuJoCo. | Sí |
| `03_scripts_movimiento/r1_pose_player_mujoco.py` | Ejecuta rutinas. | Sí |
| `03_scripts_movimiento/r1_capture_pose.py` | Captura nuevas poses. | Recomendado |
| `04_rutinas_txt/*.txt` | Rutinas de movimiento. | Sí |
| `07_instalacion/instalar_archivos_r1_en_unitree_mujoco.sh` | Copia modelo y configuración al repositorio Unitree MuJoCo. | Sí |

### 4.3 Rutas recomendadas

Se recomienda ubicar la carpeta en:

```bash
$HOME/Projects/unitree_lab/MUJOCO R1
```

El nombre contiene un espacio. Los scripts incluidos usan comillas internamente para soportarlo. Si se escriben comandos manuales, usar comillas:

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
```

---

## 5. Formato de Entrada

Las rutinas están escritas como JSON válido dentro de archivos `.txt`. Cada rutina contiene metadatos generales y una lista ordenada de pasos. Cada paso define un nombre, un diccionario de posiciones articulares y una duración en segundos.

### 5.1 Campos de una rutina

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `nombre_rutina` | string | Sí | Nombre lógico de la rutina. |
| `fecha_creacion` | string | Sí | Fecha de creación o actualización. |
| `descripcion` | string | Sí | Explicación breve del movimiento. |
| `numero_pasos` | entero | Sí | Número total de pasos en la lista `pasos`. |
| `pasos` | lista | Sí | Secuencia ordenada de posiciones. |
| `nombre` | string | Sí | Nombre descriptivo de cada paso. |
| `posiciones` | objeto | Sí | Pares `"indice": valor` en radianes. |
| `duracion` | número | Sí | Tiempo de transición o sostenimiento en segundos. |

### 5.2 Índices válidos

Las posiciones usan `Actuator_index`, no `Joint_index`. Para rutinas de pose se deben usar los índices 12 a 25.

| Índice | Articulación |
|---:|---|
| 12 | `waist_roll_joint` |
| 13 | `waist_yaw_joint` |
| 14 | `left_shoulder_pitch_joint` |
| 15 | `left_shoulder_roll_joint` |
| 16 | `left_shoulder_yaw_joint` |
| 17 | `left_elbow_joint` |
| 18 | `left_wrist_roll_joint` |
| 19 | `right_shoulder_pitch_joint` |
| 20 | `right_shoulder_roll_joint` |
| 21 | `right_shoulder_yaw_joint` |
| 22 | `right_elbow_joint` |
| 23 | `right_wrist_roll_joint` |
| 24 | `head_pitch_joint` |
| 25 | `head_yaw_joint` |

> **Advertencia crítica.** No usar índices 26 o superiores en rutinas R1. El mensaje `LowState` puede tener más espacios internos por estructura IDL, pero el R1 activo en esta simulación usa 26 actuadores reales, indexados de 0 a 25.

### 5.3 Pose segura obligatoria

Todas las rutinas deben iniciar y terminar en la siguiente pose segura:

```json
{
  "12": 0.0,
  "13": 0.0,
  "14": 0.0,
  "15": 0.151786,
  "16": 0.0,
  "17": 1.062987,
  "18": 0.0,
  "19": 0.0,
  "20": -0.151872,
  "21": 0.0,
  "22": 1.062987,
  "23": 0.0,
  "24": 0.0,
  "25": 0.0
}
```

### 5.4 Ejemplo mínimo funcional

```json
{
  "nombre_rutina": "ejemplo_minimo",
  "fecha_creacion": "2026-07-03",
  "descripcion": "Rutina minima R1 con pose segura.",
  "numero_pasos": 2,
  "pasos": [
    {
      "nombre": "Pose segura inicial",
      "posiciones": {
        "12": 0.0,
        "13": 0.0,
        "14": 0.0,
        "15": 0.151786,
        "16": 0.0,
        "17": 1.062987,
        "18": 0.0,
        "19": 0.0,
        "20": -0.151872,
        "21": 0.0,
        "22": 1.062987,
        "23": 0.0,
        "24": 0.0,
        "25": 0.0
      },
      "duracion": 1.0
    },
    {
      "nombre": "Pose segura final",
      "posiciones": {
        "12": 0.0,
        "13": 0.0,
        "14": 0.0,
        "15": 0.151786,
        "16": 0.0,
        "17": 1.062987,
        "18": 0.0,
        "19": 0.0,
        "20": -0.151872,
        "21": 0.0,
        "22": 1.062987,
        "23": 0.0,
        "24": 0.0,
        "25": 0.0
      },
      "duracion": 1.0
    }
  ]
}
```

---

## 6. Código Fuente y Funcionamiento Interno

### 6.1 Script principal: `r1_pose_player_mujoco.py`

Este script es el ejecutor de rutinas. Recibe como argumento la ruta de una rutina `.txt`, carga el JSON, valida los pasos, mantiene las piernas en una postura estable inicial y controla cintura, brazos y cabeza según los objetivos de la rutina.

#### 6.1.1 Responsabilidades principales

| Elemento | Responsabilidad | Entradas | Salidas / Efecto |
|---|---|---|---|
| Constantes R1 | Definen cantidad de motores y grupos articulares. | Código fuente | Mapeo estable de articulaciones |
| `gains_for_joint(i)` | Retorna `Kp` y `Kd` por articulación. | Índice de actuador | Ganancias de control |
| Carga de rutina | Lee y valida archivo JSON/TXT. | Ruta del archivo | Lista de pasos |
| Interpolación | Calcula transición gradual entre poses. | Pose inicial, pose objetivo, tiempo | Comando articular intermedio |
| Rampa de ganancias | Evita activar `Kp` / `Kd` de golpe. | Tiempo desde inicio | Escala progresiva de control |
| Publicación DDS | Envía `LowCmd`. | Posiciones y ganancias | Movimiento en MuJoCo |
| Cierre seguro | Detiene hilo recurrente y termina proceso. | Final de rutina o interrupción | Control detenido |

#### 6.1.2 Grupos articulares usados

```python
ACTIVE_MOTOR_COUNT = 26

LEG_JOINTS = list(range(0, 12))
WAIST_JOINTS = [12, 13]
LEFT_ARM_JOINTS = [14, 15, 16, 17, 18]
RIGHT_ARM_JOINTS = [19, 20, 21, 22, 23]
HEAD_JOINTS = [24, 25]

POSE_JOINTS = WAIST_JOINTS + LEFT_ARM_JOINTS + RIGHT_ARM_JOINTS + HEAD_JOINTS
```

#### 6.1.3 Ganancias finales

Las ganancias finales se ajustaron para eliminar `twitching` rápido y conservar suficiente autoridad de movimiento en brazos.

```python
def gains_for_joint(i):
    """
    Ganancias R1 finales.
    Objetivo: estabilidad en hold y movimientos suaves en rutinas.
    """
    if i in LEG_JOINTS:
        return 12.0, 0.8
    if i in WAIST_JOINTS:
        return 15.0, 1.0
    if i in [14, 15, 16, 17, 19, 20, 21, 22]:
        return 14.0, 1.2
    if i in [18, 23]:
        return 8.0, 0.8
    if i == 24:
        return 15.0, 0.8
    if i == 25:
        return 6.0, 0.4
    return 0.0, 0.0
```

#### 6.1.4 Rampa de activación

La rampa de activación fue necesaria porque el control entraba de forma brusca y generaba oscilaciones. El factor de escala inicia en 0 y llega a 1 en aproximadamente 2.5 segundos.

```python
def gain_scale(self):
    if self.writer_start_time is None:
        return 0.0
    elapsed = time.time() - self.writer_start_time
    return max(0.0, min(elapsed / self.gain_ramp_duration, 1.0))
```

### 6.2 Script de captura: `r1_capture_pose.py`

El script de captura lee `LowState`, imprime las posiciones actuales de los índices 12 a 25 y genera un bloque JSON listo para pegar en una rutina.

Flujo de captura:

1. Abrir MuJoCo con el R1.
2. Pausar la simulación si se desea mover sliders manualmente.
3. Posicionar cintura, brazos y cabeza.
4. Ejecutar `r1_capture_pose.py`.
5. Copiar el bloque JSON generado.

### 6.3 Modelo corregido: `r1.xml`

El modelo final contiene tres grupos de sensores en orden compatible con el bridge de Unitree MuJoCo:

1. `jointpos` para los 26 actuadores.
2. `jointvel` para los 26 actuadores.
3. `actuatorfrc` para los 26 actuadores.

> **Nota técnica.** El bridge usa `sensordata[i]` como posición, `sensordata[i + num_motor]` como velocidad y `sensordata[i + 2*num_motor]` como torque estimado. Si el XML no tiene los sensores en ese orden, el robot recibe estados incorrectos y se contorsiona.

---

## 7. Flujo de Ejecución

Esta sección describe el proceso desde la descarga de la carpeta `MUJOCO R1` hasta la ejecución de una rutina.

### 7.1 Paso 1: ubicar la carpeta descargada

Ejemplo recomendado:

```bash
mkdir -p "$HOME/Projects/unitree_lab"
mv "MUJOCO R1" "$HOME/Projects/unitree_lab/"
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
```

Verificar contenido:

```bash
ls
ls 03_scripts_movimiento
ls 04_rutinas_txt
```

### 7.2 Paso 2: verificar Unitree MuJoCo

```bash
ls "$HOME/unitree_mujoco"
ls "$HOME/unitree_mujoco/simulate/build"
```

Si `$HOME/unitree_mujoco` no existe, se debe instalar primero Unitree MuJoCo siguiendo el procedimiento oficial del repositorio de Unitree. Este paquete no reemplaza la instalación completa de MuJoCo.

### 7.3 Paso 3: instalar archivos R1 finales dentro de Unitree MuJoCo

Desde la carpeta `MUJOCO R1`:

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./07_instalacion/instalar_archivos_r1_en_unitree_mujoco.sh
```

Si el repositorio `unitree_mujoco` está en otra ruta:

```bash
./07_instalacion/instalar_archivos_r1_en_unitree_mujoco.sh /ruta/a/unitree_mujoco
```

El script realiza backups automáticos antes de sobrescribir `unitree_robots/r1` y `simulate/config.yaml`.

### 7.4 Paso 4: verificar `unitree_sdk2py`

```bash
python3 -c "import unitree_sdk2py; print('unitree_sdk2py OK')"
```

Si falla, instalar desde el repositorio local del SDK:

```bash
cd ~/unitree_sdk2_python
pip3 install -e .
```

Después verificar otra vez:

```bash
python3 -c "import unitree_sdk2py; print('unitree_sdk2py OK')"
```

### 7.5 Paso 5: abrir el simulador R1

Terminal 1:

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./run_simulador_r1.sh
```

Alternativamente, de forma manual:

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/unitree_mujoco/simulate/mujoco/build/lib:/opt/unitree_robotics/lib
cd "$HOME/unitree_mujoco/simulate/build"
./unitree_mujoco
```

El archivo `config.yaml` debe contener:

```yaml
robot: "r1"
robot_scene: "scene.xml"
domain_id: 0
interface: "lo"
print_scene_information: 1
enable_elastic_band: 1
```

### 7.6 Paso 6: ejecutar una rutina

Con MuJoCo abierto y el R1 estable, abrir Terminal 2.

Para ejecutar `siuu.txt`:

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./run_siuu.sh
```

Para ejecutar `dab.txt`:

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./run_dab.sh
```

El script mostrará:

```text
[ACCION] Verifica que el R1 este estable en MuJoCo. Presiona Enter para iniciar...
```

Verificar visualmente que el robot esté estable y presionar Enter. El script ejecutará la secuencia y terminará.

### 7.7 Paso 7: validar sintaxis de una rutina

Antes de ejecutar una rutina nueva:

```bash
python3 -m json.tool 04_rutinas_txt/siuu.txt > /tmp/siuu_check.json
python3 -m json.tool 04_rutinas_txt/dab.txt > /tmp/dab_check.json
```

### 7.8 Paso 8: capturar una nueva pose

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./capturar_pose_r1.sh
```

El script imprimirá una tabla de articulaciones y un bloque JSON. Copiar el bloque dentro de una nueva rutina.

---

## 8. Seguridad Operacional

> **Advertencia crítica.** Este paquete controla articulaciones del robot R1 en simulación mediante comandos de bajo nivel. Aunque el entorno descrito es MuJoCo, las rutinas y criterios de control no deben trasladarse directamente a robot físico sin revisión específica, límites de torque, validación de SDK físico y protocolos de seguridad.

### 8.1 Condiciones antes de ejecutar

Antes de ejecutar cualquier rutina:

- Confirmar que MuJoCo está abierto con el robot R1.
- Verificar que el robot está estable antes de presionar Enter.
- Confirmar que se está usando `interface: "lo"` en simulación local.
- Confirmar que la rutina inicia y termina en pose segura.
- Validar el archivo con `python3 -m json.tool`.

### 8.2 Qué no debe modificarse sin precaución

- No cambiar el orden de sensores en `r1.xml`.
- No usar `Joint_index` como si fuera `Actuator_index`.
- No subir `Kp` o `ctrlrange` de forma global.
- No usar índices 26 o superiores.
- No eliminar la rampa de ganancias sin reemplazarla por otro mecanismo de suavización.

### 8.3 Detención en simulación

Si el robot empieza a oscilar o moverse de forma inesperada:

1. Detener el script Python con `Ctrl+C`.
2. Detener MuJoCo con `Ctrl+C`.
3. Revisar la rutina ejecutada.
4. Validar que no haya posiciones extremas o duraciones demasiado cortas.
5. Reiniciar MuJoCo antes de reintentar.

### 8.4 Consideraciones para robot físico

Este documento no valida ejecución física sobre R1 real. Para robot físico se debe preparar una guía independiente que incluya interfaz de red real, tópicos físicos correctos, límites de torque reales, parada de emergencia física y validación de que el robot no esté caminando ni ejecutando otro modo.

---

## 9. Guía de Uso Rápido

### 9.1 Ejecución rápida de `siuu`

1. Abrir la carpeta.

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
```

2. Instalar archivos finales en `unitree_mujoco`.

```bash
./07_instalacion/instalar_archivos_r1_en_unitree_mujoco.sh
```

3. Abrir MuJoCo.

```bash
./run_simulador_r1.sh
```

4. En otra terminal, ejecutar la rutina.

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./run_siuu.sh
```

5. Esperar el mensaje de confirmación y presionar Enter.

### 9.2 Ejecución rápida de `dab`

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./run_dab.sh
```

---

## 10. Problemas Conocidos y Soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: unitree_sdk2py` | SDK2 Python no instalado o no visible. | Ejecutar `pip3 install -e .` dentro del repositorio `unitree_sdk2_python`. |
| Error de librería `libmujoco.so` | Falta `LD_LIBRARY_PATH`. | Exportar ruta a `simulate/mujoco/build/lib`. |
| MuJoCo abre otro robot | `config.yaml` no apunta a R1. | Verificar `robot: "r1"` y copiar configuración final. |
| Robot cae al abrir simulador | No se está usando `unitree_mujoco` correcto o falta `elastic_band`. | Verificar `enable_elastic_band: 1`. |
| No se recibe `LowState` | Dominio o interfaz incorrectos. | Usar `domain_id = 0` e `interface = lo`. |
| Advertencia `lo is not multicast-capable` | DDS sobre loopback. | En este flujo local puede aparecer y no necesariamente bloquea la ejecución. |
| Robot se contorsiona al enviar comando | XML sin sensores articulares o sensores en orden incorrecto. | Usar el `r1.xml` final del paquete. |
| Brazos no alcanzan la pose | `ctrlrange` demasiado bajo. | Usar el `r1.xml` final con rangos corregidos. |
| Robot convulsiona o hace `twitching` | Ganancias o `ctrlrange` demasiado altos. | Usar configuración final con rangos por grupo y rampa de ganancias. |
| Error de JSON | Coma faltante, llave mal cerrada o número no válido. | Ejecutar `python3 -m json.tool archivo.txt`. |
| La rutina no se encuentra | Ruta incorrecta o carpeta distinta. | Ejecutar desde `MUJOCO R1` o pasar ruta completa. |
| Movimiento muy brusco | Duraciones muy cortas o salto grande entre poses. | Agregar poses intermedias y aumentar duración. |
| El robot no vuelve bien a pose segura | La rutina no termina con la pose segura estándar. | Copiar la pose segura final desde `r1_safe_pose_final.json`. |

---

## 11. Extensión y Mantenimiento

### 11.1 Agregar una nueva rutina

Para crear una nueva rutina:

1. Abrir MuJoCo.
2. Posicionar el R1 con sliders.
3. Capturar una pose.

```bash
cd "$HOME/Projects/unitree_lab/MUJOCO R1"
./capturar_pose_r1.sh
```

Crear un archivo nuevo en `04_rutinas_txt/`:

```bash
nano 04_rutinas_txt/nueva_pose.txt
```

Validar JSON:

```bash
python3 -m json.tool 04_rutinas_txt/nueva_pose.txt > /tmp/nueva_pose_check.json
```

Ejecutar:

```bash
python3 03_scripts_movimiento/r1_pose_player_mujoco.py 04_rutinas_txt/nueva_pose.txt
```

### 11.2 Recomendaciones para rutinas nuevas

- Usar duraciones de 1.5 a 3 segundos para transiciones amplias.
- No saltar directamente de pose segura a una pose extrema.
- Agregar poses intermedias para movimientos expresivos.
- Evitar cambios rápidos de una sola articulación con amplitud grande.
- Mantener cabeza y muñecas con movimientos suaves.
- Probar primero con `test_hold_actual.txt`.

### 11.3 Validaciones después de modificar

```bash
python3 -m py_compile 03_scripts_movimiento/r1_pose_player_mujoco.py
python3 -m py_compile 03_scripts_movimiento/r1_capture_pose.py
python3 -m json.tool 04_rutinas_txt/dab.txt > /tmp/dab_check.json
python3 -m json.tool 04_rutinas_txt/siuu.txt > /tmp/siuu_check.json
```

---

## 12. Correcciones Técnicas Realizadas

| Problema encontrado | Solución aplicada | Archivo final |
|---|---|---|
| R1 no se sostenía correctamente en escena normal. | Se usó Unitree MuJoCo con `enable_elastic_band: 1`. | `02_config_simulador/config.yaml` |
| Error de librería MuJoCo al ejecutar. | Se agregó ruta de MuJoCo a `LD_LIBRARY_PATH`. | `run_simulador_r1.sh` |
| Confusión entre `Joint_index` y `Actuator_index`. | Se documentó y usó mapeo por actuador. | `r1_pose_player_mujoco.py`, `r1_capture_pose.py` |
| `LowState` devolvía datos no articulares. | Se agregaron sensores `jointpos`, `jointvel` y `actuatorfrc`. | `r1.xml` |
| Brazos no subían ni alcanzaban poses amplias. | Se corrigió `ctrlrange` de actuadores. | `r1.xml` |
| Convulsión global al subir `ctrlrange`. | Se redujeron límites por grupo articular. | `r1.xml` |
| `Twitching` rápido en brazos. | Se redujeron ganancias y se agregó rampa de activación. | `r1_pose_player_mujoco.py` |
| Rutinas sin estándar de seguridad. | Se definió pose segura obligatoria inicial y final. | `r1_safe_pose_final.json`, `dab.txt`, `siuu.txt` |

---

## 13. Resumen de Actividades

| Actividad | Estado | Observación |
|---|---|---|
| Inspección del modelo R1 | Completado | Se identificó mapeo real por actuadores y sensores faltantes. |
| Corrección de sensores en XML | Completado | Se agregaron sensores necesarios para `LowState`. |
| Corrección de límites de actuador | Completado | Se ajustó `ctrlrange` por grupo articular. |
| Ajuste de ganancias | Completado | Se logró estabilidad mediante ganancias suaves y rampa. |
| Validación de `test_hold_actual.txt` | Completado | Robot estable. |
| Validación de `dab.txt` | Completado | Rutina ejecutable desde el paquete. |
| Validación de `siuu.txt` | Completado | Rutina validada como funcional y estable. |
| Organización de carpeta `MUJOCO R1` | Completado | Incluye modelo, scripts, rutinas, config y README. |
| Documentación técnica | Completado | Este documento funciona como guía reproducible. |
| Validación en robot físico | Pendiente | No incluida en el alcance de esta versión. Requiere protocolo separado. |

---

## Cierre técnico

El paquete **MUJOCO R1** queda como una entrega reproducible para simulación de poses del Unitree R1. La versión final permite instalar los archivos corregidos sobre una instalación existente de `unitree_mujoco`, ejecutar rutinas incluidas, capturar nuevas poses y extender el catálogo de movimientos manteniendo criterios mínimos de seguridad, estabilidad y trazabilidad técnica.

---

**Robotics 4.0**  
www.robotics40.com  
ceo@robotics40.com
