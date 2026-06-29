/*
  PsicoConecta - Firmware ESP32 para Telemetría de Pulsaciones Cardíacas
  
  Este sketch se conecta a una red WiFi, establece una conexión WebSocket
  persistente con el servidor de telemetría (a través de Nginx), lee un sensor
  analógico conectado al pin G34 cada 20ms (frecuencia de 50Hz) y envía los datos en tiempo real.
  
  Si no hay un sensor físico conectado, genera una señal de electrocardiograma (ECG)
  simulada para facilitar las pruebas del dashboard.
*/

#include <WiFi.h>
#include <WebSocketsClient.h> // Librería de Links2004/arduinoWebSockets o similar

// ---- CONFIGURACIÓN DE RED Y SERVIDOR ----
const char* WIFI_SSID = "marinerito";
const char* WIFI_PASS = "123456789";

// Dirección y puerto de Nginx (reverse proxy de telemetría)
const char* SERVER_HOST = "192.168.1.100"; // Cambiar por la IP local del servidor
const uint16_t SERVER_PORT = 8080;
const char* PATIENT_ID = "1"; // ID del paciente asociado a este dispositivo
const char* DEVICE_TOKEN = "esp32_secret_device_token_2026"; // Llave estática de seguridad

// ---- CONFIGURACIÓN DE HARDWARE ----
const int ANALOG_PIN = 34; // Pin G34 para el sensor cardíaco
const unsigned long INTERVALO_MUESTREO = 20; // 20ms = 50Hz

WebSocketsClient webSocket;
unsigned long ultimoMuestreo = 0;
bool websocketConectado = false;

// Variables para la simulación de ECG
unsigned long simulacionTiempo = 0;

// Generador de señal ECG simulada (QRS complex)
int obtenerValorECGSimulado() {
  unsigned long t = millis() % 1000; // Un ciclo cardíaco de 1 segundo (60 lpm)
  int base = 2000; // Nivel base de la señal ADC (12 bits: 0-4095)
  int ruido = random(-10, 10);
  
  if (t < 200) {
    // Onda P (pequeña elevación)
    return base + (int)(80 * sin((t / 200.0) * PI)) + ruido;
  } else if (t < 280) {
    // Retorno a base
    return base + ruido;
  } else if (t < 300) {
    // Onda Q (pequeño descenso)
    return base - 100 + ruido;
  } else if (t < 330) {
    // Onda R (gran pico positivo del QRS)
    float prog = (t - 300) / 30.0;
    return base + (int)(1500 * sin(prog * PI)) + ruido;
  } else if (t < 360) {
    // Onda S (descenso profundo)
    float prog = (t - 330) / 30.0;
    return base - 350 + (int)(350 * cos(prog * PI)) + ruido;
  } else if (t < 450) {
    // Retorno a base
    return base + ruido;
  } else if (t < 600) {
    // Onda T (elevación mediana)
    float prog = (t - 450) / 150.0;
    return base + (int)(250 * sin(prog * PI)) + ruido;
  } else {
    // Línea isoeléctrica
    return base + ruido;
  }
}

// Manejador de eventos WebSocket
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Desconectado del servidor de telemetría.");
      websocketConectado = false;
      break;
    case WStype_CONNECTED:
      Serial.printf("[WS] Conectado exitosamente a la ruta: %s\n", payload);
      websocketConectado = true;
      break;
    case WStype_TEXT:
      Serial.printf("[WS] Mensaje recibido del servidor: %s\n", payload);
      break;
    case WStype_ERROR:
      Serial.println("[WS] Error detectado.");
      break;
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  pinMode(ANALOG_PIN, INPUT);
  
  // Conexión WiFi
  Serial.printf("\n[WiFi] Conectando a %s...\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[WiFi] Conectado. IP obtenida: ");
  Serial.println(WiFi.localIP());
  
  // Configuración del WebSocket
  // Se concatena el device_token en los parámetros de consulta para la validación perimetral
  String path = "/esp32?device_token=" + String(DEVICE_TOKEN);
  webSocket.begin(SERVER_HOST, SERVER_PORT, path.c_str());
  webSocket.onEvent(webSocketEvent);
  
  // Reconexión automática si se cae la conexión
  webSocket.setReconnectInterval(5000);
}

void loop() {
  webSocket.loop();
  
  unsigned long tiempoActual = millis();
  if (tiempoActual - ultimoMuestreo >= INTERVALO_MUESTREO) {
    ultimoMuestreo = tiempoActual;
    
    // Leemos el sensor (si está conectado)
    int valorLectura = analogRead(ANALOG_PIN);
    
    // Si la lectura es plana o cercana a cero (indicando que no hay sensor físico conectado),
    // usamos la señal ECG simulada de alta resolución
    if (valorLectura < 100 || valorLectura > 4000) {
      valorLectura = obtenerValorECGSimulado();
    }
    
    // Solo enviamos datos si estamos conectados por WebSocket
    if (websocketConectado) {
      // Construcción del mensaje JSON de telemetría
      String mensajeJson = "{\"patient_id\":\"" + String(PATIENT_ID) + 
                           "\",\"raw_value\":" + String(valorLectura) + "}";
      
      webSocket.sendTXT(mensajeJson);
    }
  }
}
