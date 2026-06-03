import os

from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from aplicacion.configuracion import Config
from aplicacion.extensiones import bcrypt, cors, db, jwt, migrate
from aplicacion.modelos import TokenBlocklist
from aplicacion.rutas import auth_bp, dashboard_bp, roles_bp, users_bp
from aplicacion.utilidades.intentos_login import TooManyLoginAttemptsError


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError(
            "DATABASE_URL no definido. Copia .env.example a .env y configura PostgreSQL."
        )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return jsonify(estado="ok", servicio="servicio-usuarios")

    @app.post("/seed")
    def seed():
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from datos_iniciales import seed_database
        try:
            seed_database()
            return jsonify(message="Base de datos inicializada con datos demo."), 201
        except Exception as e:
            return jsonify(message=str(e)), 500

    @jwt.token_in_blocklist_loader
    def token_is_revoked(_jwt_header, jwt_payload):
        return TokenBlocklist.query.filter_by(jti=jwt_payload["jti"]).first() is not None

    @jwt.revoked_token_loader
    def revoked_token(_jwt_header, _jwt_payload):
        return jsonify(message="La sesión fue cerrada. Inicia sesión nuevamente."), 401

    @jwt.unauthorized_loader
    def missing_token(_reason):
        return jsonify(message="Se requiere autenticación."), 401

    @jwt.invalid_token_loader
    def invalid_token(_reason):
        return jsonify(message="Token inválido."), 422

    @jwt.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return jsonify(message="Tu sesión expiró. Inicia sesión nuevamente."), 401

    @app.errorhandler(ValidationError)
    def handle_validation(error):
        return jsonify(message="Revisa los datos ingresados.", errors=error.messages), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        db.session.rollback()
        return jsonify(message=str(error)), 400

    @app.errorhandler(TooManyLoginAttemptsError)
    def handle_too_many_login_attempts(error):
        response = jsonify(message=str(error))
        response.headers["Retry-After"] = str(error.retry_after)
        return response, 429

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(message=error.description), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        app.logger.exception("Error interno no controlado: %s", error)
        return jsonify(message="Ocurrió un error interno. Intenta nuevamente."), 500

    return app


