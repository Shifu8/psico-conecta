import time
from datetime import timedelta, time as hora

from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from app import create_app, db
from app.modelos.cita import Cita
from app.modelos.disponibilidad import Disponibilidad
from app.servicios.servicio_cita import ServicioCita
from app.utilidades.tiempo import ahora_utc, a_hora_local, combinar_fecha_hora_local


HORARIOS_BASE = (
    (hora(8, 0), hora(12, 0), 50),
    (hora(14, 0), hora(17, 0), 50),
)


def obtener_usuarios_demo_y_psicologos():
    consulta = text(
        """
        SELECT u.id, u.email, r.name AS rol
        FROM usuarios_schema.usuarios u
        JOIN usuarios_schema.roles r ON r.id = u.role_id
        WHERE u.status = 'active'
          AND (r.name = 'PSYCHOLOGIST' OR u.email = 'paciente@psicoconecta.com')
        ORDER BY u.id
        """
    )
    filas = db.session.execute(consulta).all()
    psicologos = [fila.id for fila in filas if fila.rol == "PSYCHOLOGIST"]
    paciente_demo = next(
        (fila.id for fila in filas if fila.email == "paciente@psicoconecta.com"),
        None,
    )
    return psicologos, paciente_demo


def esperar_usuarios(intentos=30):
    for _ in range(intentos):
        try:
            psicologos, paciente_demo = obtener_usuarios_demo_y_psicologos()
            if psicologos:
                return psicologos, paciente_demo
        except Exception:
            db.session.rollback()
        time.sleep(1)
    return [], None


def asegurar_horarios_base(psicologo_id):
    if Disponibilidad.query.filter_by(psicologo_id=psicologo_id).first():
        return False

    for dia in range(5):
        for inicio, fin, duracion in HORARIOS_BASE:
            db.session.add(
                Disponibilidad(
                    psicologo_id=psicologo_id,
                    dia_semana=dia,
                    hora_inicio=inicio,
                    hora_fin=fin,
                    duracion_slot=duracion,
                    activo=True,
                )
            )
    return True


def crear_cita_demo(psicologo_id, paciente_id):
    if not paciente_id or Cita.query.filter_by(psicologo_id=psicologo_id).first():
        return False

    fecha_local = a_hora_local(ahora_utc()).date() + timedelta(days=1)
    while fecha_local.weekday() > 4:
        fecha_local += timedelta(days=1)
    inicio_local = combinar_fecha_hora_local(fecha_local, hora(9, 40))
    fin_local = combinar_fecha_hora_local(fecha_local, hora(10, 30))
    cita = Cita(
        paciente_id=paciente_id,
        psicologo_id=psicologo_id,
        fecha_hora_inicio=inicio_local.astimezone(ahora_utc().tzinfo),
        fecha_hora_fin=fin_local.astimezone(ahora_utc().tzinfo),
        estado="CONFIRMADA",
        modalidad="VIRTUAL",
        motivo_consulta="Cita demostrativa",
    )
    db.session.add(cita)
    db.session.flush()
    ServicioCita.registrar_historial(
        cita,
        "CREACION_DEMO",
        psicologo_id,
        motivo="Dato inicial de demostración",
    )
    return True


def seed_database():
    db.create_all()
    psicologos, paciente_demo = esperar_usuarios()
    if not psicologos:
        print("No se encontraron psicólogos activos; el servicio iniciará sin horarios persistidos.")
        return

    creados = 0
    for psicologo_id in psicologos:
        if asegurar_horarios_base(psicologo_id):
            creados += 1

    # Solo se crea una cita de demostración, para no ocupar horarios de todos.
    crear_cita_demo(psicologos[0], paciente_demo)
    db.session.commit()
    print(f"Horarios base verificados para {len(psicologos)} psicólogo(s); nuevos: {creados}.")


if __name__ == "__main__":
    aplicacion = create_app()
    with aplicacion.app_context():
        seed_database()
