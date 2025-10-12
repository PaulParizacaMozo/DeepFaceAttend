from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.schemas.student_schema import student_schema, students_schema

students_bp = Blueprint('students_bp', __name__, url_prefix='/students')

@students_bp.route('/', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = student_schema.load(data, session=db.session)
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
    data = request.get_json()
    if 'cui' in data:
        student.cui = data['cui']
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'filepath_embeddings' in data:
        student.filepath_embeddings = data['filepath_embeddings']
    db.session.commit()
    return student_schema.jsonify(student), 200
