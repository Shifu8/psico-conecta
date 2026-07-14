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

    # Importa modelos antes de registrar rutas/migraciones.
    from app import modelos  # noqa: F401
    from app.rutas.rutas_citas import bp_citas
    from app.rutas.rutas_disponibilidad import bp_disponibilidad

    app.register_blueprint(bp_citas, url_prefix="/api/citas")
    app.register_blueprint(bp_disponibilidad, url_prefix="/api/disponibilidad")

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(estado="ok", servicio="servicio-citas", base_datos="ok")
        except Exception:
            db.session.rollback()
            return jsonify(estado="error", servicio="servicio-citas", base_datos="no_disponible"), 503

    @jwt.unauthorized_loader
    def token_faltante(_motivo):
        return jsonify(error="autenticacion_requerida", mensaje="Se requiere autenticación."), 401

    @jwt.invalid_token_loader
    def token_invalido(_motivo):
        return jsonify(error="token_invalido", mensaje="El token de acceso no es válido."), 401

    @jwt.expired_token_loader
    def token_expirado(_cabecera, _contenido):
        return jsonify(error="token_expirado", mensaje="La sesión expiró. Inicia sesión nuevamente."), 401

    @app.errorhandler(ErrorDominio)
    def manejar_error_dominio(error):
        db.session.rollback()
        respuesta = {"error": error.error, "mensaje": error.mensaje}
        if error.detalles is not None:
            respuesta["detalles"] = error.detalles
        return jsonify(respuesta), error.codigo

    @app.errorhandler(ValidationError)
    def manejar_validacion(error):
        db.session.rollback()
        return jsonify(
            error="datos_invalidos",
            mensaje="Revisa los datos enviados.",
            detalles=error.messages,
        ), 400

    @app.errorhandler(IntegrityError)
    def manejar_integridad(_error):
        db.session.rollback()
        return jsonify(
            error="conflicto_de_datos",
            mensaje="La operación entra en conflicto con información ya registrada.",
        ), 409

    @app.errorhandler(HTTPException)
    def manejar_http(error):
        return jsonify(error="error_http", mensaje=error.description), error.code

    @app.errorhandler(Exception)
    def manejar_error_inesperado(error):
        db.session.rollback()
        app.logger.exception("Error interno en servicio-citas: %s", error)
        return jsonify(
            error="error_interno",
            mensaje="Ocurrió un error interno al procesar la solicitud.",
        ), 500

    return app
