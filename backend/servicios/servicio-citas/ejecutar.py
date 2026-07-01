# Archivo: ejecutar.py
# Descripción: Inicialización y ejecución del servidor de la API.
# Módulo: Servicio Citas

import os
from dotenv import load_dotenv

load_dotenv()
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")))
