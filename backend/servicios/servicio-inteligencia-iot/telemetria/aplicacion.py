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
DEVICE_TOKEN = os.getenv("DEVICE_TOKEN", "PsicoConectaSecureToken2026")

# Configuración AWS/DynamoDB
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_LECTURAS_IOT", "lecturas_iot")

try:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
except Exception as e:
    print(f"[!] Advertencia: Error inicializando DynamoDB: {e}")
    table = None

# Clientes web: cita_id -> set de websockets
web_clients = {}
# Conexiones ESP32: cita_id -> websocket
esp32_connections = {}
# Buffer en memoria de lecturas de la ESP32: cita_id -> list of raw_values
buffer_citas = {}

# Mapeos activos de sesión para enlazar la ESP32 si conecta por canal general /esp32
cita_to_patient = {}
patient_to_cita = {}

# Mapeo global de identificadores a nombres de pacientes
PACIENTES_MAP = {
    "4": "Justin Gutiérrez"
}

def _save_to_dynamo_sync(patient_id, raw_values):
    if table is None:
        print(f"[!] DynamoDB no está disponible. Ignorando persistencia de lote para paciente {patient_id}.")
        return
    try:
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        now_local = datetime.now()
        patient_name = PACIENTES_MAP.get(str(patient_id), "Desconocido")
        hora_captura = now_local.strftime("%H:%M:%S")
        fecha_local = now_local.strftime("%Y-%m-%d %H:%M:%S")
        
        table.put_item(Item={
            "patient_id": patient_id,
            "timestamp": timestamp_iso,
            "patient_name": patient_name,
            "hora_captura": hora_captura,
            "fecha_local": fecha_local,
            "raw_values": raw_values
        })
        print(f"[Cloud] Persistido lote de {len(raw_values)} lecturas para paciente {patient_id} ({patient_name}) en DynamoDB.")
    except Exception as e:
        print(f"[!] Error al persistir lote en DynamoDB para paciente {patient_id}: {e}")

async def guardar_batch_dynamodb(patient_id, raw_values):
    # Ejecutar en hilo secundario para evitar bloquear el event loop asíncrono
    await asyncio.to_thread(_save_to_dynamo_sync, patient_id, raw_values)

async def loop_limpieza_buffer():
    print("[+] Iniciando bucle de limpieza y persistencia de buffers de telemetría...")
    while True:
        await asyncio.sleep(2.0)
        # Recorrer de forma segura los buffers existentes
        for c_id in list(buffer_citas.keys()):
            if buffer_citas[c_id]:
                p_id = cita_to_patient.get(c_id, "unknown")
                lote_a_guardar = list(buffer_citas[c_id])
                buffer_citas[c_id].clear()
                asyncio.create_task(guardar_batch_dynamodb(p_id, lote_a_guardar))

async def registrar_cliente_web(cita_id, patient_id, websocket):
    cita_id = str(cita_id)
    patient_id = str(patient_id)
    
    # Enlazar la sesión activa para la ESP32
    cita_to_patient[cita_id] = patient_id
    patient_to_cita[patient_id] = cita_id

    if cita_id not in web_clients:
        web_clients[cita_id] = set()
    web_clients[cita_id].add(websocket)
    
    # Notificar estado inicial de la placa ESP32 para esta cita
    estado_esp32 = "connected" if cita_id in esp32_connections else "disconnected"
    await websocket.send(json.dumps({
        "type": "status",
        "status": estado_esp32
    }))

async def desregistrar_cliente_web(cita_id, websocket):
    cita_id = str(cita_id)
    if cita_id in web_clients:
        web_clients[cita_id].discard(websocket)
        if not web_clients[cita_id]:
            del web_clients[cita_id]
            # Limpiar mapeo si ya no hay nadie conectado a esta cita
            p_id = cita_to_patient.pop(cita_id, None)
            if p_id:
                patient_to_cita.pop(p_id, None)

