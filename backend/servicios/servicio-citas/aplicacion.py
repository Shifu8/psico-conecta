"""Punto de entrada compatible. Usa la aplicación real del paquete ``app``."""

from ejecutar import app


if __name__ == "__main__":
    import os

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")))
