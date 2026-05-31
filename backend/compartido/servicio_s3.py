import os


def obtener_configuracion_s3():
    """Expone la configuracion prevista sin incluir credenciales en codigo."""
    return {
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "bucket": os.getenv("S3_BUCKET_ARCHIVOS", ""),
        "usos": ["comprobantes_pdf", "reportes_exportados", "evidencias"],
    }


def generar_ruta_archivo(categoria, nombre_archivo):
    return f"{categoria.strip('/')}/{nombre_archivo}"