async def notificar_estado_esp32(cita_id, estado):
    cita_id = str(cita_id)
    if cita_id in web_clients:
        mensaje = json.dumps({
            "type": "status",
            "status": estado
        })
        tasks = [asyncio.create_task(client.send(mensaje)) for client in web_clients[cita_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def retransmitir_datos(cita_id, datos):
    cita_id = str(cita_id)
    if cita_id in web_clients:
        mensaje = json.dumps({
            "type": "data",
            "data": datos
        })
        tasks = [asyncio.create_task(client.send(mensaje)) for client in web_clients[cita_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def handler(websocket, path):
    # Analizar parámetros y ruta
    parsed_url = urlparse(path)
    query_params = parse_qs(parsed_url.query)
    actual_path = parsed_url.path
    
    clean_path = actual_path.strip("/")
    parts = clean_path.split("/")
    
    # Buscar cita_id y determinar si es conexión de hardware (ESP32)
    cita_id = None
    is_esp32 = "esp32" in parts or "esp32" in actual_path
    
    if is_esp32:
        # Rutas ESP32 posibles:
        # - esp32/<cita_id>
        # - api/telemetria/ws/<cita_id>/esp32
        # - esp32 (canal general sin cita_id en el path, se resuelve por paciente)
        if len(parts) >= 2 and parts[0] == "esp32":
            cita_id = parts[1]
        elif len(parts) >= 4 and parts[2] == "ws" and parts[-1] == "esp32":
            cita_id = parts[3]
    else:
        # Rutas Cliente Web posibles:
        # - api/telemetria/ws/<cita_id>
        # - ws/<cita_id>
        if len(parts) >= 4 and parts[2] == "ws":
            cita_id = parts[3]
        elif len(parts) >= 2 and parts[0] == "ws":
            cita_id = parts[1]
            
    print(f"[WS] Nueva conexión. Path: {actual_path}, is_esp32: {is_esp32}, cita_id: {cita_id}")
    
    if is_esp32:
        # Validar llave de seguridad estática
        token_recibido = query_params.get("device_token", [None])[0]
        if not token_recibido:
            token_recibido = websocket.request_headers.get("X-Device-Token")
            
        if token_recibido != DEVICE_TOKEN:
            print("[-] Conexión de ESP32 rechazada: Token de dispositivo inválido.")
            await websocket.close(1008, "Token inválido")
            return
            
        print("[+] Conexión de ESP32 autenticada exitosamente.")
        current_cita_id = None
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    val_patient_id = str(data.get("patient_id"))
                    if not val_patient_id:
                        continue
                    
                    # Resolver cita_id si no se obtuvo del path
                    actual_cita_id = cita_id or patient_to_cita.get(val_patient_id)
                    if not actual_cita_id:
                        actual_cita_id = f"fallback_{val_patient_id}"
                    
                    if current_cita_id != actual_cita_id:
                        if current_cita_id and esp32_connections.get(current_cita_id) == websocket:
                            del esp32_connections[current_cita_id]
                            await notificar_estado_esp32(current_cita_id, "disconnected")
                            
                        current_cita_id = actual_cita_id
                        esp32_connections[current_cita_id] = websocket
                        await notificar_estado_esp32(current_cita_id, "connected")
                        
                    await retransmitir_datos(current_cita_id, data)
                    
                    # Persistencia en búfer para DynamoDB
                    raw_value = data.get("raw_value")
                    if raw_value is not None:
                        if current_cita_id not in buffer_citas:
                            buffer_citas[current_cita_id] = []
                        buffer_citas[current_cita_id].append(int(raw_value))
                        
                        # Vaciado atómico al llegar a 100 elementos
                        if len(buffer_citas[current_cita_id]) >= 100:
                            lote_a_guardar = list(buffer_citas[current_cita_id])
                            buffer_citas[current_cita_id].clear()
                            real_p_id = cita_to_patient.get(current_cita_id, val_patient_id)
                            asyncio.create_task(guardar_batch_dynamodb(real_p_id, lote_a_guardar))
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"[-] Error en canal ESP32: {e}")
        finally:
            if current_cita_id:
                if esp32_connections.get(current_cita_id) == websocket:
                    del esp32_connections[current_cita_id]
                await notificar_estado_esp32(current_cita_id, "disconnected")
            print("[-] Conexión de ESP32 finalizada.")
            
    else:
        # Cliente web (Psicólogo o Paciente)
        token = query_params.get("token", [None])[0]
        patient_id = query_params.get("patient_id", [None])[0]
        
        if not token or not patient_id or not cita_id:
            print(f"[-] Conexión web rechazada: Parámetros incompletos. token={bool(token)}, patient_id={patient_id}, cita_id={cita_id}")
            await websocket.close(1008, "Parámetros incompletos")
            return
            
        # Decodificar y validar JWT
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            role = payload.get("role") or payload.get("user_claims", {}).get("role")
            if role not in ["PSYCHOLOGIST", "PATIENT"]:
                print(f"[-] Acceso denegado: El rol '{role}' no está autorizado.")
                await websocket.close(1008, "No autorizado")
                return
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            print(f"[-] Validación de token JWT fallida: {e}")
            await websocket.close(1008, "Token inválido o expirado")
            return
            
        patient_id = str(patient_id)
        cita_id = str(cita_id)
        
        await registrar_cliente_web(cita_id, patient_id, websocket)
        print(f"[+] Cliente web ({role}) conectado para la cita {cita_id} (paciente {patient_id}).")
        
        try:
            async for message in websocket:
                pass
        except Exception as e:
            pass
        finally:
            await desregistrar_cliente_web(cita_id, websocket)
            print(f"[-] Cliente web ({role}) desconectado de la cita {cita_id}.")
