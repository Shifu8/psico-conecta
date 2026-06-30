import asyncio
import json
import jwt
import sys
import websockets

JWT_SECRET_KEY = "change_this_jwt_secret_at_least_32_chars"
DEVICE_TOKEN = "PsicoConectaSecureToken2026"
WS_URL = "ws://localhost:5006"

def generar_token(user_id, role):
    payload = {
        "sub": str(user_id),
        "role": role
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

async def test_esp32_sin_token():
    print("[Prueba] Intentando conectar ESP32 sin token...")
    try:
        async with websockets.connect(f"{WS_URL}/esp32") as ws:
            await ws.recv()
            print("ERROR: La conexión sin token fue permitida!")
            return False
    except websockets.exceptions.ConnectionClosed as e:
        if e.rcvd.code == 1008:
            print(f"OK: Conexión rechazada con código esperado: {e.rcvd.code}")
            return True
        else:
            print(f"ERROR: Conexión cerrada con código inesperado: {e.rcvd.code}")
            return False
    except Exception as e:
        print(f"OK: Conexión rechazada con excepción: {e}")
        return True

async def test_esp32_token_invalido():
    print("[Prueba] Intentando conectar ESP32 con token inválido...")
    try:
        async with websockets.connect(f"{WS_URL}/esp32?device_token=token_falso") as ws:
            await ws.recv()
            print("ERROR: La conexión con token inválido fue permitida!")
            return False
    except websockets.exceptions.ConnectionClosed as e:
        if e.rcvd.code == 1008:
            print(f"OK: Conexión rechazada con código esperado: {e.rcvd.code}")
            return True
        else:
            print(f"ERROR: Conexión cerrada con código inesperado: {e.rcvd.code}")
            return False
    except Exception as e:
        print(f"OK: Conexión rechazada con excepción: {e}")
        return True

async def test_web_sin_token():
    print("[Prueba] Intentando conectar Cliente Web sin token...")
    try:
        async with websockets.connect(f"{WS_URL}/api/telemetria/ws?patient_id=1") as ws:
            await ws.recv()
            print("ERROR: La conexión sin token fue permitida!")
            return False
    except websockets.exceptions.ConnectionClosed as e:
        if e.rcvd.code == 1008:
            print(f"OK: Conexión rechazada con código esperado: {e.rcvd.code}")
            return True
        else:
            print(f"ERROR: Conexión cerrada con código inesperado: {e.rcvd.code}")
            return False
    except Exception as e:
        print(f"OK: Conexión rechazada con excepción: {e}")
        return True

async def test_web_rol_paciente():
    print("[Prueba] Intentando conectar Cliente Web con rol PATIENT...")
    token = generar_token(10, "PATIENT")
    try:
        async with websockets.connect(f"{WS_URL}/api/telemetria/ws?token={token}&patient_id=1") as ws:
            await ws.recv()
            print("ERROR: La conexión con rol de paciente fue permitida!")
            return False
    except websockets.exceptions.ConnectionClosed as e:
        if e.rcvd.code == 1008:
            print(f"OK: Conexión de paciente rechazada con éxito: {e.rcvd.code}")
            return True
        else:
            print(f"ERROR: Conexión cerrada con código inesperado: {e.rcvd.code}")
            return False
    except Exception as e:
        print(f"OK: Conexión rechazada con excepción: {e}")
        return True

async def test_flujo_completo():
    print("[Prueba] Probando flujo completo de comunicación...")
    token_psicologo = generar_token(5, "PSYCHOLOGIST")
    
    try:
        # 1. Conectar Psicólogo
        ws_web = await websockets.connect(f"{WS_URL}/api/telemetria/ws?token={token_psicologo}&patient_id=1")
        # Recibir estado inicial de la placa (desconectada)
        msg = await ws_web.recv()
        status_msg = json.loads(msg)
        print(f"[Web] Estado inicial del ESP32 recibido: {status_msg}")
        assert status_msg["type"] == "status"
        assert status_msg["status"] == "disconnected"
        
        # 2. Conectar ESP32
        ws_esp = await websockets.connect(f"{WS_URL}/esp32?device_token={DEVICE_TOKEN}")
        print("[ESP32] Placa conectada.")
        
        # Enviar datos iniciales inmediatamente para registrar el patient_id en el servidor
        datos_enviados = {"patient_id": "1", "raw_value": 2048}
        await ws_esp.send(json.dumps(datos_enviados))
        print("[ESP32] Datos iniciales enviados.")
        
        # El psicólogo debe recibir el cambio de estado a conectado
        msg = await ws_web.recv()
        status_msg = json.loads(msg)
        print(f"[Web] Nuevo estado del ESP32 recibido: {status_msg}")
        assert status_msg["type"] == "status"
        assert status_msg["status"] == "connected"
        
        # El psicólogo debe recibir los datos retransmitidos
        msg = await ws_web.recv()
        data_msg = json.loads(msg)
        print(f"[Web] Datos recibidos: {data_msg}")
        assert data_msg["type"] == "data"
        assert data_msg["data"]["raw_value"] == 2048
        
        # 4. Desconectar ESP32
        await ws_esp.close()
        print("[ESP32] Placa desconectada.")
        
        # El psicólogo debe recibir la desconexión
        msg = await ws_web.recv()
        status_msg = json.loads(msg)
        print(f"[Web] Estado de ESP32 final recibido: {status_msg}")
        assert status_msg["type"] == "status"
        assert status_msg["status"] == "disconnected"
        
        await ws_web.close()
        print("OK: Flujo completo verificado con éxito.")
        return True
    except Exception as e:
        print(f"ERROR en flujo completo: {e}")
        return False

async def main():
    print("=== INICIANDO PRUEBAS DE TELEMETRÍA E INTEGRACIÓN ===")
    exitos = []
    
    exitos.append(await test_esp32_sin_token())
    exitos.append(await test_esp32_token_invalido())
    exitos.append(await test_web_sin_token())
    exitos.append(await test_web_rol_paciente())
    exitos.append(await test_flujo_completo())
    
    total = len(exitos)
    pasados = sum(1 for x in exitos if x)
    print(f"\n=== RESULTADOS: {pasados}/{total} PRUEBAS PASADAS ===")
    if pasados == total:
        print("¡Todo funciona perfectamente!")
        sys.exit(0)
    else:
        print("Hubo fallos en las pruebas.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
