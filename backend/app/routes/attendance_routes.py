from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance
from app.schemas.attendance_schema import attendance_schema, attendances_schema
from datetime import datetime

attendance_bp = Blueprint('attendance_bp', __name__, url_prefix='/attendance')

@attendance_bp.route('/', methods=['POST'])
def add_attendance_record():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['student_id', 'course_id', 'status']):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    new_record = attendance_schema.load(data, session=db.session)
    db.session.add(new_record)
    db.session.commit()
    return attendance_schema.jsonify(new_record), 201

@attendance_bp.route('/search', methods=['POST'])
def search_attendance():
    """
    BUSCA registros de asistencia usando filtros en un cuerpo JSON.
    Recibe: JSON con filtros opcionales como course_id y/o date.
    """
    data = request.get_json()
    
    # Si no se envía un cuerpo JSON, devuelve un error.
    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON con los filtros"}), 400

    # Extraer filtros del cuerpo JSON
    course_id = data.get('course_id')
    date_str = data.get('date')

    query = Attendance.query

    if course_id:
        query = query.filter_by(course_id=course_id)
    
    if date_str:
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(attendance_date=attendance_date)
        except (ValueError, TypeError):
            return jsonify({"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}), 400

    records = query.all()
    print(f"--> {len(records)} registros encontrados con los filtros.")
    return attendances_schema.jsonify(records), 200