from app import create_app, db
from app.modelos.disponibilidad import Disponibilidad
from app.modelos.cita import Cita
from sqlalchemy import text
from datetime import datetime, timedelta, time

import os

def obtener_ids_demo():
    # Obtener IDs de la tabla users
    tabla_users = "usuarios_schema.usuarios" if os.getenv("DB_SCHEMA") else "usuarios"
    with db.engine.connect() as conn:
        result_psicologo = conn.execute(text(f"SELECT id FROM {tabla_users} WHERE email = 'psicologo@psicoconecta.com'")).first()
        result_paciente = conn.execute(text(f"SELECT id FROM {tabla_users} WHERE email = 'paciente@psicoconecta.com'")).first()
        
    return (result_psicologo[0] if result_psicologo else None, 
            result_paciente[0] if result_paciente else None)

def seed_database():
    db.create_all()
    psicologo_id, paciente_id = obtener_ids_demo()
    
    if not psicologo_id or not paciente_id:
        print("No se encontraron usuarios demo en usuarios_schema. Ejecute primero el seed de usuarios.")
        return

    # Verificar si ya hay disponibilidad
    if not Disponibilidad.query.filter_by(psicologo_id=psicologo_id).first():
        # Lunes a Viernes: bloque mañana 08:00-12:00 y bloque tarde 14:00-17:00
        for dia in range(5):
            # Bloque mañana
            db.session.add(Disponibilidad(
                psicologo_id=psicologo_id,
                dia_semana=dia,
                hora_inicio=time(8, 0),
                hora_fin=time(12, 0),
                duracion_slot=60
            ))
            # Bloque tarde
            db.session.add(Disponibilidad(
                psicologo_id=psicologo_id,
                dia_semana=dia,
                hora_inicio=time(14, 0),
                hora_fin=time(17, 0),
                duracion_slot=60
            ))
        db.session.commit()
        print("Disponibilidad demo creada (L-V, 08-12 y 14-17, slots de 60 min).")

    # Verificar si ya hay citas
    if not Cita.query.filter_by(psicologo_id=psicologo_id).first():
        # Crear una cita mañana
        manana = datetime.now() + timedelta(days=1)
        if manana.weekday() > 4: # Si es fin de semana, pasar a lunes
            manana = manana + timedelta(days=7 - manana.weekday())
            
        hora_cita_inicio = manana.replace(hour=10, minute=0, second=0, microsecond=0)
        hora_cita_fin = manana.replace(hour=11, minute=0, second=0, microsecond=0)
        
        db.session.add(Cita(
            paciente_id=paciente_id,
            psicologo_id=psicologo_id,
            fecha_hora_inicio=hora_cita_inicio,
            fecha_hora_fin=hora_cita_fin,
            estado='CONFIRMADA',
            modalidad='VIRTUAL',
            motivo_consulta='Ansiedad generalizada'
        ))
        db.session.commit()
        print("Cita demo creada (10:00-11:00).")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database()
