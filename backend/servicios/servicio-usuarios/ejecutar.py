import os

from dotenv import load_dotenv

from aplicacion import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    depuracion = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5001")),
        debug=depuracion,
        use_reloader=False,
    )


