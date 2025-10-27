from flask import Blueprint, request, jsonify, current_app
from ..services.embedding_service import generate_student_embedding, assign_student_to_course

processing_bp = Blueprint('processing_bp', __name__)

# ==========================================================
# Endpoint 1: Generar embedding promedio del estudiante
# ==========================================================
@processing_bp.route('/generate-embedding', methods=['POST'])
def generate_embedding_endpoint():
    face_model = current_app.face_model

    if 'student_id' not in request.form:
        return jsonify({"error": "Field 'student_id' is required."}), 400
    
    student_id = request.form['student_id']
    images = request.files.getlist('images')

    if not images:
        return jsonify({"error": "No images provided in the 'images' field."}), 400

    success = generate_student_embedding(images, student_id, face_model)

    if success:
        return jsonify({
            "status": "success",
            "message": f"Embedding for student '{student_id}' saved/updated successfully."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Could not extract any high-quality embeddings from the provided images."
        }), 400

# ==========================================================
# Endpoint 2: Asignar estudiante a un curso
# ==========================================================
@processing_bp.route('/assign-to-course', methods=['POST'])
def assign_to_course_endpoint():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required."}), 400

    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not student_id or not course_id:
        return jsonify({"error": "Fields 'student_id' and 'course_id' are required."}), 400

    success = assign_student_to_course(student_id, course_id)

    if success:
        return jsonify({
            "status": "success",
            "message": f"Student '{student_id}' assigned to course '{course_id}' successfully."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"Failed to assign student '{student_id}' to course '{course_id}'."
        }), 400