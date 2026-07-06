# Documentación Técnica del Código de Control Manual WASD para Unitree R1

**Robotics 4.0**  
**Documento técnico de análisis, operación y validación**  
**Fecha:** 30 de junio de 2026

---

## Información general del código

| Campo | Descripción |
|---|---|
| Robot objetivo | Unitree R1 |
| Lenguaje | C++ |
| Función principal | Teleoperación local del robot mediante teclado en terminal Linux |
| Interfaz de operación | Teclas WASD, Q/E, espacio y X |
| API utilizada | Unitree R1 Loco API y Unitree R1 Loco Client |
| Tipo de documento | Documentación técnica específica del código |

---

## Índice

1. [Propósito del documento](#1-propósito-del-documento)
2. [Objetivo del código](#2-objetivo-del-código)
3. [Descripción general de la implementación](#3-descripción-general-de-la-implementación)
   - [3.1. Componentes funcionales](#31-componentes-funcionales)
4. [Dependencias y entorno de ejecución](#4-dependencias-y-entorno-de-ejecución)
   - [4.1. Librerías estándar](#41-librerías-estándar)
   - [4.2. Librerías Unitree](#42-librerías-unitree)
5. [Parámetros configurables](#5-parámetros-configurables)
6. [Captura inmediata de teclado](#6-captura-inmediata-de-teclado)
   - [6.1. Lógica aplicada](#61-lógica-aplicada)
7. [Inicialización del robot](#7-inicialización-del-robot)
   - [7.1. Secuencia de arranque](#71-secuencia-de-arranque)
8. [Mapa de comandos de teclado](#8-mapa-de-comandos-de-teclado)
   - [8.1. Convención de ejes](#81-convención-de-ejes)
9. [Ciclo principal de operación](#9-ciclo-principal-de-operación)
   - [9.1. Flujo lógico](#91-flujo-lógico)
   - [9.2. Manejo de teclas no válidas](#92-manejo-de-teclas-no-válidas)
10. [Consideraciones de seguridad operacional](#10-consideraciones-de-seguridad-operacional)
    - [10.1. Condiciones recomendadas de prueba](#101-condiciones-recomendadas-de-prueba)
11. [Compilación y ejecución](#11-compilación-y-ejecución)
    - [11.1. Procedimiento general](#111-procedimiento-general)
12. [Validación técnica del código](#12-validación-técnica-del-código)
    - [12.1. Pruebas recomendadas](#121-pruebas-recomendadas)
13. [Limitaciones del código](#13-limitaciones-del-código)
14. [Conclusión](#14-conclusión)
15. [Anexo A. Código fuente documentado](#anexo-a-código-fuente-documentado)

---

## 1. Propósito del documento

Este documento describe el funcionamiento técnico de un código en C++ diseñado para controlar manualmente el robot Unitree R1 mediante pulsaciones directas de teclado en una terminal Linux. La implementación permite enviar comandos de locomoción al robot usando la API de Unitree, sin requerir una interfaz gráfica ni un sistema externo de teleoperación.

El alcance de esta documentación se limita al código suministrado: inicialización de comunicación, captura inmediata de teclado, asociación de teclas con comandos de movimiento, parada del robot y salida controlada del programa.

## 2. Objetivo del código

Implementar un mecanismo de teleoperación local para el robot Unitree R1, donde el operador pueda controlar desplazamiento lineal, desplazamiento lateral, giro sobre el eje vertical, frenado y cierre del programa mediante teclas predefinidas.

> **Resultado funcional esperado**  
> El programa debe iniciar la conexión con el robot, activar el cliente de locomoción, permanecer a la espera de una tecla y ejecutar el movimiento correspondiente hasta que el operador envíe una nueva orden, active el freno o cierre el programa.

## 3. Descripción general de la implementación

El código se estructura en dos bloques funcionales. El primero corresponde a la función `getch()`, encargada de modificar temporalmente el comportamiento de la terminal para capturar una tecla sin necesidad de presionar `Enter`. El segundo corresponde a la función `main()`, donde se inicializa la comunicación con el robot, se configura el cliente de locomoción y se ejecuta el ciclo de lectura de comandos.

### 3.1. Componentes funcionales

| Componente | Función dentro del código |
|---|---|
| `getch()` | Captura una pulsación de teclado de forma inmediata, sin esperar salto de línea y sin mostrar la tecla en pantalla. |
| `ChannelFactory::Init()` | Inicializa el canal de comunicación del SDK de Unitree usando la interfaz de red configurada. |
| `LocoClient` | Cliente de locomoción utilizado para iniciar el modo de control, enviar velocidades y detener el movimiento. |
| `client.Move()` | Envía velocidades lineales y angulares al robot en función de la tecla presionada. |
| `client.StopMove()` | Ejecuta la orden de parada de movimiento. Se usa para frenar y antes de salir del programa. |
| `switch(key)` | Asocia cada tecla válida con una acción de movimiento, parada o salida. |

## 4. Dependencias y entorno de ejecución

### 4.1. Librerías estándar

- `chrono`: permite generar pausas temporales controladas.
- `iostream`: permite imprimir mensajes de estado en terminal.
- `thread`: permite suspender la ejecución durante el inicio del robot.
- `termios.h`: permite modificar el modo de lectura de la terminal Linux.
- `unistd.h`: permite usar `read()` para capturar caracteres desde la entrada estándar.

### 4.2. Librerías Unitree

```cpp
#include "unitree/robot/r1/loco/r1_loco_api.hpp"
#include "unitree/robot/r1/loco/r1_loco_client.hpp"
```

Estas cabeceras permiten acceder a la API de locomoción del robot R1 y crear el cliente usado para enviar comandos de movimiento.

> **Condición de ejecución**  
> El programa depende de una interfaz de red válida para comunicarse con el robot. En el código se usa `eth10`; si la máquina de control utiliza otra interfaz, este valor debe modificarse antes de compilar o ejecutar.

## 5. Parámetros configurables

El código define tres parámetros principales que deben revisarse antes de la operación física.

| Parámetro | Valor actual | Descripción técnica |
|---|---:|---|
| `network_interface` | `eth10` | Nombre de la interfaz de red usada por el SDK para comunicarse con el robot. Debe coincidir con la interfaz real del equipo de control. |
| `speed` | `0.3f` | Velocidad lineal usada para avance, retroceso y desplazamiento lateral. Su unidad operativa es metros por segundo. |
| `turn_speed` | `0.5f` | Velocidad angular usada para giros a izquierda y derecha. Su unidad operativa es radianes por segundo. |

## 6. Captura inmediata de teclado

La función `getch()` modifica temporalmente la configuración de la terminal para que cada tecla sea capturada de forma directa. Por defecto, una terminal Linux trabaja en modo canónico, lo que significa que acumula la entrada hasta que el usuario presiona `Enter`. Para control robótico, ese comportamiento no es adecuado, porque introduce una demora innecesaria entre la intención del operador y la respuesta del robot.

### 6.1. Lógica aplicada

1. Se guarda la configuración actual de la terminal mediante `tcgetattr()`.
2. Se desactiva `ICANON` para evitar el buffer de línea.
3. Se desactiva `ECHO` para ocultar la tecla presionada.
4. Se configura `VMIN = 1`, de modo que la lectura espere exactamente un carácter.
5. Se captura la tecla con `read()`.
6. Se restaura el modo canónico y el eco de la terminal.
7. Se retorna el carácter capturado.

> **Implicación operativa**  
> El programa permanece bloqueado esperando una tecla. Cada pulsación genera una orden puntual de movimiento, parada o salida. El robot no recibe comandos continuos por temporizador; recibe una nueva orden únicamente cuando el operador presiona una tecla válida.

## 7. Inicialización del robot

La función `main()` inicia definiendo la interfaz de red, inicializando el canal de comunicación del SDK y creando un cliente de locomoción.

### 7.1. Secuencia de arranque

1. Definición de la interfaz de red mediante `network_interface`.
2. Inicialización de `ChannelFactory` con el dominio `0` y la interfaz seleccionada.
3. Creación de `unitree::robot::r1::LocoClient`.
4. Inicialización del cliente mediante `client.Init()`.
5. Configuración de tiempo máximo de espera con `client.SetTimeout(10.f)`.
6. Inicio del robot mediante `client.Start()`.
7. Pausa de un segundo para permitir estabilización inicial antes de recibir comandos.

> **Criterio de arranque correcto**  
> El arranque se considera correcto cuando el programa imprime el menú de control y el robot queda disponible para recibir comandos de movimiento desde teclado.

## 8. Mapa de comandos de teclado

El control manual se basa en un esquema WASD ampliado con teclas de giro, frenado y salida.

### 8.1. Convención de ejes

La estructura de `client.Move(x, y, yaw)` permite separar el movimiento en tres componentes: velocidad longitudinal, velocidad lateral y velocidad angular. En este código, el eje longitudinal se controla con `W/S`, el eje lateral con `A/D` y el giro sobre el eje vertical con `Q/E`.

| Tecla | Acción | Comando enviado |
|---|---|---|
| `W` | Avance | `client.Move(speed, 0.0f, 0.0f)` |
| `S` | Retroceso | `client.Move(-speed, 0.0f, 0.0f)` |
| `A` | Desplazamiento lateral izquierdo | `client.Move(0.0f, speed, 0.0f)` |
| `D` | Desplazamiento lateral derecho | `client.Move(0.0f, -speed, 0.0f)` |
| `Q` | Giro hacia la izquierda | `client.Move(0.0f, 0.0f, turn_speed)` |
| `E` | Giro hacia la derecha | `client.Move(0.0f, 0.0f, -turn_speed)` |
| `Espacio` | Freno operativo | `client.StopMove()` |
| `X` | Salida del programa | `client.StopMove()` y cierre del ciclo |

## 9. Ciclo principal de operación

El ciclo principal se ejecuta mientras la variable `running` sea verdadera. En cada iteración, el programa espera una tecla, evalúa su valor mediante una estructura `switch` y ejecuta la acción asociada.

### 9.1. Flujo lógico

1. El programa espera una pulsación mediante `getch()`.
2. La tecla se compara contra los casos válidos del `switch`.
3. Si la tecla corresponde a movimiento, se envía `client.Move()`.
4. Si la tecla es espacio, se ejecuta `client.StopMove()`.
5. Si la tecla es `X`, se detiene el robot y se termina el ciclo.
6. Si la tecla no está definida, el programa la ignora.

### 9.2. Manejo de teclas no válidas

El bloque `default` no ejecuta ninguna acción. Esta decisión evita que pulsaciones accidentales envíen comandos no previstos al robot. Desde el punto de vista operativo, el comportamiento es seguro porque el programa solo responde ante teclas explícitamente definidas.

## 10. Consideraciones de seguridad operacional

El código incluye dos mecanismos básicos de seguridad: una tecla de parada y una salida controlada. La tecla de espacio ejecuta `StopMove()` sin terminar el programa, mientras que la tecla `X` detiene el movimiento antes de cerrar el ciclo principal.

> **Punto crítico**  
> El operador debe tener acceso inmediato a la tecla de espacio durante cualquier prueba física. La parada por teclado es el mecanismo de frenado operativo del programa y debe verificarse antes de ejecutar movimientos prolongados.

### 10.1. Condiciones recomendadas de prueba

- Ejecutar primero con velocidades bajas si el espacio es reducido.
- Verificar que la interfaz de red corresponda al enlace real con el robot.
- Probar `StopMove()` antes de realizar desplazamientos.
- Mantener el robot en un área libre de obstáculos durante las primeras pruebas.
- Tener un operador atento al comportamiento físico del robot durante toda la ejecución.

## 11. Compilación y ejecución

La compilación depende de la estructura del workspace y de la ubicación del SDK de Unitree. El archivo debe compilarse enlazando correctamente las librerías requeridas por `r1_loco_client.hpp` y `r1_loco_api.hpp`.

### 11.1. Procedimiento general

1. Confirmar la interfaz de red conectada al robot.
2. Ajustar el valor de `network_interface` si no corresponde a `eth10`.
3. Compilar el código dentro del entorno donde estén disponibles las cabeceras y librerías del SDK.
4. Ejecutar el binario desde una terminal Linux.
5. Verificar que aparezca el menú de control.
6. Probar primero la tecla de parada.
7. Ejecutar movimientos individuales y cerrar con `X`.

> **Nota de implementación**  
> Si el código se integra a un proyecto con CMake, el objetivo de compilación debe incluir el archivo fuente y enlazar las dependencias del SDK de Unitree. El nombre del ejecutable puede definirse según la estructura interna del workspace.

## 12. Validación técnica del código

La validación debe confirmar que el programa cumple su función específica: controlar manualmente el robot mediante teclado, detenerlo de forma segura y cerrar sin dejar movimiento activo.

### 12.1. Pruebas recomendadas

#### PT-01. Validación de conexión con el robot

**Objetivo:** confirmar que el cliente de locomoción inicializa correctamente usando la interfaz de red configurada.  
**Resultado esperado:** el programa inicia, muestra el menú de control y queda a la espera de comandos.

#### PT-02. Validación de comandos lineales

**Objetivo:** verificar que las teclas `W` y `S` generen avance y retroceso respectivamente.  
**Resultado esperado:** el robot responde en la dirección correspondiente y se detiene al presionar espacio.

#### PT-03. Validación de desplazamiento lateral

**Objetivo:** comprobar que las teclas `A` y `D` ejecuten desplazamientos laterales diferenciados.  
**Resultado esperado:** el robot realiza *strafe* hacia izquierda o derecha según la tecla presionada.

#### PT-04. Validación de giro

**Objetivo:** verificar que las teclas `Q` y `E` ejecuten giro sobre el eje vertical.  
**Resultado esperado:** el robot gira hacia el lado correspondiente sin desplazamiento lineal.

#### PT-05. Validación de parada y salida

**Objetivo:** comprobar que la tecla espacio detenga el movimiento y que la tecla `X` cierre el programa después de enviar una orden de parada.  
**Resultado esperado:** no queda movimiento activo después de frenar o cerrar el programa.

## 13. Limitaciones del código

- El programa no implementa control proporcional ni rampa de aceleración.
- El movimiento depende de la última orden enviada hasta que se ejecute una nueva orden o una parada.
- No existe lectura de estado del robot dentro del ciclo principal.
- No se implementa evasión de obstáculos ni validación del entorno.
- El control requiere una terminal activa y acceso directo al teclado.
- La interfaz de red está definida de forma fija en el código.

## 14. Conclusión

El código documentado implementa una herramienta directa y funcional para teleoperar el robot Unitree R1 desde una terminal Linux. Su lógica es simple, verificable y adecuada para pruebas iniciales de locomoción, validación de comandos básicos y control manual en entornos supervisados.

La implementación se apoya en tres elementos centrales: captura inmediata de teclado, cliente de locomoción de Unitree y asociación explícita entre teclas y velocidades. La correcta operación física depende de una interfaz de red válida, parámetros de velocidad adecuados y verificación previa del comando de parada.

---

## Anexo A. Código fuente documentado

```cpp
#include <chrono>
#include <iostream>
#include <thread>
#include <termios.h>
#include <unistd.h>

#include "unitree/robot/r1/loco/r1_loco_api.hpp"
#include "unitree/robot/r1/loco/r1_loco_client.hpp"

// Captura una tecla sin requerir Enter.
char getch() {
  char buf = 0;
  struct termios old = {0};

  if (tcgetattr(0, &old) < 0) perror("tcsetattr()");

  old.c_lflag &= ~ICANON;
  old.c_lflag &= ~ECHO;
  old.c_cc[VMIN] = 1;
  old.c_cc[VTIME] = 0;

  if (tcsetattr(0, TCSANOW, &old) < 0) perror("tcsetattr ICANON");
  if (read(0, &buf, 1) < 0) perror("read()");

  old.c_lflag |= ICANON;
  old.c_lflag |= ECHO;

  if (tcsetattr(0, TCSADRAIN, &old) < 0) perror("tcsetattr ~ICANON");

  return buf;
}

int main() {
  std::string network_interface = "eth10";
  unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);

  unitree::robot::r1::LocoClient client;
  client.Init();
  client.SetTimeout(10.f);

  float speed = 0.3f;
  float turn_speed = 0.5f;

  std::cout << "Iniciando robot..." << std::endl;
  client.Start();
  std::this_thread::sleep_for(std::chrono::seconds(1));

  std::cout << "\n=== CONTROL POR TECLADO ACTIVADO ===" << std::endl;
  std::cout << " W : Adelante      Q : Girar Izquierda" << std::endl;
  std::cout << " S : Atras         E : Girar Derecha" << std::endl;
  std::cout << " A : Izquierda (Strafe)" << std::endl;
  std::cout << " D : Derecha (Strafe)" << std::endl;
  std::cout << " [ESPACIO] : DETENER (Freno)" << std::endl;
  std::cout << " X : Salir y apagar" << std::endl;
  std::cout << "====================================\n" << std::endl;

  bool running = true;

  while (running) {
    char key = getch();

    switch (key) {
      case 'w':
      case 'W':
        std::cout << "Adelante" << std::endl;
        client.Move(speed, 0.0f, 0.0f);
        break;

      case 's':
      case 'S':
        std::cout << "Atras" << std::endl;
        client.Move(-speed, 0.0f, 0.0f);
        break;

      case 'a':
      case 'A':
        std::cout << "Izquierda" << std::endl;
        client.Move(0.0f, speed, 0.0f);
        break;

      case 'd':
      case 'D':
        std::cout << "Derecha" << std::endl;
        client.Move(0.0f, -speed, 0.0f);
        break;

      case 'q':
      case 'Q':
        std::cout << "Girar Izquierda" << std::endl;
        client.Move(0.0f, 0.0f, turn_speed);
        break;

      case 'e':
      case 'E':
        std::cout << "Girar Derecha" << std::endl;
        client.Move(0.0f, 0.0f, -turn_speed);
        break;

      case ' ':
        std::cout << "DETENIDO" << std::endl;
        client.StopMove();
        break;

      case 'x':
      case 'X':
        std::cout << "Saliendo del programa..." << std::endl;
        client.StopMove();
        running = false;
        break;

      default:
        break;
    }
  }

  return 0;
}
```

---

**Sitio web:** www.robotics40.com  
**Contacto:** ceo@robotics40.com
