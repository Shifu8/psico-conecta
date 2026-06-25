# Archivo: __init__.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Registrar blueprints
    from app.rutas.rutas_citas import bp_citas
    from app.rutas.rutas_disponibilidad import bp_disponibilidad

    app.register_blueprint(bp_citas, url_prefix='/api/citas')
    app.register_blueprint(bp_disponibilidad, url_prefix='/api/disponibilidad')

    @app.route("/health")
    def health():
        return {"estado": "ok", "servicio": "servicio-citas"}

    return app
