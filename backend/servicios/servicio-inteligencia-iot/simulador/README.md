# Simulador de Telemetría ESP32 e IoT (Ritmo Cardíaco)

Este directorio contiene el simulador de hardware en software que reemplaza las lecturas del microcontrolador ESP32 y sensor óptico pulsómetro cuando no se dispone del dispositivo físico.

## Archivos

- `simulador_esp32.py`: Script en Python que imita una tarjeta ESP32 conectada por WebSockets. Genera señales fotopletismográficas (PPG) sintéticas con variabilidad cardíaca fisiológica y transmisión en tiempo real.

## Uso por línea de comandos

Para probar el simulador manualmente desde la consola:

```bash
# Ejecutar para el paciente con ID 4 durante 15 segundos
python simulador_esp32.py 4 15
```

Parámetros opcionales:
1. `patient_id` (por defecto: `4`)
2. `duracion_segundos` (por defecto: `15`)

## Variables de entorno opcionales

- `WEBSOCKET_URL`: URL del servidor de telemetría (predeterminado: `ws://localhost:5006/ws/esp32`)
- `DEVICE_TOKEN`: Token de autenticación de dispositivo (predeterminado: `PsicoConectaSecureToken2026`)
