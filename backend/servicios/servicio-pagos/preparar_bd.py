"""Crea o actualiza las tablas del servicio de pagos de forma idempotente."""

import re

from sqlalchemy import inspect, text

from app import create_app, db


IDENTIFICADOR_SEGURO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TABLAS_REQUERIDAS = {"pagos", "transacciones", "reembolsos", "tarifas"}


def preparar_base_de_datos():
    aplicacion = create_app()
    with aplicacion.app_context():
        schema = aplicacion.config.get("DB_SCHEMA") or None
        if schema and not IDENTIFICADOR_SEGURO.fullmatch(schema):
            raise RuntimeError(f"DB_SCHEMA no válido: {schema!r}")

        if schema and db.engine.dialect.name == "postgresql":
            with db.engine.begin() as conexion:
                conexion.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

        inspector = inspect(db.engine)
        tablas_existentes = set(inspector.get_table_names(schema=schema))
        if "pagos" in tablas_existentes:
            columnas = {item["name"] for item in inspector.get_columns("pagos", schema=schema)}
            columnas_nuevas = {"cita_id", "paciente_id", "psicologo_id", "monto_centavos"}
            if not columnas_nuevas.issubset(columnas):
                prefijo = f'"{schema}".' if schema else ""
                with db.engine.begin() as conexion:
                    for tabla in ("comprobantes", "transacciones", "pagos"):
                        existentes = set(inspect(conexion).get_table_names(schema=schema))
                        if tabla in existentes and f"{tabla}_legacy" not in existentes:
                            conexion.execute(text(
                                f'ALTER TABLE {prefijo}"{tabla}" RENAME TO "{tabla}_legacy"'
                            ))
                print("Esquema antiguo de pagos conservado con sufijo _legacy.")

        db.create_all()
        tablas_finales = set(inspect(db.engine).get_table_names(schema=schema))
        faltantes = sorted(TABLAS_REQUERIDAS - tablas_finales)
        if faltantes:
            raise RuntimeError(f"No fue posible crear las tablas de pagos: {', '.join(faltantes)}")
        print("Esquema de pagos verificado correctamente.")


if __name__ == "__main__":
    preparar_base_de_datos()
