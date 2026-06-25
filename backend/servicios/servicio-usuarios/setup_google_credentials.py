# Archivo: setup_google_credentials.py
# Descripción: Configuración para credenciales de Google API.
# Módulo: Servicio Usuarios

"""
Script para configurar Gmail API y Google Login.
Genera un enlace para autorizar y obtener el refresh token manualmente.

REQUISITO: pip install google-auth-oauthlib requests
"""
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

BASE_DIR = Path(__file__).resolve().parent

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", "TU_CLIENT_ID.apps.googleusercontent.com"),
        "project_id": os.environ.get("GOOGLE_PROJECT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", "TU_CLIENT_SECRET"),
        "redirect_uris": ["http://localhost"],
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def main():
    print("=" * 60)
    print("CONFIGURACION DE GMAIL API + GOOGLE LOGIN")
    print("=" * 60)
    print()
    if (
        CLIENT_CONFIG["installed"]["client_id"].startswith("TU_")
        or CLIENT_CONFIG["installed"]["client_secret"].startswith("TU_")
    ):
        print("Configura GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET antes de continuar.")
        return

    sender_email = input("Correo remitente autorizado para Gmail API: ").strip().lower()
    if "@" not in sender_email:
        print("Ingresa un correo remitente válido.")
        return

    print()
    print("Paso 1: Abre este enlace en el NAVEGADOR")
    print()
    print("  IMPORTANTE: Asegúrate de iniciar sesión con:")
    print(f"  {sender_email}")
    print()

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    print("  " + auth_url)
    print()
    print("Paso 2: Despues de autorizar, el navegador se quedara")
    print("  en una pagina en blanco o de error. Copia la URL completa")
    print("  de la barra de direcciones y pegalo aqui:")
    print()

    redirect_response = input("  URL despues de autorizar: ").strip()

    print()
    print("Paso 3: Intercambiando codigo por tokens...")
    print()

    try:
        from google_auth_oauthlib.helpers import _parse_state

        parsed = urlparse(redirect_response)
        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]

        if not code:
            # Try to parse from fragment
            params = parse_qs(parsed.fragment)
            code = params.get("code", [None])[0]

        if not code:
            print("No se pudo extraer el codigo de autorizacion.")
            print("Asegurate de copiar la URL completa de la barra de direcciones.")
            return

        flow.fetch_token(code=code)
        credenciales = flow.credentials
    except Exception as e:
        print(f"Error de autorización: {type(e).__name__}")
        print()
        print("Alternativa manual:")
        print("1. Abre el enlace de arriba")
        print(f"2. Autoriza con {sender_email}")
        print("3. Te redirigira a una URL como:")
        print("   http://localhost/?code=4/0A...&scope=...")
        print("4. Copia el codigo '4/0A...' (entre code= y &scope)")
        code = input("  Pega el codigo aqui: ").strip()
        if not code:
            return
        token_data = {
            "code": code,
            "client_id": CLIENT_CONFIG["installed"]["client_id"],
            "client_secret": CLIENT_CONFIG["installed"]["client_secret"],
            "redirect_uri": "http://localhost",
            "grant_type": "authorization_code",
        }
        r = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        if r.status_code != 200:
            print(f"Error al intercambiar código. Estado HTTP: {r.status_code}")
            return
        tokens = r.json()
        credenciales = tokens
        refresh_token = tokens.get("refresh_token")
    else:
        refresh_token = credenciales.refresh_token

    if not refresh_token:
        print()
        print("NO SE OBTUVO REFRESH TOKEN.")
        print("Vuelve a intentarlo y asegurate de autorizar completamente.")
        print("El refresh token solo se entrega la PRIMERA vez que autorizas.")
        return

    print()
    print("=" * 60)
    print("TOKENS OBTENIDOS CORRECTAMENTE")
    print("=" * 60)
    print()

    env_path = BASE_DIR / ".env"
    env_content = ""
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            env_content = f.read()

    nuevas_vars = {
        "GOOGLE_CLIENT_ID": CLIENT_CONFIG["installed"]["client_id"],
        "GOOGLE_CLIENT_SECRET": CLIENT_CONFIG["installed"]["client_secret"],
        "GOOGLE_REFRESH_TOKEN": refresh_token,
        "GOOGLE_SENDER_EMAIL": sender_email,
    }

    print("Variables OAuth preparadas para escribir en .env.")
    print()
    if input("Escribir estas variables en .env? (s/n): ").strip().lower() == "s":
        lineas = env_content.splitlines() if env_content else []
        keys_actualizadas = set()

        for i, linea in enumerate(lineas):
            for var in nuevas_vars:
                if linea.startswith(f"{var}="):
                    lineas[i] = f"{var}={nuevas_vars[var]}"
                    keys_actualizadas.add(var)

        for var, valor in nuevas_vars.items():
            if var not in keys_actualizadas:
                lineas.append(f"{var}={valor}")

        # Also ensure COGNITO_ENABLED=false and MODO_DESARROLLO=true or false
        modo_vars = {
            "COGNITO_ENABLED": "false",
        }
        for var, valor in modo_vars.items():
            found = False
            for i, linea in enumerate(lineas):
                if linea.startswith(f"{var}="):
                    found = True
                    break
            if not found:
                lineas.append(f"{var}={valor}")

        with open(env_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lineas) + "\n")

        print()
        print(f"Archivo {env_path} actualizado!")
        print()
        print("AHORA: En frontend/.env agrega:")
        print(f"  VITE_GOOGLE_CLIENT_ID={CLIENT_CONFIG['installed']['client_id']}")
        print()

    print()
    print("LISTO! El envio de correos con Gmail API ya funciona.")
    print("Y los usuarios pueden iniciar sesion con Google.")
    print()


if __name__ == "__main__":
    main()
