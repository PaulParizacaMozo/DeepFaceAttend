from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from app.schemas.schedule_schema import schedule_schema, schedules_schema
from app.models.course import Course
from app.models.student import Student
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