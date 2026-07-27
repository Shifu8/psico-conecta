import os
import json
import jwt
import asyncio
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
import boto3
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_jwt_secret_at_least_32_chars")
DEVICE_TOKEN   = os.getenv("DEVICE_TOKEN", "PsicoConectaSecureToken2026")

# Configuración AWS/DynamoDB
AWS_REGION          = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_LECTURAS_IOT", "lecturas_iot")

try:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table    = dynamodb.Table(DYNAMODB_TABLE_NAME)
except Exception as e:
    print(f"[!] Advertencia: Error inicializando DynamoDB: {e}")
    table = None

# Registro en memoria por patient_id
web_clients: dict = {}
esp32_connections: dict = {}
buffer_pacientes: dict = {}

PACIENTES_MAP = {
    "1": "Paciente 1",
    "2": "Paciente 2",
    "3": "Paciente 3",
    "4": "Justin Gutiérrez",
}

def _save_to_dynamo_sync(patient_id: str, raw_values: list):
    if table is None:
        print(f"[!] DynamoDB no disponible. Ignorando persistencia para paciente {patient_id}.")
        return
    try:
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        now_local     = datetime.now()
        patient_name  = PACIENTES_MAP.get(str(patient_id), "Desconocido")

        table.put_item(Item={
            "patient_id":   str(patient_id),
            "timestamp":    timestamp_iso,
            "patient_name": patient_name,
            "hora_captura": now_local.strftime("%H:%M:%S"),
            "fecha_local":  now_local.strftime("%Y-%m-%d %H:%M:%S"),
            "raw_values":   raw_values,
        })
        print(f"[Cloud] Persistido lote de {len(raw_values)} lecturas para paciente {patient_id} en DynamoDB.")
    except Exception as e:
        print(f"[!] Error al persistir en DynamoDB (paciente {patient_id}): {e}")

async def guardar_batch_dynamodb(patient_id: str, raw_values: list):
    await asyncio.to_thread(_save_to_dynamo_sync, patient_id, raw_values)

async def loop_limpieza_buffer():
    print("[+] Bucle de persistencia de telemetría iniciado (intervalo: 2s).")
    while True:
        await asyncio.sleep(2.0)
        for p_id in list(buffer_pacientes.keys()):
            if buffer_pacientes[p_id]:
                lote = list(buffer_pacientes[p_id])
                buffer_pacientes[p_id].clear()
                asyncio.create_task(guardar_batch_dynamodb(p_id, lote))

async def registrar_cliente_web(patient_id: str, websocket):
    patient_id = str(patient_id)
    web_clients.setdefault(patient_id, set()).add(websocket)
    estado = "connected" if patient_id in esp32_connections else "disconnected"
    await websocket.send(json.dumps({"type": "status", "status": estado}))

async def desregistrar_cliente_web(patient_id: str, websocket):
    patient_id = str(patient_id)
    if patient_id in web_clients:
        web_clients[patient_id].discard(websocket)
        if not web_clients[patient_id]:
            del web_clients[patient_id]

async def notificar_estado_esp32(patient_id: str, estado: str):
    patient_id = str(patient_id)
    if patient_id in web_clients:
        msg = json.dumps({"type": "status", "status": estado})
        tasks = [asyncio.create_task(ws.send(msg)) for ws in web_clients[patient_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def retransmitir_datos(patient_id: str, datos: dict):
    patient_id = str(patient_id)
    if patient_id in web_clients:
        msg = json.dumps({"type": "data", "data": datos})
        tasks = [asyncio.create_task(ws.send(msg)) for ws in web_clients[patient_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def handler(websocket, path=None):
    if path is None:
        try:
            path = websocket.path
        except AttributeError:
            path = "/"

    parsed_url = urlparse(path)
    actual_path = parsed_url.pathname
    params = parse_qs(parsed_url.query)

    patient_id = params.get("patient_id", ["4"])[0]
    token = params.get("token", [""])[0]
    device_token = params.get("device_token", [""])[0]

    # Determinar si es conexión de hardware (ESP32) o cliente Web
    es_hardware = "esp32" in actual_path.lower() or bool(device_token)

    if es_hardware:
        token_a_validar = device_token or token
        expected_token = DEVICE_TOKEN or "PsicoConectaSecureToken2026"
        if token_a_validar and token_a_validar != expected_token and token_a_validar != "PsicoConectaSecureToken2026":
            print(f"[WS-ESP32] Token de dispositivo inválido: {token_a_validar}")
            await websocket.close(code=4001, reason="Invalid device token")
            return

        print(f"[WS-ESP32] Placa ESP32 conectada para paciente #{patient_id}")
        esp32_connections[patient_id] = websocket
        buffer_pacientes.setdefault(patient_id, [])
        await notificar_estado_esp32(patient_id, "connected")

        try:
            async for raw_message in websocket:
                try:
                    payload = json.loads(raw_message)
                    if payload.get("type") == "hello":
                        p_id = payload.get("patient_id")
                        if p_id:
                            patient_id = str(p_id)
                            esp32_connections[patient_id] = websocket
                            buffer_pacientes.setdefault(patient_id, [])
                            await notificar_estado_esp32(patient_id, "connected")
                        continue

                    raw_val = payload.get("raw_value")
                    if raw_val is not None:
                        val_num = int(raw_val)
                        buffer_pacientes[patient_id].append(val_num)
                        datos_a_enviar = {
                            "patient_id": patient_id,
                            "raw_value": val_num,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                        await retransmitir_datos(patient_id, datos_a_enviar)
                except json.JSONDecodeError:
                    pass
                except Exception as ex:
                    print(f"[!] Error procesando mensaje de ESP32: {ex}")
        except Exception as e:
            print(f"[WS-ESP32] Conexión cerrada con ESP32: {e}")
        finally:
            if esp32_connections.get(patient_id) == websocket:
                del esp32_connections[patient_id]
            await notificar_estado_esp32(patient_id, "disconnected")
            print(f"[WS-ESP32] ESP32 desconectada de paciente #{patient_id}")

    else:
        # Cliente Web (Psicólogo / Paciente)
        print(f"[WS-WEB] Cliente web conectado para paciente #{patient_id}")
        await registrar_cliente_web(patient_id, websocket)

        try:
            async for raw_message in websocket:
                pass
        except Exception as e:
            print(f"[WS-WEB] Conexión cliente web terminada: {e}")
        finally:
            await desregistrar_cliente_web(patient_id, websocket)
            print(f"[WS-WEB] Cliente web desconectado de paciente #{patient_id}")
