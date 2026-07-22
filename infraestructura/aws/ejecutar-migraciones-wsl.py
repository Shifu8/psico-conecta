import os
import sys
import psycopg2

db_url = "postgresql://postgres:PsicoConecta2026Secure!@psicoconecta-db.ctwi0kkq4isz.us-east-2.rds.amazonaws.com:5432/psicoconecta"

sql_files = [
    "infraestructura/postgres/inicializar_esquemas.sql",
    "infraestructura/postgres/migracion_fecha_nacimiento_usuarios.sql",
    "infraestructura/postgres/migracion_eventos_auditoria.sql",
    "infraestructura/postgres/migracion_modulo_citas.sql",
    "infraestructura/postgres/migracion_modulo_teleconsultas.sql",
    "infraestructura/postgres/migracion_modulo_pagos.sql"
]

print("Conectando a RDS PostgreSQL...")
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

for path in sql_files:
    if os.path.exists(path):
        print(f"Ejecutando {path}...")
        with open(path, "r", encoding="utf-8") as fh:
            sql = fh.read()
        cur.execute(sql)
        print(f"  [OK] {path}")

cur.close()
conn.close()
print("Todas las migraciones fueron ejecutadas exitosamente en RDS.")
