from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance
from app.models.schedule import Schedule
from app.models.student import Student
from app.schemas.attendance_schema import attendance_schema, attendances_schema
from datetime import date, datetime

attendance_bp = Blueprint('attendance_bp', __name__, url_prefix='/attendance')

@attendance_bp.route('/', methods=['POST'])
def add_attendance_record():
    """
    Registra asistencia recibiendo student_id y schedule_id.
    Busca el course_id a través del schedule y crea el registro.
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['student_id', 'schedule_id']):
        return jsonify({"error": "Faltan los campos 'student_id' y 'schedule_id'"}), 400

    student_id = data.get('student_id')
    schedule_id = data.get('schedule_id')

    # Validar que el estudiante y el horario existan
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Estudiante (student_id) no encontrado"}), 404
        
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario (schedule_id) no encontrado"}), 404

    course_id = schedule.course_id

    # Evitar registros duplicados para el mismo estudiante, curso y día
    today = date.today()
    existing_attendance = Attendance.query.filter_by(
        student_id=student_id,
        course_id=course_id,
        attendance_date=today
    ).first()

    if existing_attendance:
        return jsonify({
            "message": "La asistencia para este estudiante en este curso ya fue registrada hoy.",
            "attendance": attendance_schema.dump(existing_attendance)
        }), 409 # Conflict

    # Crear el nuevo registro con estado 'presente'
    new_record_data = {
        "student_id": student_id,
        "course_id": course_id,
        "status": "presente"
    }

    new_record = attendance_schema.load(new_record_data, session=db.session)
    
    db.session.add(new_record)
    db.session.commit()
    
    return attendance_schema.jsonify(new_record), 201

@attendance_bp.route('/manual', methods=['POST'])
def add_manual_attendance_record():
    """
    Registra asistencia manualmente recibiendo student_id, schedule_id, fecha (YYYY-MM-DD) y hora (HH:MM:SS).
    """
    data = request.get_json()
    
    required_fields = ['student_id', 'schedule_id', 'date', 'time']
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": f"Faltan campos requeridos: {required_fields}"}), 400

    student_id = data.get('student_id')
    schedule_id = data.get('schedule_id')
    date_str = data.get('date') # Formato esperado: "2025-09-02"
    time_str = data.get('time') # Formato esperado: "14:30:00"

    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Estudiante (student_id) no encontrado"}), 404
        
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Horario (schedule_id) no encontrado"}), 404

    course_id = schedule.course_id

    try:
        attendance_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        full_datetime_str = f"{date_str} {time_str}"
        check_in_time_obj = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Formato inválido. Use 'YYYY-MM-DD' para fecha y 'HH:MM:SS' para hora."}), 400

    existing_attendance = Attendance.query.filter_by(
        student_id=student_id,
        course_id=course_id,
        attendance_date=attendance_date_obj
    ).first()

    if existing_attendance:
        return jsonify({
            "message": "La asistencia para este estudiante en este curso ya existe en la fecha indicada.",
            "attendance": attendance_schema.dump(existing_attendance)
        }), 409  
    new_record = Attendance(
        student_id=student_id,
        course_id=course_id,
        attendance_date=attendance_date_obj,   
        check_in_time=check_in_time_obj,       
        status="presente"                     
    )
    
    db.session.add(new_record)
    db.session.commit()
    
    return attendance_schema.jsonify(new_record), 201


@attendance_bp.route('/search', methods=['POST'])
def search_attendance():
    """
    Busca registros de asistencia usando filtros opcionales en un cuerpo JSON.
    Puede filtrar por: course_id, schedule_id, y/o date.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON con los filtros"}), 400

    course_id = data.get('course_id')
    schedule_id = data.get('schedule_id')
    date_str = data.get('date')

    query = Attendance.query

    # Si se provee un schedule_id, este tiene prioridad para obtener el course_id
    if schedule_id:
        schedule = Schedule.query.get(schedule_id)
        if schedule:
            query = query.filter_by(course_id=schedule.course_id)
        else:
            return jsonify([]), 200 # Devuelve lista vacía si el schedule no existe
            
    elif course_id:
        query = query.filter_by(course_id=course_id)
    
    if date_str:
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(attendance_date=attendance_date)
        except (ValueError, TypeError):
            return jsonify({"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}), 400

    records = query.all()
    
    # Este print es útil para depurar en la consola del servidor
    print(f"Registros encontrados en la BD: {records}")
    
    return attendances_schema.jsonify(records), 200



@attendance_bp.route('/batch', methods=['POST'])
def batch_update_attendance():
    """
    Permite crear o actualizar múltiples registros de asistencia a la vez.
    Espera un JSON: { "records": [ { "student_id": "...", "course_id": "...", "attendance_date": "YYYY-MM-DD", "status": "..." } ] }
    """
    try:
        data = request.get_json()
        records = data.get('records', [])

        if not records:
            return jsonify({"message": "No se proporcionaron registros"}), 400

        processed_count = 0

        for item in records:
            student_id = item.get('student_id')
            course_id = item.get('course_id')
            date_str = item.get('attendance_date')
            status = item.get('status')

            # Validar campos básicos
            if not all([student_id, course_id, date_str, status]):
                continue

            # Convertir fecha string (YYYY-MM-DD) a objeto date de Python
            try:
                attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                # Si la fecha viene mal formateada, saltamos este registro
                continue

            # Buscar si ya existe un registro para este estudiante, curso y fecha
            existing_record = Attendance.query.filter_by(
                student_id=student_id,
                course_id=course_id,
                attendance_date=attendance_date
            ).first()

            if existing_record:
                # UPDATE: Si existe, actualizamos el estado
                existing_record.status = status
                # Opcional: Actualizar la hora de modificación si lo deseas
                # existing_record.check_in_time = datetime.now()
            else:
                # INSERT: Si no existe, creamos uno nuevo
                new_record = Attendance(
                    student_id=student_id,
                    course_id=course_id,
                    attendance_date=attendance_date,
                    status=status,
                    check_in_time=datetime.now() # Hora actual del servidor como marca de tiempo
                )
                db.session.add(new_record)
            
            processed_count += 1

        # Guardar todos los cambios en una sola transacción
        db.session.commit()

        return jsonify({
            "message": "Asistencia actualizada correctamente",
            "processed_records": processed_count
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en batch update: {e}")
        return jsonify({"message": "Error interno al procesar la asistencia"}), 500
