import schedule
import time
from datetime import datetime
import requests

from flask import current_app
from sqlalchemy import extract

def check_schedules_and_notify():
    """
    Se ejecuta cada minuto para buscar clases que COMIENZAN en ese preciso instante
    y notifica al servicio de captura de asistencia.
    """
    with current_app.app_context():
        from app.models.schedule import Schedule

        now = datetime.now()
        current_day_of_week = now.weekday() + 1  # Lunes=1, ..., Domingo=7
        
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scheduler running: Checking for classes starting now...")

        schedules_starting_now = Schedule.query.filter(
            Schedule.day_of_week == current_day_of_week,
            extract('hour', Schedule.start_time) == now.hour,
            extract('minute', Schedule.start_time) == now.minute
        ).all()

        if not schedules_starting_now:
            print("--> No classes scheduled to start this minute.")
            return

        for schedule_item in schedules_starting_now:
            print(f"✅ Class starting: Schedule ID {schedule_item.id}. Notifying attendance service...")
            
            # --- PAYLOAD Y ENDPOINT ACTUALIZADOS ---
            # El payload ahora solo contiene el ID del horario (schedule).
            payload = {
                "scheduler_id": schedule_item.id
            }
            
            # La URL del endpoint de destino.
            target_url = "http://127.0.0.1:4000/start_attendance_capture"

            try:
                response = requests.post(target_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    print(f"--> Successfully notified for schedule {schedule_item.id}. Response: {response.json()}")
                else:
                    print(f"--> Error notifying for schedule {schedule_item.id}. Status: {response.status_code}, Response: {response.text}")
            
            except requests.exceptions.RequestException as e:
                print(f"--> CRITICAL: Could not connect to attendance service at {target_url}. Error: {e}")

def run_scheduler(app):
    """
    Configura y ejecuta el bucle del planificador (sin cambios).
    """
    with app.app_context():
        # Programar la tarea para que se ejecute cada minuto.
        schedule.every(1).minutes.do(check_schedules_and_notify)

        print("Scheduler started. Waiting for scheduled jobs...")
        while True:
            schedule.run_pending()
            time.sleep(1)
