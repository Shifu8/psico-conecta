import asyncio
import os
import websockets
from dotenv import load_dotenv
from aplicacion import handler

load_dotenv()

async def main():
    port = int(os.getenv("PORT", "5006"))
    print(f"[+] Iniciando servidor de telemetría asíncrono en el puerto {port}...")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Ejecutar de forma indefinida

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[-] Servidor de telemetría detenido por el usuario.")
