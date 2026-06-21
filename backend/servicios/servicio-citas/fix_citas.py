from app import create_app, db
from app.modelos.cita import Cita
from datetime import timedelta

app = create_app()
with app.app_context():
    citas = Cita.query.all()
    for cita in citas:
        # Prevent fixing twice
        if cita.fecha_hora_inicio.hour >= 13:
            cita.fecha_hora_inicio -= timedelta(hours=5)
            cita.fecha_hora_fin -= timedelta(hours=5)
    db.session.commit()
    print("Citas arregladas")
