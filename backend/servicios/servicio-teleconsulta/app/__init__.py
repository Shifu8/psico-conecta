from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from app.utilidades.errores import ErrorDominio


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class="app.config.Config", test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import modelos  # noqa: F401
    from app.rutas import bp, bp_webhooks

    app.register_blueprint(bp, url_prefix="/api/teleconsultas")
    app.register_blueprint(bp_webhooks, url_prefix="/api/teleconsultas/webhooks")

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            zoom_ok = all([
                app.config["ZOOM_ACCOUNT_ID"],
                app.config["ZOOM_CLIENT_ID"],
                app.config["ZOOM_CLIENT_SECRET"],
                app.config["ZOOM_HOST_USER_ID"] or app.config["ZOOM_HOSTS"],
            ])
            return jsonify(
                estado="ok",
                servicio="servicio-teleconsulta",
                base_datos="ok",
                zoom="configurado" if zoom_ok else "no_configurado",
            )
        except Exception:
            db.session.rollback()
            return jsonify(estado="error", servicio="servicio-teleconsulta", base_datos="no_disponible"), 503

    @jwt.unauthorized_loader
    def token_faltante(_motivo):
        return jsonify(error="autenticacion_requerida", mensaje="Se requiere autenticación."), 401

    @jwt.invalid_token_loader
    def token_invalido(_motivo):
        return jsonify(error="token_invalido", mensaje="El token no es válido."), 401

    @jwt.expired_token_loader
    def token_expirado(_cabecera, _contenido):
        return jsonify(error="token_expirado", mensaje="La sesión expiró."), 401

    @app.errorhandler(ErrorDominio)
    def error_dominio(error):
        db.session.rollback()
        datos = {"error": error.error, "mensaje": error.mensaje}
        if error.detalles is not None:
            datos["detalles"] = error.detalles
        return jsonify(datos), error.codigo

    @app.errorhandler(ValidationError)
    def error_validacion(error):
        db.session.rollback()
        return jsonify(error="datos_invalidos", mensaje="Revisa los datos enviados.", detalles=error.messages), 400

    @app.errorhandler(IntegrityError)
    def error_integridad(_error):
        db.session.rollback()
        return jsonify(error="conflicto_de_datos", mensaje="La sesión ya existe o entra en conflicto."), 409

    @app.errorhandler(HTTPException)
    def error_http(error):
        return jsonify(error="error_http", mensaje=error.description), error.code

    @app.errorhandler(Exception)
    def error_inesperado(error):
        db.session.rollback()
        app.logger.exception("Error en servicio-teleconsulta: %s", error)
        return jsonify(error="error_interno", mensaje="Ocurrió un error interno."), 500

    return app
