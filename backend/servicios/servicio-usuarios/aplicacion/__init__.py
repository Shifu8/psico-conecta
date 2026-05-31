from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from aplicacion.configuracion import Config
from aplicacion.extensiones import bcrypt, cors, db, jwt, migrate
from aplicacion.modelos import TokenBlocklist
from aplicacion.rutas import auth_bp, dashboard_bp, roles_bp, users_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "execution_options": {
                "schema_translate_map": {"usuarios_schema": None},
            }
        }

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/health")
    def health():
        return jsonify(estado="ok", servicio="servicio-usuarios")

    @jwt.token_in_blocklist_loader
    def token_is_revoked(_jwt_header, jwt_payload):
        return TokenBlocklist.query.filter_by(jti=jwt_payload["jti"]).first() is not None

    @jwt.revoked_token_loader
    def revoked_token(_jwt_header, _jwt_payload):
        return jsonify(message="La sesion fue cerrada. Inicia sesion nuevamente."), 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(message="Se requiere autenticacion.", detail=reason), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify(message="Token invalido.", detail=reason), 422

    @app.errorhandler(ValidationError)
    def handle_validation(error):
        return jsonify(message="Datos invalidos.", errors=error.messages), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        db.session.rollback()
        return jsonify(message=str(error)), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(message=error.description), error.code

    return app


