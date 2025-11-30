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

    new_student = Student(
        cui=cui,
        first_name=first_name,
        last_name=last_name,
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

    db.session.commit()
    return student_schema.jsonify(student), 200

@students_bp.route('/check-embeddings/<string:user_id>', methods=['GET'])
def check_embeddings_status(user_id):
    """
    Verifica si un usuario (estudiante) ya tiene sus embeddings generados.
    Recibe: user_id (UUID del usuario logueado)
    Retorna: JSON con 'has_embeddings': bool
    """
    # Buscamos al estudiante filtrando por el user_id (relación 1 a 1)
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"error": "No se encontró un perfil de estudiante para este usuario."}), 404
    return jsonify({
        "has_embeddings": student.embeddings
    }), 200
    
@students_bp.route('/upload-embeddings', methods=['POST'])
def upload_student_embeddings():
    """
    Recibe 3 fotos y el user_id para generar embeddings.
    """
    try:
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({"error": "Student profile not found for this user"}), 404
        images = request.files.getlist('images') 
        if not images or len(images) == 0:
            return jsonify({"error": "No images provided"}), 400
        success = call_embedding_service(images, student.id)
        if success:
            return jsonify({"message": "Biometrics processed and updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to process embeddings with the recognition service"}), 500
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

@students_bp.route('/get-id/<string:user_id>', methods=['GET'])
def get_student_id(user_id):
    """
    Obtiene el student_id asociado a un user_id específico.
    """
    try:
        student = Student.query.filter_by(user_id=user_id).first()

        if not student:
            return jsonify({"error": "Student profile not found for this user"}), 404
        return jsonify({
            "student_id": student.id
        }), 200

    except Exception as e:
        print(f"Error fetching student ID: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    