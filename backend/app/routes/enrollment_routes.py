from flask import Blueprint, request, jsonify
from app import db
from app.models.enrollment import Enrollment
from app.schemas.enrollment_schema import enrollment_schema, enrollments_schema

enrollments_bp = Blueprint('enrollments_bp', __name__, url_prefix='/enrollments')

@enrollments_bp.route('/', methods=['POST'])
def add_enrollment():
    data = request.get_json()
    # Asegúrate de que tanto student_id como course_id existan antes de matricular
    new_enrollment = enrollment_schema.load(data, session=db.session)
    db.session.add(new_enrollment)
    db.session.commit()
    return enrollment_schema.jsonify(new_enrollment), 201

@enrollments_bp.route('/', methods=['GET'])
def get_enrollments():
    all_enrollments = Enrollment.query.all()
    return enrollments_schema.jsonify(all_enrollments), 200
