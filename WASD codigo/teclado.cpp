#include <chrono>
#include <iostream>
#include <thread>
#include <termios.h> // Librería para manipular la terminal en Linux
#include <unistd.h>

#include "unitree/robot/r1/loco/r1_loco_api.hpp"
#include "unitree/robot/r1/loco/r1_loco_client.hpp"

// Función para capturar pulsaciones de teclado al instante (sin presionar Enter)
char getch() {
    char buf = 0;
    struct termios old = {0};
    if (tcgetattr(0, &old) < 0) perror("tcsetattr()");
    old.c_lflag &= ~ICANON; // Deshabilita el buffer de línea
    old.c_lflag &= ~ECHO;   // Oculta la tecla presionada en pantalla
    old.c_cc[VMIN] = 1;
    old.c_cc[VTIME] = 0;
    if (tcsetattr(0, TCSANOW, &old) < 0) perror("tcsetattr ICANON");
    if (read(0, &buf, 1) < 0) perror ("read()");
    old.c_lflag |= ICANON;
    old.c_lflag |= ECHO;
    if (tcsetattr(0, TCSADRAIN, &old) < 0) perror ("tcsetattr ~ICANON");
    return buf;
}

int main() {
  // NOTA: Cambia "eth10" si descubriste que tu interfaz es otra (ej. "lo", "enp3s0")
  std::string network_interface = "eth10"; 
  unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);

  unitree::robot::r1::LocoClient client;
  client.Init();
  client.SetTimeout(10.f);

  // Configuración de velocidades (Ajusta estos valores si lo sientes muy rápido/lento)
  float speed = 0.3f;       // m/s para movimiento lineal
  float turn_speed = 0.5f;  // rad/s para giros

  std::cout << "Iniciando robot..." << std::endl;
  client.Start();
  std::this_thread::sleep_for(std::chrono::seconds(1));

  std::cout << "\n=== CONTROL POR TECLADO ACTIVADO ===" << std::endl;
  std::cout << " W : Adelante             Q : Girar Izquierda" << std::endl;
  std::cout << " S : Atrás                E : Girar Derecha" << std::endl;
  std::cout << " A : Izquierda (Strafe)" << std::endl;
  std::cout << " D : Derecha (Strafe)" << std::endl;
  std::cout << " [ESPACIO] : DETENER (Freno)" << std::endl;
  std::cout << " X : Salir y apagar" << std::endl;
  std::cout << "====================================\n" << std::endl;

  bool running = true;
  while (running) {
    char key = getch(); // El programa se pausa aquí hasta que toques una tecla

    switch (key) {
      case 'w': case 'W':
        std::cout << "↑ Adelante" << std::endl;
        client.Move(speed, 0.0f, 0.0f);
        break;
      case 's': case 'S':
        std::cout << "↓ Atrás" << std::endl;
        client.Move(-speed, 0.0f, 0.0f);
        break;
      case 'a': case 'A':
        std::cout << "← Izquierda" << std::endl;
        client.Move(0.0f, speed, 0.0f);
        break;
      case 'd': case 'D':
        std::cout << "→ Derecha" << std::endl;
        client.Move(0.0f, -speed, 0.0f);
        break;
      case 'q': case 'Q':
        std::cout << "↶ Girar Izquierda" << std::endl;
        client.Move(0.0f, 0.0f, turn_speed);
        break;
      case 'e': case 'E':
        std::cout << "↷ Girar Derecha" << std::endl;
        client.Move(0.0f, 0.0f, -turn_speed);
        break;
      case ' ': // Espacio
        std::cout << "■ DETENIDO" << std::endl;
        client.StopMove();
        break;
      case 'x': case 'X':
        std::cout << "Saliendo del programa..." << std::endl;
        client.StopMove();
        running = false;
        break;
      default:
        // Ignora cualquier otra tecla
        break;
    }
  }

  return 0;
}