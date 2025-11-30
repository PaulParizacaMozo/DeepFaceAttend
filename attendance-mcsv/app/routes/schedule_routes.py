import requests
from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from app.schemas.schedule_schema import schedule_schema, schedules_schema
from app.models.course import Course
from app.models.student import Student
from app.models.user import UserRole
from app.routes.auth_routes import token_required
from datetime import datetime

schedules_bp = Blueprint('schedules_bp', __name__, url_prefix='/schedules')

@schedules_bp.route('/', methods=['POST'])
def add_schedule():
    data = request.get_json()
    course_id = data.get('course_id')
    student_id = data.get('student_id')
    date_str = data.get('date')
    time_str = data.get('time')

    # Validar que el curso y el estudiante existan
    course = Course.query.get(course_id)
    student = Student.query.get(student_id)
    if not course or not student:
        return jsonify({"message": "Course or Student not found"}), 404

    # Convertir fecha y hora de string a objetos datetime
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        return jsonify({"message": "Invalid date or time format"}), 400

    new_schedule = Schedule(course_id=course_id, student_id=student_id, date=date, time=time)
    db.session.add(new_schedule)
    db.session.commit()
    return schedule_schema.jsonify(new_schedule), 201


@schedules_bp.route('/<string:schedule_id>/start-attendance', methods=['POST'])
@token_required
def start_manual_attendance(current_user, schedule_id):
    """
    Permite a un profesor iniciar manualmente la captura de asistencia para un horario específico.
    """
    # 1. Validar que el schedule existe
    schedule_item = Schedule.query.get_or_404(schedule_id)
    course = schedule_item.course

    # 2. Validar que el usuario es un profesor y está asignado a este curso
    if current_user.role != UserRole.TEACHER:
        return jsonify({"error": "Solo los profesores pueden iniciar la asistencia."}), 403

    if not current_user.teacher or course.teacher_id != current_user.teacher.id:
        return jsonify({"error": "No estás autorizado para iniciar la asistencia de este curso."}), 403

    # (Opcional pero recomendado) Validar que la clase esté realmente en sesión
    now = datetime.now()
    current_day_of_week = now.weekday() + 1
    current_time = now.time()

    if not (schedule_item.day_of_week == current_day_of_week and 
            schedule_item.start_time <= current_time and 
            schedule_item.end_time >= current_time):
        return jsonify({"message": "Esta clase no está en sesión en este momento."}), 400

    # 3. Construir el payload y enviarlo al servicio de la cámara
    payload = {
        "scheduler_id": schedule_item.id
    }
    target_url = "http://localhost:4000/start_attendance_capture"

    try:
        response = requests.post(target_url, json=payload, timeout=10)
        response.raise_for_status() # Lanza error si el status no es 2xx

        print(f"Notificación manual enviada para schedule {schedule_item.id}. Respuesta: {response.json()}")
        return jsonify({
            "status": "success",
            "message": f"Se inició la captura de asistencia para '{course.course_name}'.",
            "details": response.json()
        }), 200
    except requests.exceptions.RequestException as e:
        print(f"CRITICAL: No se pudo conectar con el servicio de asistencia en {target_url}. Error: {e}")
        return jsonify({"error": "No se pudo conectar con el servicio de la cámara."}), 503
    
@schedules_bp.route('/<string:schedule_id>/course', methods=['GET'])
def get_course_by_schedule(schedule_id):
    """
    Devuelve la info del curso asociado a un schedule dado.

    GET /schedules/<schedule_id>/course

    Respuesta:
    {
      "course_id": "...",
      "course_code": "...",
      "course_name": "...",
      "semester": "..."
    }
    """
    # 1. Buscar el schedule
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": f"Schedule '{schedule_id}' not found."}), 404

    # 2. Usar la relación hacia Course
    course = schedule.course
    if not course:
        return jsonify({"error": f"No course associated to schedule '{schedule_id}'."}), 404

    # 3. Devolver solo lo que necesitas para el front
    return jsonify({
        "course_id": course.id,
        "course_code": course.course_code,
        "course_name": course.course_name,
        "semester": course.semester
    }), 200
