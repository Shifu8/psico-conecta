/*
  PsicoConecta - Firmware ESP32 para Telemetría de Pulsaciones Cardíacas
  
  Este sketch se conecta a una red WiFi, establece una conexión WebSocket
  persistente con el servidor de telemetría en AWS (a través de Nginx en puerto 80),
  lee un sensor analógico conectado al pin G34 cada 20ms (frecuencia de 50Hz)
  y envía los datos en tiempo real.
  
  Si no hay un sensor físico conectado, genera una señal de electrocardiograma (ECG)
  simulada para facilitar las pruebas del dashboard.

  ─────────────────────────────────────────────────────────────────
  CONFIGURACIÓN RÁPIDA:
    1. Cambia WIFI_SSID y WIFI_PASS con tu red WiFi.
    2. Cambia SERVER_HOST con la IP pública o dominio de tu instancia AWS.
    3. SERVER_PORT = 80  (Nginx escucha en puerto estándar HTTP).
    4. La ruta /esp32 es manejada por Nginx y redirigida al WebSocket.
  ─────────────────────────────────────────────────────────────────
*/

#include <WiFi.h>
#include <WebSocketsClient.h> // Librería de Links2004/arduinoWebSockets

// ---- CONFIGURACIÓN DE RED Y SERVIDOR ────────────────────────────────────────
const char* WIFI_SSID       = "marinerito";           // <-- Tu red WiFi
const char* WIFI_PASS       = "123456789";            // <-- Tu contraseña WiFi

// Dirección del servidor en AWS (IP pública o nombre de dominio)
// Puerto 80: Nginx escucha en el puerto HTTP estándar
const char* SERVER_HOST     = "54.0.0.0";            // <-- Cambia por la IP/dominio AWS
const uint16_t SERVER_PORT  = 80;

// ID del paciente y token de seguridad del dispositivo
const char* PATIENT_ID      = "1";
const char* DEVICE_TOKEN    = "esp32_secret_device_token_2026";

// ---- CONFIGURACIÓN DE HARDWARE ──────────────────────────────────────────────
const int ANALOG_PIN              = 34;   // Pin G34 para el sensor cardíaco (MAX30102 o similar)
const unsigned long INTERVALO_MS  = 20;   // 20 ms = 50 Hz de muestreo

// ---- VARIABLES DE ESTADO ────────────────────────────────────────────────────
WebSocketsClient webSocket;
unsigned long ultimoMuestreo = 0;
bool websocketConectado      = false;
unsigned long ultimoReconexion = 0;

