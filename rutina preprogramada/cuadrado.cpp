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

  client.Start(); // Asegura que el robot esté activo
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