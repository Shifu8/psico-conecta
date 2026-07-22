# Archivo: simulador_esp32.py
# Descripción: Simulador de hardware ESP32 y sensor de pulsaciones cardíacas.
# Módulo: Servicio Inteligencia e IoT

import asyncio
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
import websockets

DEVICE_TOKEN = os.getenv("DEVICE_TOKEN", "PsicoConectaSecureToken2026")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:5006/ws/esp32")

def generar_lectura_ppg(t, bpm=72):
    """
    Genera un valor sintético de fotopletismograma (PPG) imitando un sensor óptico de pulso cardíaco.
    """
    frecuencia = bpm / 60.0  # Hz
    fasa = 2 * math.pi * frecuencia * t
    
    # Onda sistólica principal + sica dicrota secundaria + ruido fisiológico
    sistole = math.exp(-((math.sin(fasa / 2)) ** 2) * 12)
    dicrota = 0.3 * math.exp(-((math.sin((fasa - 0.8) / 2)) ** 2) * 20)
    ruido = random.uniform(-0.02, 0.02)
    
    # Escalar a valores analógicos típicos de ADC de ESP32 (300 a 850)
    base = 512.0
    amplitud = 250.0
    raw_val = int(base + (sistole + dicrota + ruido) * amplitud)
    return max(0, min(1023, raw_val))

async def simular_captura(patient_id=4, duracion_segundos=15, bpm_base=75):
    """
    Simula la transmisión de telemetría de una ESP32 durante 'duracion_segundos'.
    """
    url_con_token = f"{WEBSOCKET_URL}?device_token={DEVICE_TOKEN}"
    print(f"[Simulador ESP32] Conectando a {url_con_token} para paciente #{patient_id}...")
    
    try:
        async with websockets.connect(url_con_token) as ws:
            print(f"[Simulador ESP32] Conexión establecida. Iniciando simulación ({duracion_segundos}s)...")
            inicio = time.time()
            frecuencia_muestreo = 20  # 20 Hz (20 muestras por segundo)
            intervalo = 1.0 / frecuencia_muestreo
            
            raw_values = []
            bpm_actual = bpm_base
            
            while time.time() - inicio < duracion_segundos:
                t_transcurrido = time.time() - inicio
                
                # Ligera variación natural del ritmo cardíaco (HRV)
                bpm_actual += random.uniform(-0.5, 0.5)
                bpm_actual = max(60, min(120, bpm_actual))
                
                raw = generar_lectura_ppg(t_transcurrido, bpm=bpm_actual)
                raw_values.append(raw)
                
                payload = {
                    "patient_id": str(patient_id),
                    "raw_value": raw,
                    "bpm": round(bpm_actual, 1),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "simulado": True
                }
                
                await ws.send(json.dumps(payload))
                print(f"  [{t_transcurrido:.1f}s] BPM: {bpm_actual:.1f} | Analog Raw: {raw}")
                await asyncio.sleep(intervalo)
                
            bpm_promedio = round(sum([bpm_base] + [bpm_actual]) / 2, 1)
            print(f"[Simulador ESP32] Simulación completada exitosamente.")
            print(f"  Total muestras enviadas: {len(raw_values)}")
            print(f"  BPM Promedio simulado: {bpm_promedio}")
            
    except Exception as e:
        print(f"[!] Error en conexión de simulador ESP32: {e}")

if __name__ == "__main__":
    patient_id = sys.argv[1] if len(sys.argv) > 1 else "4"
    duracion = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    asyncio.run(simular_captura(patient_id=patient_id, duracion_segundos=duracion))
