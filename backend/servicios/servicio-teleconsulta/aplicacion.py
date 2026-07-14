"""Punto de entrada conservado por compatibilidad con comandos anteriores."""
from ejecutar import app

if __name__ == "__main__":
    import os

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5003")), debug=False)
