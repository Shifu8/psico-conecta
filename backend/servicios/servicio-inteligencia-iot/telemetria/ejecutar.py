import asyncio
import os
import sys
import websockets
from dotenv import load_dotenv

# Asegurar que el directorio de 'telemetria' esté en el path para importar correctamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aplicacion import handler, loop_limpieza_buffer

load_dotenv()

async def main():
    port = int(os.getenv("PORT_TELEMETRIA", "5006"))
    print(f"[+] Iniciando servidor de telemetría WebSocket en el puerto {port}...")
    print(f"[+] El ESP32 debe conectar a: ws://<host>:{port}/esp32?device_token=<token>")
    
    # Iniciar bucle de persistencia de fondo para DynamoDB
    asyncio.create_task(loop_limpieza_buffer())
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Ejecutar de forma indefinida

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[-] Servidor de telemetría detenido por el usuario.")
