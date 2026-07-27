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
DEVICE_TOKEN   = os.getenv("DEVICE_TOKEN", "esp32_secret_device_token_2026")

# Configuración AWS/DynamoDB
AWS_REGION          = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_LECTURAS_IOT", "lecturas_iot")

try:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table    = dynamodb.Table(DYNAMODB_TABLE_NAME)
except Exception as e:
    print(f"[!] Advertencia: Error inicializando DynamoDB: {e}")
    table = None

# ── Registro en memoria ────────────────────────────────────────────────────────
# Clientes web (psicólogos): patient_id → set de websockets
web_clients: dict = {}
# Conexiones ESP32 activas: patient_id → websocket
esp32_connections: dict = {}
# Buffer de lecturas crudas: patient_id → list[int]
buffer_pacientes: dict = {}

# Mapeo de patient_id a nombre (complementar desde la base de datos si se desea)
PACIENTES_MAP = {
    "1": "Paciente 1",
    "2": "Paciente 2",
    "3": "Paciente 3",
    "4": "Justin Gutiérrez",
}

# ── Persistencia DynamoDB ──────────────────────────────────────────────────────

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
        print(f"[Cloud] Persistido lote de {len(raw_values)} lecturas para paciente "
              f"{patient_id} ({patient_name}) en DynamoDB.")
    except Exception as e:
        print(f"[!] Error al persistir en DynamoDB (paciente {patient_id}): {e}")


async def guardar_batch_dynamodb(patient_id: str, raw_values: list):
    """Ejecuta la escritura a DynamoDB en un hilo secundario para no bloquear el loop."""
    await asyncio.to_thread(_save_to_dynamo_sync, patient_id, raw_values)


async def loop_limpieza_buffer():
    """Vacía los buffers de lecturas cada 2 segundos y los persiste en DynamoDB."""
    print("[+] Bucle de persistencia de telemetría iniciado (intervalo: 2s).")
    while True:
        await asyncio.sleep(2.0)
        for p_id in list(buffer_pacientes.keys()):
            if buffer_pacientes[p_id]:
                lote = list(buffer_pacientes[p_id])
                buffer_pacientes[p_id].clear()
                asyncio.create_task(guardar_batch_dynamodb(p_id, lote))

# ── Gestión de clientes web ────────────────────────────────────────────────────

async def registrar_cliente_web(patient_id: str, websocket):
    web_clients.setdefault(patient_id, set()).add(websocket)
    # Notificar el estado actual del ESP32 al nuevo cliente
    estado = "connected" if patient_id in esp32_connections else "disconnected"
    await websocket.send(json.dumps({"type": "status", "status": estado}))


async def desregistrar_cliente_web(patient_id: str, websocket):
    if patient_id in web_clients:
        web_clients[patient_id].discard(websocket)
        if not web_clients[patient_id]:
            del web_clients[patient_id]


