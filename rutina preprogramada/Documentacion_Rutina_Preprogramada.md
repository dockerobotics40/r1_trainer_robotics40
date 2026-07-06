# Documentación técnica: Rutina Preprogramada de Trayectoria Cuadrada

**Control de locomoción para robot Unitree R1 EDU mediante Unitree R1 LocoClient**

| Campo | Detalle |
|---|---|
| Paquete / Script | `r1_square_mode.cpp` |
| Versión | Documento técnico v1.0 |
| Plataforma | Linux / C++ / entorno de compilación compatible con Unitree SDK |
| Robot / Hardware | Unitree R1 EDU |
| SDK / Framework | Unitree R1 Loco API, `r1_loco_client.hpp`, `ChannelFactory` |
| Script base | Rutina C++ de locomoción por velocidad con `LocoClient` |
| Autor | Robotics 4.0 |
| Fecha | 30 de junio de 2026 |

Documento interno para reproducción, operación, diagnóstico y mantenimiento técnico.

---

## Índice

1. [Descripción general](#1-descripción-general)
   - [1.1. Problema que resuelve](#11-problema-que-resuelve)
   - [1.2. Entradas, procesamiento y salida](#12-entradas-procesamiento-y-salida)
   - [1.3. Componentes desarrollados](#13-componentes-desarrollados)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
   - [2.1. Descripción por capas](#21-descripción-por-capas)
   - [2.2. Comunicación e interfaces](#22-comunicación-e-interfaces)
   - [2.3. Trayectoria ejecutada](#23-trayectoria-ejecutada)
3. [Requisitos y dependencias](#3-requisitos-y-dependencias)
   - [3.1. Requisitos mínimos](#31-requisitos-mínimos)
   - [3.2. Comandos de verificación](#32-comandos-de-verificación)
4. [Organización de archivos](#4-organización-de-archivos)
   - [4.1. Estructura recomendada](#41-estructura-recomendada)
   - [4.2. Archivos obligatorios](#42-archivos-obligatorios)
   - [4.3. Nombres y rutas](#43-nombres-y-rutas)
5. [Formato de entrada](#5-formato-de-entrada)
   - [5.1. Campos de entrada](#51-campos-de-entrada)
   - [5.2. Ejemplo mínimo funcional](#52-ejemplo-mínimo-funcional)
   - [5.3. Validación de entrada](#53-validación-de-entrada)
6. [Código fuente y funcionamiento interno](#6-código-fuente-y-funcionamiento-interno)
   - [6.1. Importaciones](#61-importaciones)
   - [6.2. Inicialización de comunicación](#62-inicialización-de-comunicación)
   - [6.3. Captura de parámetros](#63-captura-de-parámetros)
   - [6.4. Cálculo temporal](#64-cálculo-temporal)
   - [6.5. Secuencia de activación](#65-secuencia-de-activación)
   - [6.6. Margen de espera entre lados](#66-margen-de-espera-entre-lados)
   - [6.7. Comandos de movimiento](#67-comandos-de-movimiento)
   - [6.8. Cierre de movimiento](#68-cierre-de-movimiento)
   - [6.9. Código fuente completo de referencia](#69-código-fuente-completo-de-referencia)
7. [Flujo de ejecución](#7-flujo-de-ejecución)
   - [7.1. Preparación del entorno](#71-preparación-del-entorno)
   - [7.2. Compilación sugerida](#72-compilación-sugerida)
   - [7.3. Ejecución](#73-ejecución)
   - [7.4. Verificación del resultado](#74-verificación-del-resultado)
8. [Seguridad operacional](#8-seguridad-operacional)
   - [8.1. Condiciones antes de ejecutar](#81-condiciones-antes-de-ejecutar)
   - [8.2. Acciones no recomendadas](#82-acciones-no-recomendadas)
   - [8.3. Detención segura](#83-detención-segura)
   - [8.4. Interrupción con Ctrl+C](#84-interrupción-con-ctrlc)
9. [Guía de uso rápido](#9-guía-de-uso-rápido)
10. [Problemas conocidos y soluciones](#10-problemas-conocidos-y-soluciones)
11. [Extensión y mantenimiento](#11-extensión-y-mantenimiento)
    - [11.1. Agregar pausa explícita entre lados](#111-agregar-pausa-explícita-entre-lados)
    - [11.2. Agregar trayectoria con giro](#112-agregar-trayectoria-con-giro)
    - [11.3. Parametrizar la interfaz de red](#113-parametrizar-la-interfaz-de-red)
    - [11.4. Agregar límites máximos de seguridad](#114-agregar-límites-máximos-de-seguridad)
    - [11.5. Partes que no deben modificarse sin precaución](#115-partes-que-no-deben-modificarse-sin-precaución)
    - [11.6. Validación posterior a modificaciones](#116-validación-posterior-a-modificaciones)
12. [Resumen de actividades](#12-resumen-de-actividades)
13. [Conclusión técnica](#13-conclusión-técnica)

---

## 1. Descripción general

Esta documentación describe una rutina preprogramada en C++ para ejecutar una trayectoria cuadrada con el robot **Unitree R1 EDU**. El programa controla la locomoción mediante comandos temporizados de velocidad lineal enviados a través de `unitree::robot::r1::LocoClient`.

La lógica del sistema es directa: el usuario ingresa por terminal la longitud del lado del cuadrado y la velocidad de desplazamiento. El programa calcula el tiempo requerido para cada lado usando la relación física:

```text
tiempo = distancia / velocidad
```

Después activa el cliente de locomoción y ejecuta cuatro comandos secuenciales de velocidad: avance, desplazamiento lateral izquierdo, retroceso y desplazamiento lateral derecho. Al finalizar, envía una orden explícita de detención mediante `StopMove()`.

> **Objetivo operativo:** permitir que el robot R1 EDU ejecute una trayectoria cuadrada aproximada sin programar puntos de navegación ni depender de un sistema de odometría cerrada. La rutina es útil para pruebas iniciales de locomoción, validación de comunicación SDK, demostraciones controladas y verificación básica de respuesta en los ejes X/Y.

### 1.1. Problema que resuelve

En pruebas de locomoción robótica es frecuente requerir rutinas simples, repetibles y parametrizables. Este código reemplaza un flujo manual donde el operador tendría que enviar comandos individuales para cada tramo del movimiento. La herramienta centraliza el cálculo temporal, la secuencia de comandos y la detención final en un único programa ejecutable.

### 1.2. Entradas, procesamiento y salida

| Etapa | Descripción | Resultado |
|---|---|---|
| Entrada | El operador ingresa distancia del lado en metros y velocidad en metros por segundo. | Parámetros numéricos `distance` y `speed`. |
| Validación | El programa comprueba que distancia y velocidad sean mayores que cero. | Ejecución permitida o terminación con error. |
| Procesamiento | Calcula `duration = distance / speed`. | Tiempo de ejecución para cada lado del cuadrado. |
| Ejecución | Envía cuatro comandos `SetVelocity(vx, vy, wz, duration)`. | Desplazamiento secuencial en +X, +Y, -X y -Y. |
| Salida | Ejecuta `StopMove()`. | Robot detenido al finalizar la rutina. |

### 1.3. Componentes desarrollados

| Componente | Tipo | Descripción | Estado |
|---|---|---|---|
| `r1_square_mode.cpp` | Script C++ | Programa principal que inicializa comunicación, recibe parámetros, calcula duración y ejecuta los cuatro lados del cuadrado. | Implementado |
| `LocoClient` | Cliente SDK | Interfaz de locomoción del R1 utilizada para iniciar, controlar velocidad y detener movimiento. | Requerido |
| `ChannelFactory` | Comunicación SDK | Inicializa el canal de red con el robot mediante una interfaz Ethernet específica. | Requerido |
| Terminal de usuario | Interfaz textual | Permite ingresar distancia y velocidad de ejecución. | Implementado |
| Control temporizado | Lógica interna | Calcula duración por lado y añade margen de espera de 500 ms entre comandos. | Implementado |
| `StopMove()` | Cierre operacional | Orden explícita de detención al finalizar la trayectoria. | Implementado |

---

## 2. Arquitectura del sistema

La herramienta opera sobre una arquitectura de control por comandos de velocidad. El computador que ejecuta el programa se comunica con el robot R1 EDU mediante una interfaz Ethernet configurada en el SDK de Unitree. El programa no crea un nodo ROS2 propio ni publica tópicos directamente; su canal operativo principal es el cliente de locomoción `LocoClient`.

> **Modelo de ejecución:** la rutina es de lazo abierto. Calcula cuánto tiempo debe mantenerse una velocidad, pero no corrige la trayectoria con odometría, percepción, localización ni realimentación de posición. Por tanto, el cuadrado real puede variar según superficie, fricción, respuesta dinámica del robot y latencia de comunicación.

### 2.1. Descripción por capas

| Capa / Módulo | Función | Entrada | Salida |
|---|---|---|---|
| Operador | Define los parámetros físicos de la trayectoria. | Distancia y velocidad. | Valores capturados por `std::cin`. |
| Programa C++ | Valida entradas, calcula duración y ejecuta la secuencia. | `distance`, `speed`. | Comandos `SetVelocity`. |
| Unitree SDK | Gestiona comunicación y abstracción de locomoción. | Llamadas a `LocoClient`. | Paquetes de control hacia el robot. |
| Red Ethernet | Transporta los mensajes entre computador y robot. | Interfaz definida en `network_interface`. | Comunicación física con R1 EDU. |
| Robot R1 EDU | Ejecuta la locomoción solicitada. | Velocidades `vx`, `vy`, `wz`. | Movimiento físico sobre el plano. |

### 2.2. Comunicación e interfaces

| Canal / Interfaz | Uso | Entorno | Observación |
|---|---|---|---|
| `eth10` | Interfaz Ethernet declarada en el código. | Computador conectado al robot. | Debe cambiarse si la interfaz real tiene otro nombre. |
| `ChannelFactory::Instance()->Init(0, interface)` | Inicialización de comunicación Unitree. | SDK C++. | El parámetro `0` corresponde al modo de comunicación de red para robot físico. |
| `LocoClient::Init()` | Inicializa el cliente de locomoción. | Proceso C++. | Debe ejecutarse antes de enviar comandos. |
| `LocoClient::SetTimeout(10.f)` | Define tiempo máximo de espera. | Proceso C++. | Permite detectar bloqueos o falta de respuesta del SDK. |
| `SetVelocity(vx, vy, wz, duration)` | Envía velocidad lineal/angular durante un intervalo. | Robot físico. | Controla movimiento en X/Y y yaw. |
| `StopMove()` | Detiene la locomoción. | Robot físico. | Debe ejecutarse al finalizar la rutina. |

### 2.3. Trayectoria ejecutada

La rutina no gira el robot noventa grados en cada esquina. El robot conserva aproximadamente su orientación inicial y se desplaza de forma translacional sobre los ejes del marco de locomoción utilizado por el SDK.

```text
Inicio
-> Lado 1: vx = +speed, vy = 0,      wz = 0
-> Lado 2: vx = 0,      vy = +speed, wz = 0
-> Lado 3: vx = -speed, vy = 0,      wz = 0
-> Lado 4: vx = 0,      vy = -speed, wz = 0
Fin
-> StopMove()
```

---

## 3. Requisitos y dependencias

La ejecución requiere un entorno capaz de compilar C++ y acceder a las cabeceras/librerías del SDK de Unitree para el R1. Además, el computador debe tener comunicación de red funcional con el robot.

### 3.1. Requisitos mínimos

| Requisito | Versión / Valor | Verificación |
|---|---|---|
| Sistema operativo | Linux compatible con SDK Unitree. | `uname -a` |
| Compilador C++ | C++17 recomendado. | `g++ --version` |
| CMake | Recomendado si se integra al proyecto SDK. | `cmake --version` |
| SDK Unitree R1 | Cabeceras `r1_loco_api.hpp` y `r1_loco_client.hpp`. | Verificar rutas `include/unitree/robot/r1/loco/`. |
| Red Ethernet | Interfaz conectada al robot, por defecto `eth10`. | `ip link show` |
| Robot | Unitree R1 EDU encendido y en estado seguro para locomoción. | Confirmación visual y estado operativo del robot. |
| Área de prueba | Superficie despejada, plana y con espacio suficiente. | Inspección física antes de ejecutar. |

### 3.2. Comandos de verificación

```bash
uname -a
g++ --version
cmake --version
ip link show
ip addr show eth10
```

Si la interfaz `eth10` no existe, debe identificarse la interfaz real conectada al robot:

```bash
ip link show
ip addr
```

> **Condición crítica:** no ejecutar la rutina si no se ha confirmado la interfaz de red correcta. Una interfaz incorrecta puede impedir el envío de comandos o dejar el programa esperando respuesta del SDK.

---

## 4. Organización de archivos

La rutina puede integrarse en un proyecto existente del SDK Unitree o mantenerse como un ejemplo propio dentro del repositorio de trabajo de Robotics 4.0. La recomendación es conservar una carpeta específica para pruebas del R1 y nombrar el archivo de forma explícita.

### 4.1. Estructura recomendada

```text
r1_loco_routines/
├── CMakeLists.txt
├── src/
│   └── r1_square_mode.cpp
├── build/
└── README.md
```

### 4.2. Archivos obligatorios

| Archivo / Carpeta | Obligatorio | Función |
|---|---|---|
| `src/r1_square_mode.cpp` | Sí | Contiene la rutina principal de trayectoria cuadrada. |
| `CMakeLists.txt` | Sí, si se compila con CMake | Define el ejecutable y enlaza dependencias del SDK. |
| Cabeceras Unitree | Sí | Proveen las clases `LocoClient` y `ChannelFactory`. |
| `build/` | No inicial | Carpeta generada durante la compilación. |
| `README.md` | Opcional | Registro breve de uso interno. |

### 4.3. Nombres y rutas

El código no depende de archivos externos de configuración. Sin embargo, sí depende del nombre de interfaz definido en esta línea:

```cpp
std::string network_interface = "eth10";
```

Si el computador usa otro nombre de interfaz, esta variable debe modificarse antes de compilar. Se recomienda evitar nombres ambiguos y documentar en el `README.md` cuál interfaz corresponde a la conexión física con el robot.

---

## 5. Formato de entrada

La herramienta no consume archivos JSON, TXT, YAML ni CSV. Su entrada es interactiva por terminal. El operador debe ingresar dos valores numéricos de tipo flotante.

### 5.1. Campos de entrada

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `distance` | `float` | metros | Longitud de cada lado del cuadrado. Debe ser mayor que cero. |
| `speed` | `float` | metros/segundo | Velocidad lineal aplicada en cada lado. Debe ser mayor que cero. |

### 5.2. Ejemplo mínimo funcional

Entrada sugerida para una prueba conservadora:

```text
=== MODO CUADRADO ===
Ingresa la longitud del lado del cuadrado (en metros, ej. 1.0): 0.5
Ingresa la velocidad (m/s, ej. 0.2): 0.2
```

Con estos valores, el programa calcula:

```text
duration = distance / speed = 0.5 m / 0.2 m/s = 2.5 s
```

Cada lado se ejecutará durante aproximadamente **2.5 segundos**, más el margen de espera interno de **0.5 segundos** antes de pasar al siguiente comando.

### 5.3. Validación de entrada

El programa termina con error si cualquiera de los dos valores es menor o igual a cero:

```cpp
if (speed <= 0 || distance <= 0) {
    std::cerr << "Error: La velocidad y la distancia deben ser mayores a 0." << std::endl;
    return 1;
}
```

---

## 6. Código fuente y funcionamiento interno

Esta sección explica la lógica interna del código por bloques funcionales. La rutina se implementa dentro de la función `main()`, sin clases auxiliares propias ni archivos de configuración externos.

### 6.1. Importaciones

```cpp
#include <chrono>
#include <iostream>
#include <thread>
#include <vector>

#include "unitree/robot/r1/loco/r1_loco_api.hpp"
#include "unitree/robot/r1/loco/r1_loco_client.hpp"
```

| Elemento | Responsabilidad |
|---|---|
| `chrono` | Manejo de duraciones y pausas temporales. |
| `iostream` | Entrada y salida por terminal. |
| `thread` | Ejecución de pausas con `std::this_thread::sleep_for`. |
| `vector` | Incluida, pero no utilizada en esta versión. Puede eliminarse sin afectar la lógica actual. |
| `r1_loco_api.hpp` | API de locomoción del R1. |
| `r1_loco_client.hpp` | Cliente C++ para enviar comandos de locomoción. |

### 6.2. Inicialización de comunicación

```cpp
std::string network_interface = "eth10";
unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);

unitree::robot::r1::LocoClient client;
client.Init();
client.SetTimeout(10.f);
```

| Elemento | Función | Riesgo si falla |
|---|---|---|
| `network_interface` | Define la interfaz Ethernet usada para comunicarse con el robot. | Sin comunicación con el R1. |
| `ChannelFactory::Init` | Inicializa la capa de comunicación del SDK. | El cliente no puede enviar comandos. |
| `client.Init()` | Prepara el cliente de locomoción. | Fallo de ejecución o comandos ignorados. |
| `client.SetTimeout(10.f)` | Establece tiempo máximo de espera de 10 segundos. | Bloqueos prolongados si hay problemas de red. |

### 6.3. Captura de parámetros

```cpp
float distance = 0.0f;
float speed = 0.2f;

std::cout << "=== MODO CUADRADO ===" << std::endl;
std::cout << "Ingresa la longitud del lado del cuadrado (en metros, ej. 1.0): ";
std::cin >> distance;
std::cout << "Ingresa la velocidad (m/s, ej. 0.2): ";
std::cin >> speed;
```

El valor por defecto de `speed` es `0.2f`, pero se sobrescribe cuando el usuario ingresa una velocidad por terminal.

### 6.4. Cálculo temporal

```cpp
float duration = distance / speed;
```

El cálculo representa una aproximación cinemática simple:

```text
t = d / v
```

Donde `t` es el tiempo por lado, `d` es la distancia del lado y `v` es la velocidad lineal. El programa no mide el desplazamiento real ni corrige errores acumulados.

### 6.5. Secuencia de activación

```cpp
std::cout << "\nIniciando secuencia en 3 segundos. ¡Despeja el área!" << std::endl;
std::this_thread::sleep_for(std::chrono::seconds(3));

client.Start();
std::this_thread::sleep_for(std::chrono::seconds(1));
```

La pausa inicial de **3 segundos** permite despejar el área. Luego, `client.Start()` activa el cliente de locomoción antes de enviar los comandos de velocidad.

### 6.6. Margen de espera entre lados

```cpp
int sleep_ms = static_cast<int>(duration * 1000) + 500;
```

El programa espera el tiempo de ejecución del movimiento más **500 ms**. Este margen busca evitar transiciones inmediatas entre direcciones opuestas o perpendiculares.

### 6.7. Comandos de movimiento

```cpp
client.SetVelocity(speed, 0.0f, 0.0f, duration);   // +X
std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

client.SetVelocity(0.0f, speed, 0.0f, duration);   // +Y
std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

client.SetVelocity(-speed, 0.0f, 0.0f, duration);  // -X
std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

client.SetVelocity(0.0f, -speed, 0.0f, duration);  // -Y
std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));
```

| Paso | Movimiento | `vx` | `vy` | `wz` | Efecto |
|---|---|---:|---:|---:|---|
| 1 | Adelante | `+speed` | `0` | `0` | Avance longitudinal. |
| 2 | Izquierda | `0` | `+speed` | `0` | Desplazamiento lateral. |
| 3 | Atrás | `-speed` | `0` | `0` | Retroceso longitudinal. |
| 4 | Derecha | `0` | `-speed` | `0` | Retorno lateral. |

### 6.8. Cierre de movimiento

```cpp
std::cout << "Cuadrado completado. Deteniendo robot." << std::endl;
client.StopMove();
```

La función `StopMove()` es la acción de cierre más importante del programa. Sin esta llamada, el robot podría no recibir una orden explícita de finalización desde el proceso del usuario.

### 6.9. Código fuente completo de referencia

```cpp
#include <chrono>
#include <iostream>
#include <thread>
#include <vector>

#include "unitree/robot/r1/loco/r1_loco_api.hpp"
#include "unitree/robot/r1/loco/r1_loco_client.hpp"

int main() {
  // 1. Inicialización de la red (Ajusta "eth10" a tu interfaz real si es necesario)
  std::string network_interface = "eth10";
  unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);

  unitree::robot::r1::LocoClient client;
  client.Init();
  client.SetTimeout(10.f);

  // 2. Pedir dimensiones al usuario en la terminal
  float distance = 0.0f;
  float speed = 0.2f;

  std::cout << "=== MODO CUADRADO ===" << std::endl;
  std::cout << "Ingresa la longitud del lado del cuadrado (en metros, ej. 1.0): ";
  std::cin >> distance;
  std::cout << "Ingresa la velocidad (m/s, ej. 0.2): ";
  std::cin >> speed;

  if (speed <= 0 || distance <= 0) {
    std::cerr << "Error: La velocidad y la distancia deben ser mayores a 0." << std::endl;
    return 1;
  }

  // 3. Cálculo de la duración
  // Fórmula física básica: Tiempo = Distancia / Velocidad
  float duration = distance / speed;

  std::cout << "\nResumen: El robot recorrera " << distance << "m a " << speed
            << "m/s." << std::endl;
  std::cout << "Tiempo por lado: " << duration << " segundos." << std::endl;

  std::cout << "\nIniciando secuencia en 3 segundos. ¡Despeja el área!" << std::endl;
  std::this_thread::sleep_for(std::chrono::seconds(3));

  client.Start();  // Asegura que el robot esté activo
  std::this_thread::sleep_for(std::chrono::seconds(1));

  // Margen de seguridad: Agregamos 0.5s de pausa entre movimientos para estabilizar
  int sleep_ms = static_cast<int>(duration * 1000) + 500;

  // 4. Secuencia del Cuadrado (Desplazamiento Translacional)
  // LADO 1: Hacia adelante (+X)
  std::cout << "[1/4] Moviendo hacia adelante..." << std::endl;
  client.SetVelocity(speed, 0.0f, 0.0f, duration);
  std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

  // LADO 2: Hacia la izquierda (+Y)
  std::cout << "[2/4] Moviendo hacia la izquierda..." << std::endl;
  client.SetVelocity(0.0f, speed, 0.0f, duration);
  std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

  // LADO 3: Hacia atrás (-X)
  std::cout << "[3/4] Moviendo hacia atrás..." << std::endl;
  client.SetVelocity(-speed, 0.0f, 0.0f, duration);
  std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

  // LADO 4: Hacia la derecha (-Y)
  std::cout << "[4/4] Moviendo hacia la derecha..." << std::endl;
  client.SetVelocity(0.0f, -speed, 0.0f, duration);
  std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));

  // 5. Finalizar
  std::cout << "Cuadrado completado. Deteniendo robot." << std::endl;
  client.StopMove();

  return 0;
}
```

---

## 7. Flujo de ejecución

El flujo de ejecución debe realizarse de forma controlada. Antes de correr el programa, se debe comprobar que el robot esté en un área segura, que la interfaz Ethernet sea correcta y que el binario haya sido compilado sin errores.

### 7.1. Preparación del entorno

1. Conectar el computador al robot R1 EDU mediante Ethernet.
2. Verificar el nombre de la interfaz de red.
3. Ajustar `network_interface` en el código si no corresponde a `eth10`.
4. Confirmar que las cabeceras del SDK estén disponibles.
5. Compilar el ejecutable.

### 7.2. Compilación sugerida

Si el código se integra en un proyecto CMake existente del SDK, crear o adaptar un `CMakeLists.txt`. La estructura exacta de enlazado puede variar según la instalación del SDK; el siguiente bloque muestra una base de referencia que debe ajustarse a las librerías disponibles del proyecto Unitree local.

```cmake
cmake_minimum_required(VERSION 3.10)
project(r1_loco_routines)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(r1_square_mode src/r1_square_mode.cpp)

# Ajustar estas líneas según la estructura real del SDK Unitree instalado.
# target_include_directories(r1_square_mode PRIVATE /ruta/al/unitree_sdk/include)
# target_link_libraries(r1_square_mode PRIVATE unitree_sdk2)
```

Construcción del ejecutable:

```bash
cd r1_loco_routines
mkdir -p build
cd build
cmake ..
make -j$(nproc)
```

### 7.3. Ejecución

```bash
cd r1_loco_routines/build
./r1_square_mode
```

Durante la ejecución, ingresar valores conservadores para la primera prueba:

```text
Distancia: 0.3
Velocidad: 0.1
```

Estos valores reducen el desplazamiento inicial y permiten verificar que los signos de los ejes X/Y correspondan al comportamiento esperado del robot.

### 7.4. Verificación del resultado

| Elemento a verificar | Comportamiento esperado | Acción si falla |
|---|---|---|
| Comunicación | El programa avanza después de `client.Start()`. | Revisar interfaz Ethernet y conexión física. |
| Lado 1 | Movimiento hacia adelante. | Revisar convención de ejes o modo de locomoción. |
| Lado 2 | Movimiento lateral hacia la izquierda. | Confirmar si el robot permite desplazamiento lateral en el modo activo. |
| Lado 3 | Movimiento hacia atrás. | Reducir velocidad si hay inestabilidad. |
| Lado 4 | Movimiento lateral hacia la derecha. | Verificar que no existan obstáculos en el retorno. |
| Final | El robot se detiene al ejecutar `StopMove()`. | Usar parada física si no se detiene. |

---

## 8. Seguridad operacional

Esta rutina controla movimiento físico del robot. Por tanto, debe tratarse como una ejecución de hardware real, no como una prueba puramente de software.

> **Advertencia crítica:** antes de ejecutar el programa, despejar completamente el área alrededor del robot. La trayectoria esperada es cuadrada, pero el movimiento real puede desviarse por fricción, latencia, deriva de orientación, saturaciones del controlador o errores de configuración de red.

### 8.1. Condiciones antes de ejecutar

- El robot debe estar encendido, estable y en modo apto para locomoción.
- El área debe estar libre de personas, cables, mesas, paredes y objetos bajos.
- La superficie debe ser plana y no deslizante.
- La interfaz de red debe estar confirmada con `ip link show`.
- La velocidad inicial debe ser conservadora.
- El operador debe tener acceso inmediato a una parada de emergencia física.

### 8.2. Acciones no recomendadas

- No ejecutar la rutina si el robot ya está en otro modo de movimiento autónomo.
- No combinar la prueba con navegación, SLAM, teleoperación o control remoto simultáneo.
- No iniciar con distancias largas ni velocidades altas.
- No modificar los signos de `vx` o `vy` sin una prueba corta previa.
- No usar `Ctrl+C` como salida normal, porque puede interrumpir el programa antes de ejecutar `StopMove()`.

### 8.3. Detención segura

La salida normal del programa ocurre al completar los cuatro lados y ejecutar:

```cpp
client.StopMove();
```

Si el robot presenta comportamiento inesperado, se debe priorizar la parada física o el método de seguridad definido por el fabricante. Luego se debe revisar la configuración antes de volver a ejecutar.

### 8.4. Interrupción con Ctrl+C

El código actual no implementa un manejador de señales. Si se interrumpe el proceso con `Ctrl+C`, no está garantizado que `StopMove()` se ejecute. Para una versión de producción, se recomienda agregar manejo de `SIGINT` para llamar una función de cierre seguro.

> **Mejora recomendada:** implementar un manejador de interrupción que invoque `StopMove()` antes de terminar el proceso. Esto aumenta la seguridad cuando el operador necesita abortar la rutina desde terminal.

---

## 9. Guía de uso rápido

Esta guía resume el uso para operadores que ya conocen el entorno y solo necesitan ejecutar la rutina.

1. Conectar el computador al Unitree R1 EDU por Ethernet.
2. Verificar la interfaz:

```bash
ip link show
```

3. Editar el código si la interfaz no es `eth10`:

```cpp
std::string network_interface = "eth10";
```

4. Compilar:

```bash
cd r1_loco_routines
mkdir -p build && cd build
cmake ..
make -j$(nproc)
```

5. Ejecutar:

```bash
./r1_square_mode
```

6. Ingresar una distancia y velocidad conservadoras.
7. Verificar que el robot ejecute los cuatro lados.
8. Confirmar que al final aparezca el mensaje de detención y se ejecute `StopMove()`.

---

## 10. Problemas conocidos y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| No compila por cabecera no encontrada | Las rutas del SDK Unitree no están incluidas en el proyecto. | Ajustar `target_include_directories` o compilar dentro del árbol de ejemplos del SDK. |
| Error de enlazado | Falta enlazar la librería correspondiente del SDK. | Revisar el `CMakeLists.txt` usado por ejemplos oficiales del R1 y replicar las librerías necesarias. |
| El programa no se comunica con el robot | `network_interface` no corresponde a la interfaz real. | Ejecutar `ip link show`, identificar la interfaz Ethernet correcta y recompilar. |
| La interfaz aparece inactiva | Cable desconectado, interfaz abajo o configuración de red incorrecta. | Revisar cableado, ejecutar `ip addr`, activar interfaz si aplica. |
| El robot no se mueve | Cliente no inicializado, robot en modo no apto o comando no aceptado. | Verificar estado del robot, ejecutar primero una prueba mínima y revisar mensajes del SDK. |
| Movimiento lateral incorrecto | Convención de eje Y distinta o modo de locomoción limitado. | Realizar prueba corta con `vy = +0.1` y confirmar dirección real. |
| El cuadrado queda deformado | Rutina de lazo abierto sin odometría ni corrección de yaw. | Reducir velocidad, usar superficie plana o implementar control con realimentación. |
| Movimiento brusco entre lados | Cambio directo entre velocidades perpendiculares u opuestas. | Agregar `StopMove()` y pausa corta entre lados. |
| El robot se desvía de orientación | Pequeña deriva de yaw durante la locomoción. | Implementar corrección de orientación o reducir duración/velocidad. |
| Valores de entrada inválidos | Distancia o velocidad menor o igual a cero. | Ingresar valores positivos. El programa ya bloquea estos casos. |
| El proceso se interrumpe con `Ctrl+C` | No existe manejador de señales. | Usar parada física si es necesario y agregar manejo de `SIGINT` en una versión posterior. |

---

## 11. Extensión y mantenimiento

La herramienta puede ampliarse sin alterar su principio operativo. Las modificaciones deben mantener la secuencia lógica: validar entrada, calcular duración o parámetros, activar locomoción, ejecutar comandos y cerrar con `StopMove()`.

### 11.1. Agregar pausa explícita entre lados

Para aumentar estabilidad, puede insertarse una detención corta entre movimientos:

```cpp
client.StopMove();
std::this_thread::sleep_for(std::chrono::milliseconds(300));
```

Esta modificación reduce transiciones bruscas y facilita observar cada segmento por separado.

### 11.2. Agregar trayectoria con giro

La versión actual no rota el robot. Para una rutina tipo “avanzar y girar 90 grados”, se debe usar velocidad angular `wz` o una API específica de orientación si el SDK la proporciona. La extensión debe documentar claramente la unidad usada para `wz` y validar el sentido de giro antes de ejecutar distancias largas.

### 11.3. Parametrizar la interfaz de red

En lugar de dejar `eth10` fijo, se puede recibir la interfaz como argumento:

```cpp
int main(int argc, char** argv) {
    std::string network_interface = "eth10";
    if (argc > 1) {
        network_interface = argv[1];
    }

    unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);
    // ... resto del programa
}
```

Ejecución:

```bash
./r1_square_mode eth0
```

### 11.4. Agregar límites máximos de seguridad

Se recomienda limitar distancia y velocidad para evitar entradas accidentales:

```cpp
const float MAX_DISTANCE = 2.0f;
const float MAX_SPEED = 0.4f;

if (distance > MAX_DISTANCE || speed > MAX_SPEED) {
    std::cerr << "Error: parámetros por encima del límite seguro." << std::endl;
    return 1;
}
```

### 11.5. Partes que no deben modificarse sin precaución

| Elemento | Motivo |
|---|---|
| `ChannelFactory::Instance()->Init(0, network_interface)` | Define el modo y canal de comunicación con el robot. Un cambio incorrecto puede impedir control físico. |
| `client.Init()` | Inicializa el cliente requerido para comandos posteriores. |
| `client.Start()` | Activa el sistema antes de enviar velocidades. |
| `client.StopMove()` | Cierre operativo esencial para detener el movimiento. |
| Signos de `vx` y `vy` | Determinan la dirección real del movimiento. Deben validarse con pruebas cortas. |

### 11.6. Validación posterior a modificaciones

Después de cualquier cambio, ejecutar el siguiente protocolo:

1. Compilar sin advertencias críticas.
2. Probar con distancia menor o igual a `0.3 m`.
3. Probar con velocidad menor o igual a `0.1 m/s`.
4. Confirmar la dirección de cada eje.
5. Confirmar detención final.
6. Registrar el cambio en el `README.md` o en la bitácora del proyecto.

---

## 12. Resumen de actividades

| Actividad | Estado | Observación |
|---|---|---|
| Desarrollo del script de rutina cuadrada | Completado | El código implementa entrada por terminal, cálculo temporal, secuencia de cuatro lados y detención final. |
| Inicialización con `LocoClient` | Completado | Se usa `ChannelFactory`, `client.Init()` y `SetTimeout`. |
| Validación de parámetros | Completado | Bloquea distancia y velocidad menores o iguales a cero. |
| Secuencia translacional +X/+Y/-X/-Y | Completado | La rutina conserva `wz = 0`; no ejecuta giros. |
| Validación en robot físico | Pendiente de registro | Debe documentarse resultado real, interfaz usada y condiciones de prueba. |
| Validación de seguridad | Parcial | El código incluye `StopMove()` final, pero no maneja `Ctrl+C`. |
| Documentación técnica | Completado | Este documento permite replicar, ejecutar, depurar y extender la implementación. |
| Mejoras recomendadas | Pendiente | Agregar límites máximos, pausa explícita con `StopMove()` entre lados y manejo de señales. |

---

## 13. Conclusión técnica

La rutina documentada constituye una base funcional para ejecutar una trayectoria cuadrada en el Unitree R1 EDU mediante comandos de velocidad. Su principal ventaja es la simplicidad: el operador define distancia y velocidad, y el programa transforma esos valores en una secuencia de locomoción reproducible. Su principal limitación es que opera en lazo abierto, por lo que no garantiza precisión geométrica absoluta ni corrección de orientación.

Para pruebas internas, la versión actual es adecuada como rutina básica de validación de comunicación, locomoción y respuesta del robot. Para uso más robusto, se recomienda añadir límites máximos de seguridad, detención intermedia entre lados, manejo de interrupciones y, si el proyecto lo requiere, realimentación por odometría o estimación de pose.
