"""Asegura que el esquema de usuarios exista antes de ejecutar el seed."""

import re

from sqlalchemy import text

from aplicacion import create_app
from aplicacion.extensiones import db


IDENTIFICADOR_SEGURO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def preparar_base_de_datos():
    aplicacion = create_app()
    with aplicacion.app_context():
        schema = aplicacion.config.get("DATABASE_SCHEMA") or None
        if schema and not IDENTIFICADOR_SEGURO.fullmatch(schema):
            raise RuntimeError(f"DATABASE_SCHEMA no válido: {schema!r}")
        if schema and db.engine.dialect.name == "postgresql":
            with db.engine.begin() as conexion:
                conexion.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        db.create_all()
        print("Esquema de usuarios verificado correctamente.")


if __name__ == "__main__":
    preparar_base_de_datos()
