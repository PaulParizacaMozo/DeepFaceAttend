import schedule
import time
from datetime import datetime
import requests

# Importar la aplicacion Flask para tener acceso a su contexto
# Usamos 'current_app' para asegurar que estamos trabajando con la instancia correcta
from flask import current_app

def check_schedules_and_notify():
    """
    Esta es la funcion principal que se ejecutara a intervalos regulares.
    Busca las clases programadas para la hora actual y notifica al servidor de asistencia.
    """
    # Usar el contexto de la aplicacion es CRUCIAL para que el planificador pueda
    # acceder a la base de datos y a la configuracion de Flask.
    with current_app.app_context():
        from app.models.schedule import Schedule
        from app.models.course import Course

        now = datetime.now()
        current_day_of_week = now.weekday() + 1  # Lunes=1, ..., Domingo=7
        current_time = now.time()
        
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scheduler running: Checking for classes...")

        # Buscar todos los horarios que coincidan con el día y la hora actual
        schedules_now = Schedule.query.filter(
            Schedule.day_of_week == current_day_of_week,
            Schedule.start_time <= current_time,
            Schedule.end_time >= current_time
        ).all()

        if not schedules_now:
            print("--> No classes scheduled for this exact minute.")
            return

        for schedule_item in schedules_now:
            course = Course.query.get(schedule_item.course_id)
            if course:
                print(f"✅ Class found: '{course.course_name}' is in session. Notifying attendance server...")
                
                # Construir el payload para enviar al otro servidor
                payload = {
                    "course_id": course.id,
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "start_time": schedule_item.start_time.strftime('%H:%M'),
                    "end_time": schedule_item.end_time.strftime('%H:%M'),
                    "location": schedule_item.location,
                    "notification_time": now.isoformat()
                }

                # Enviar la peticion POST al servidor de asistencia
                try:
                    response = requests.post("http://localhost:4000/take-attendance", json=payload, timeout=10)
                    if response.status_code == 200:
                        print(f"--> Successfully notified server for course {course.course_code}. Response: {response.json()}")
                    else:
                        print(f"--> Error notifying server for course {course.course_code}. Status: {response.status_code}, Response: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"--> CRITICAL: Could not connect to attendance server at localhost:4000. Error: {e}")

def run_scheduler(app):
    """
    Configura y ejecuta el bucle del planificador.
    """
    # Pasar la instancia de la app es necesario para que el hilo tenga el contexto correcto.
    with app.app_context():
        # Programar la tarea para que se ejecute cada minuto.
        # Puedes ajustarlo a 'every(5).minutes', 'every().hour', etc.
        schedule.every(1).minutes.do(check_schedules_and_notify)

        print("Scheduler started. Waiting for scheduled jobs...")
        while True:
            schedule.run_pending()
            time.sleep(1)