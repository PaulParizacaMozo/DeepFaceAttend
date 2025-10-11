from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance
from app.schemas.attendance_schema import attendance_schema, attendances_schema
from datetime import datetime

attendance_bp = Blueprint('attendance_bp', __name__, url_prefix='/attendance')

@attendance_bp.route('/', methods=['POST'])
def add_attendance_record():
    data = request.get_json()
    new_record = attendance_schema.load(data, session=db.session)
    db.session.add(new_record)
    db.session.commit()
    return attendance_schema.jsonify(new_record), 201

@attendance_bp.route('/', methods=['GET'])
def get_attendance():
    # Permite filtrar por curso y/o fecha. Ej: /attendance?course_id=...&date=YYYY-MM-DD
    course_id = request.args.get('course_id')
    date_str = request.args.get('date')
    
    query = Attendance.query

    if course_id:
        query = query.filter_by(course_id=course_id)
    if date_str:
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(attendance_date=attendance_date)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}), 400

    records = query.all()
    return attendances_schema.jsonify(records), 200