async def notificar_estado_esp32(patient_id: str, estado: str):
    """Envía el estado de conexión del ESP32 a todos los clientes web del paciente."""
    if patient_id in web_clients:
        msg   = json.dumps({"type": "status", "status": estado})
        tasks = [asyncio.create_task(ws.send(msg)) for ws in web_clients[patient_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


async def retransmitir_datos(patient_id: str, datos: dict):
    """Reenvía los datos del ESP32 a todos los clientes web del paciente."""
    if patient_id in web_clients:
        msg   = json.dumps({"type": "data", "data": datos})
        tasks = [asyncio.create_task(ws.send(msg)) for ws in web_clients[patient_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

# ── Handler principal WebSocket ────────────────────────────────────────────────

async def handler(websocket, path=None):
    """
    Punto de entrada para todas las conexiones WebSocket.
    
    Rutas soportadas (a través de Nginx):
      - /esp32            → dispositivo hardware ESP32
      - /ws/esp32         → simulador software (misma lógica)
      - /api/telemetria/ws → cliente web (psicólogo/dashboard)
    """
    # La librería websockets ≥ 10 pasa el path dentro del objeto websocket
    if path is None:
        try:
            path = websocket.path
        except AttributeError:
            path = "/"

    parsed      = urlparse(path)
    query       = parse_qs(parsed.query)
    actual_path = parsed.path

    is_esp32 = "esp32" in actual_path

    # ── Conexión ESP32 ──────────────────────────────────────────────────────────
    if is_esp32:
        # Validar token de dispositivo (query param o cabecera)
        token_recibido = (query.get("device_token", [None])[0]
                          or websocket.request_headers.get("X-Device-Token"))

        if token_recibido != DEVICE_TOKEN:
            print(f"[-] ESP32 rechazado desde {websocket.remote_address}: token inválido.")
            await websocket.close(1008, "Token inválido")
            return

        # patient_id puede venir en la URL (nuevo firmware) o en el primer mensaje JSON
        patient_id_url = query.get("patient_id", [None])[0]
        patient_id     = patient_id_url  # Puede ser None si lo envía en el JSON

        if patient_id:
            print(f"[+] ESP32 autenticado para paciente {patient_id} "
                  f"({websocket.remote_address})")
            esp32_connections[patient_id] = websocket
            await notificar_estado_esp32(patient_id, "connected")
        else:
            print(f"[+] ESP32 autenticado (paciente desconocido aún) "
                  f"({websocket.remote_address})")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)

                    # Ignorar mensajes de handshake que no tienen raw_value
                    if data.get("type") == "hello":
                        pid = str(data.get("patient_id", ""))
                        if pid and pid != patient_id:
                            if patient_id and esp32_connections.get(patient_id) == websocket:
                                del esp32_connections[patient_id]
                                await notificar_estado_esp32(patient_id, "disconnected")
                            patient_id = pid
                            esp32_connections[patient_id] = websocket
                            await notificar_estado_esp32(patient_id, "connected")
                            print(f"[+] ESP32 vinculado al paciente {patient_id}.")
                        continue

                    # Extraer patient_id del JSON si aún no está definido
                    val_pid = str(data.get("patient_id", ""))
                    if val_pid and val_pid != patient_id:
                        if patient_id and esp32_connections.get(patient_id) == websocket:
                            del esp32_connections[patient_id]
                            await notificar_estado_esp32(patient_id, "disconnected")
                        patient_id = val_pid
                        esp32_connections[patient_id] = websocket
                        await notificar_estado_esp32(patient_id, "connected")

                    if not patient_id:
                        continue

                    # Retransmitir en tiempo real a los clientes web
                    await retransmitir_datos(patient_id, data)

                    # Acumular en buffer para persistencia por lotes en DynamoDB
                    raw_value = data.get("raw_value")
                    if raw_value is not None:
                        buffer_pacientes.setdefault(patient_id, []).append(int(raw_value))
                        # Vaciado inmediato si el buffer supera 100 lecturas (~2 segundos de datos)
                        if len(buffer_pacientes[patient_id]) >= 100:
                            lote = list(buffer_pacientes[patient_id])
                            buffer_pacientes[patient_id].clear()
                            asyncio.create_task(guardar_batch_dynamodb(patient_id, lote))

                except json.JSONDecodeError:
                    pass  # Ignorar mensajes malformados

        except Exception as e:
            print(f"[-] Error en canal ESP32: {e}")
        finally:
            if patient_id and esp32_connections.get(patient_id) == websocket:
                del esp32_connections[patient_id]
                await notificar_estado_esp32(patient_id, "disconnected")
            print(f"[-] Conexión ESP32 cerrada (paciente: {patient_id}).")

    # ── Conexión cliente web (psicólogo / dashboard) ────────────────────────────
    else:
        token      = query.get("token", [None])[0]
        patient_id = query.get("patient_id", [None])[0]

        if not token or not patient_id:
            print("[-] Cliente web rechazado: falta 'token' o 'patient_id' en la URL.")
            await websocket.close(1008, "Parámetros incompletos")
            return

        # Verificar JWT
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            role    = payload.get("role") or payload.get("user_claims", {}).get("role")
            if role != "PSYCHOLOGIST":
                print(f"[-] Acceso denegado al cliente web: rol '{role}' no autorizado.")
                await websocket.close(1008, "No autorizado")
                return
        except jwt.ExpiredSignatureError:
            print("[-] JWT expirado.")
            await websocket.close(1008, "Token expirado")
            return
        except jwt.InvalidTokenError as e:
            print(f"[-] JWT inválido: {e}")
            await websocket.close(1008, "Token inválido")
            return

        patient_id = str(patient_id)
        await registrar_cliente_web(patient_id, websocket)
        print(f"[+] Psicólogo conectado para paciente {patient_id} ({websocket.remote_address}).")

        try:
            async for _ in websocket:
                pass  # El cliente web es solo receptor; no envía datos
        except Exception:
            pass
        finally:
            await desregistrar_cliente_web(patient_id, websocket)
            print(f"[-] Psicólogo desconectado (paciente: {patient_id}).")
