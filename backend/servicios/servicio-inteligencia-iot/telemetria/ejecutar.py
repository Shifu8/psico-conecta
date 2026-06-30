import asyncio
import os
import websockets
from dotenv import load_dotenv
from aplicacion import handler, loop_limpieza_buffer

load_dotenv()

async def main():
    port = int(os.getenv("PORT_TELEMETRIA", "5006"))
    print(f"[+] Iniciando servidor de telemetría asíncrono en el puerto {port}...")
    
    # Iniciar bucle de persistencia de fondo para DynamoDB
    asyncio.create_task(loop_limpieza_buffer())
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Ejecutar de forma indefinida

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[-] Servidor de telemetría detenido por el usuario.")
