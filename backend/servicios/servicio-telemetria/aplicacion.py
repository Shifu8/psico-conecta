import os
import json
import jwt
import asyncio
from urllib.parse import urlparse, parse_qs

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_jwt_secret_at_least_32_chars")
DEVICE_TOKEN = os.getenv("DEVICE_TOKEN", "PsicoConectaSecureToken2026")

# Clientes web: patient_id -> set de websockets
web_clients = {}
# Conexiones ESP32: patient_id -> websocket
esp32_connections = {}

async def registrar_cliente_web(patient_id, websocket):
    if patient_id not in web_clients:
        web_clients[patient_id] = set()
    web_clients[patient_id].add(websocket)
    
    # Notificar estado inicial de la placa ESP32
    estado_esp32 = "connected" if patient_id in esp32_connections else "disconnected"
    await websocket.send(json.dumps({
        "type": "status",
        "status": estado_esp32
    }))

async def desregistrar_cliente_web(patient_id, websocket):
    if patient_id in web_clients:
        web_clients[patient_id].discard(websocket)
        if not web_clients[patient_id]:
            del web_clients[patient_id]

async def notificar_estado_esp32(patient_id, estado):
    if patient_id in web_clients:
        mensaje = json.dumps({
            "type": "status",
            "status": estado
        })
        tasks = [asyncio.create_task(client.send(mensaje)) for client in web_clients[patient_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def retransmitir_datos(patient_id, datos):
    if patient_id in web_clients:
        mensaje = json.dumps({
            "type": "data",
            "data": datos
        })
        tasks = [asyncio.create_task(client.send(mensaje)) for client in web_clients[patient_id]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def handler(websocket, path):
    # Analizar parámetros y ruta
    parsed_url = urlparse(path)
    query_params = parse_qs(parsed_url.query)
    actual_path = parsed_url.path
    
    # Determinar si es placa ESP32 o panel del psicólogo
    is_esp32 = "esp32" in actual_path
    
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
        patient_id = None
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    val_patient_id = str(data.get("patient_id"))
                    if not val_patient_id:
                        continue
                    
                    if patient_id != val_patient_id:
                        if patient_id and esp32_connections.get(patient_id) == websocket:
                            del esp32_connections[patient_id]
                            await notificar_estado_esp32(patient_id, "disconnected")
                            
                        patient_id = val_patient_id
                        esp32_connections[patient_id] = websocket
                        await notificar_estado_esp32(patient_id, "connected")
                        
                    await retransmitir_datos(patient_id, data)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"[-] Error en canal ESP32: {e}")
        finally:
            if patient_id:
                if esp32_connections.get(patient_id) == websocket:
                    del esp32_connections[patient_id]
                await notificar_estado_esp32(patient_id, "disconnected")
            print("[-] Conexión de ESP32 finalizada.")
            
    else:
        # Cliente web (Psicólogo)
        token = query_params.get("token", [None])[0]
        patient_id = query_params.get("patient_id", [None])[0]
        
        if not token or not patient_id:
            print("[-] Conexión web rechazada: Falta token o patient_id.")
            await websocket.close(1008, "Parámetros incompletos")
            return
            
        # Decodificar y validar JWT
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            role = payload.get("role") or payload.get("user_claims", {}).get("role")
            if role != "PSYCHOLOGIST":
                print(f"[-] Acceso denegado: El rol '{role}' no está autorizado.")
                await websocket.close(1008, "No autorizado")
                return
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            print(f"[-] Validación de token JWT fallida: {e}")
            await websocket.close(1008, "Token inválido o expirado")
            return
            
        patient_id = str(patient_id)
        await registrar_cliente_web(patient_id, websocket)
        print(f"[+] Psicólogo conectado para monitorear paciente {patient_id}.")
        
        try:
            async for message in websocket:
                pass
        except Exception as e:
            pass
        finally:
            await desregistrar_cliente_web(patient_id, websocket)
            print(f"[-] Psicólogo desconectado del paciente {patient_id}.")
