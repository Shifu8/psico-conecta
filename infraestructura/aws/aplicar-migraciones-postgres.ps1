param(
    [string]$Region = "us-east-2",
    [string]$SecretName = "psicoconecta/DATABASE_URL"
)

$ErrorActionPreference = "Stop"

$databaseUrl = aws secretsmanager get-secret-value --secret-id $SecretName --region $Region --query SecretString --output text
if (-not $databaseUrl -or $databaseUrl -eq "None") {
    throw "No se pudo leer $SecretName desde Secrets Manager."
}
if ($databaseUrl -match "localhost|127\.0\.0\.1|sqlite") {
    throw "DATABASE_URL no debe apuntar a local/SQLite."
}

$env:DATABASE_URL = $databaseUrl
$sqlFiles = @(
    "infraestructura/postgres/inicializar_esquemas.sql",
    "infraestructura/postgres/migracion_fecha_nacimiento_usuarios.sql",
    "infraestructura/postgres/migracion_eventos_auditoria.sql",
    "infraestructura/postgres/migracion_modulo_citas.sql",
    "infraestructura/postgres/migracion_modulo_teleconsultas.sql",
    "infraestructura/postgres/migracion_modulo_pagos.sql"
)

foreach ($file in $sqlFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "No existe el archivo de migracion: $file"
    }
}

$script = @'
import os
import sys
import psycopg

database_url = os.environ["DATABASE_URL"].strip()
if database_url.startswith("postgresql+psycopg://"):
    database_url = "postgresql://" + database_url[len("postgresql+psycopg://"):]

with psycopg.connect(database_url, autocommit=True) as conn:
    with conn.cursor() as cur:
        for path in sys.argv[1:]:
            with open(path, "r", encoding="utf-8") as fh:
                sql = fh.read()
            cur.execute(sql)
            print(f"OK {path}")
'@

try {
    $script | python - @sqlFiles
} finally {
    Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
}

Write-Host "Migraciones PostgreSQL aplicadas sin imprimir DATABASE_URL." -ForegroundColor Green
