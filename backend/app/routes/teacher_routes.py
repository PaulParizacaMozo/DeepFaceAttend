# app/routes/teacher_routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.teacher import Teacher
from app.schemas.teacher_schema import teacher_schema, teachers_schema

teachers_bp = Blueprint('teachers_bp', __name__, url_prefix='/teachers')

@teachers_bp.route('/', methods=['POST'])
def add_teacher():
    name = request.form.get('name')
    subject = request.form.get('subject')

    if not all([name, subject]):
        return jsonify({"error": "Fields 'name' and 'subject' are required."}), 400

    new_teacher = Teacher(
        name=name,
        subject=subject
    )

    db.session.add(new_teacher)
    db.session.commit()

    return teacher_schema.jsonify(new_teacher), 201

@teachers_bp.route('/', methods=['GET'])
def get_teachers():
    all_teachers = Teacher.query.all()
    return teachers_schema.jsonify(all_teachers), 200

@teachers_bp.route('/<string:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    if 'name' in request.form:
        teacher.name = request.form['name']
    if 'subject' in request.form:
        teacher.subject = request.form['subject']

    db.session.commit()
    return teacher_schema.jsonify(teacher), 200
