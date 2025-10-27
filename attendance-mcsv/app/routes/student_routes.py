# app/routes/student_routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.schemas.student_schema import student_schema, students_schema
from app.services.student_service import call_embedding_service

students_bp = Blueprint('students_bp', __name__, url_prefix='/students')

@students_bp.route('/', methods=['POST'], strict_slashes=False)
def add_student():
    cui = request.form.get('cui')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    if not all([cui, first_name, last_name]):
        return jsonify({"error": "Fields 'cui', 'first_name', and 'last_name' are required."}), 400

    filepath = ""

    new_student = Student(
        cui=cui,
        first_name=first_name,
        last_name=last_name,
        filepath_embeddings=filepath
    )

    db.session.add(new_student)
    db.session.commit()

    return student_schema.jsonify(new_student), 201

@students_bp.route('/', methods=['GET'])
def get_students():
    all_students = Student.query.all()
    return students_schema.jsonify(all_students), 200

@students_bp.route('/<string:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)

    if 'cui' in request.form:
        student.cui = request.form['cui']
    if 'first_name' in request.form:
        student.first_name = request.form['first_name']
    if 'last_name' in request.form:
        student.last_name = request.form['last_name']

    student.filepath_embeddings = ""  # se mantiene vacío

    db.session.commit()
    return student_schema.jsonify(student), 200