// ─────────────────────────────────────────────────────────────────────────────
//  GENERADOR DE SEÑAL ECG SIMULADA
//  Produce un ciclo QRS completo de 1 segundo (60 lpm) con ondas P, QRS y T.
//  Se activa automáticamente cuando no hay sensor físico conectado.
// ─────────────────────────────────────────────────────────────────────────────
int obtenerValorECGSimulado() {
  unsigned long t    = millis() % 1000;   // Un ciclo cardíaco de 1 segundo
  int base           = 2000;              // Nivel base ADC (12 bits: 0-4095)
  int ruido          = random(-10, 10);

  if (t < 200) {
    // Onda P: pequeña elevación suave
    return base + (int)(80.0 * sin((t / 200.0) * PI)) + ruido;

  } else if (t < 280) {
    // Segmento PR: retorno a la línea base
    return base + ruido;

  } else if (t < 300) {
    // Onda Q: pequeño descenso antes del QRS
    return base - 100 + ruido;

  } else if (t < 330) {
    // Onda R: gran pico positivo del complejo QRS
    float prog = (t - 300) / 30.0;
    return base + (int)(1500.0 * sin(prog * PI)) + ruido;

  } else if (t < 360) {
    // Onda S: descenso profundo post-QRS
    float prog = (t - 330) / 30.0;
    return base - 350 + (int)(350.0 * cos(prog * PI)) + ruido;

  } else if (t < 450) {
    // Segmento ST: retorno a la línea base
    return base + ruido;

  } else if (t < 600) {
    // Onda T: elevación mediana de repolarización
    float prog = (t - 450) / 150.0;
    return base + (int)(250.0 * sin(prog * PI)) + ruido;

  } else {
    // Línea isoeléctrica (diástole)
    return base + ruido;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  MANEJADOR DE EVENTOS WEBSOCKET
// ─────────────────────────────────────────────────────────────────────────────
void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Desconectado del servidor. Reintentando en 5s...");
      websocketConectado = false;
      break;

    case WStype_CONNECTED:
      Serial.printf("[WS] Conectado exitosamente al servidor → ruta: %s\n", payload);
      websocketConectado = true;
      // Enviar mensaje de handshake con el ID del paciente
      {
        String handshake = "{\"type\":\"hello\",\"patient_id\":\"" + String(PATIENT_ID) + "\",\"device\":\"ESP32\"}";
        webSocket.sendTXT(handshake);
      }
      break;

    case WStype_TEXT:
      Serial.printf("[WS] Servidor → %s\n", payload);
      break;

    case WStype_ERROR:
      Serial.println("[WS] Error de conexión detectado.");
      websocketConectado = false;
      break;

    case WStype_PING:
      Serial.println("[WS] Ping recibido del servidor.");
      break;

    case WStype_PONG:
      Serial.println("[WS] Pong recibido.");
      break;

    default:
      break;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  SETUP
// ─────────────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(ANALOG_PIN, INPUT);
  randomSeed(analogRead(35)); // Semilla de aleatoriedad con pin flotante

  // ── Conexión WiFi ───────────────────────────────────────────────────────────
  Serial.printf("\n[WiFi] Conectando a '%s'...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n[WiFi] ERROR: No se pudo conectar. Reiniciando en 10s...");
    delay(10000);
    ESP.restart();
  }

  Serial.println("\n[WiFi] ¡Conectado!");
  Serial.printf("[WiFi] IP local: %s\n", WiFi.localIP().toString().c_str());

  // ── Configuración del WebSocket ─────────────────────────────────────────────
  // Ruta: /esp32?device_token=<TOKEN>&patient_id=<ID>
  // Nginx redirige /esp32 → servidor de telemetría en el puerto 5006
  String path = "/esp32?device_token=" + String(DEVICE_TOKEN)
              + "&patient_id=" + String(PATIENT_ID);

  Serial.printf("[WS] Conectando a ws://%s:%d%s\n", SERVER_HOST, SERVER_PORT, path.c_str());

  webSocket.begin(SERVER_HOST, SERVER_PORT, path.c_str());
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);   // Reconexión automática cada 5s
  webSocket.enableHeartbeat(15000, 3000, 2); // Ping cada 15s, pong en 3s, 2 reintentos
}

// ─────────────────────────────────────────────────────────────────────────────
//  LOOP PRINCIPAL
// ─────────────────────────────────────────────────────────────────────────────
void loop() {
  // Mantener la conexión WebSocket activa
  webSocket.loop();

  // Verificar conectividad WiFi periódicamente
  if (WiFi.status() != WL_CONNECTED) {
    unsigned long ahora = millis();
    if (ahora - ultimoReconexion > 10000) {
      ultimoReconexion = ahora;
      Serial.println("[WiFi] Conexión perdida. Reconectando...");
      WiFi.reconnect();
    }
    return;
  }

  // ── Muestreo a 50 Hz ─────────────────────────────────────────────────────
  unsigned long tiempoActual = millis();
  if (tiempoActual - ultimoMuestreo >= INTERVALO_MS) {
    ultimoMuestreo = tiempoActual;

    // Leer el sensor analógico (MAX30102 u otro)
    int valorLectura = analogRead(ANALOG_PIN);

    // Si la lectura es plana (sin sensor físico), usar señal ECG simulada
    if (valorLectura < 100 || valorLectura > 4000) {
      valorLectura = obtenerValorECGSimulado();
    }

    // Solo transmitir si el WebSocket está activo
    if (websocketConectado) {
      // JSON de telemetría:
      // {"patient_id":"1","raw_value":2150,"ts":12345678}
      String json = "{\"patient_id\":\"" + String(PATIENT_ID) + "\""
                  + ",\"raw_value\":"   + String(valorLectura)
                  + ",\"ts\":"          + String(tiempoActual)
                  + "}";
      webSocket.sendTXT(json);
    }
  }
}
