# backend/app/routes/enrollment_routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.enrollment import Enrollment
from app.schemas.enrollment_schema import enrollment_schema, enrollments_schema
from app.services.enrollment_service import assign_to_course

enrollments_bp = Blueprint('enrollments_bp', __name__, url_prefix='/enrollments')

@enrollments_bp.route('/', methods=['POST'])
def add_enrollment():
    data = request.get_json()
    # Asegúrate de que tanto student_id como course_id existan antes de matricular
    if not data:
        return jsonify({"error": "JSON body is required."}), 400
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    
    if not student_id or not course_id:
        return jsonify({"error": "Both 'student_id' and 'course_id' are required."}), 400
    
    success = assign_to_course(student_id, course_id)
    if not success:
        return jsonify({
            "status": "failed",
            "message": f"Failed to assign student {student_id} to course {course_id} (CSV update failed)."
        }), 400
    
    try:
        new_enrollment = enrollment_schema.load(data, session=db.session)
        db.session.add(new_enrollment)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Student {student_id} enrolled in course {course_id} successfully.",
            "enrollment": enrollment_schema.dump(new_enrollment)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Database error: {str(e)}"
        }), 500

@enrollments_bp.route('/', methods=['GET'])
def get_enrollments():
    all_enrollments = Enrollment.query.all()
    return enrollments_schema.jsonify(all_enrollments), 200
