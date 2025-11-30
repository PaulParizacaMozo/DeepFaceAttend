from flask import Blueprint, request, jsonify, current_app
from ..services.embedding_service import generate_student_embedding, assign_student_to_course, get_student_embedding_from_csv
import cv2
import numpy as np
from .. import config

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
    
    
# Falta probar este endpoint
# ==========================================================
# Endpoint 3: Extraer embedding (Helper para otros servicios)
# ==========================================================
@processing_bp.route('/extract-embedding', methods=['POST'])
def extract_embedding_endpoint():
    """
    Recibe una imagen y devuelve su embedding (vector) en formato JSON.
    No guarda nada en disco ni base de datos.
    """
    face_model = current_app.face_model

    if 'image' not in request.files:
        return jsonify({"error": "No image provided."}), 400

    file = request.files['image']
    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Could not decode image."}), 400

    faces = face_model.get(frame)
    
    # Buscar la cara con mejor score y tamaño
    if not faces:
        return jsonify({"error": "No face detected."}), 400

    best_face = max(faces, key=lambda face: face.det_score)
    
    if best_face.det_score < config.DETECTION_THRESHOLD:
        return jsonify({"error": "Face detection score too low."}), 400

    # Convertir ndarray a lista para JSON
    embedding_list = best_face.embedding.tolist()

    return jsonify({
        "status": "success",
        "embedding": embedding_list
    }), 200

# ==========================================================
# Endpoint 4: Obtener embedding guardado de un estudiante
# ==========================================================
@processing_bp.route('/student-embedding/<student_id>', methods=['GET'])
def get_student_embedding_endpoint(student_id):
    """
    Devuelve el embedding guardado en students.csv para el student_id dado.
    Si no existe, responde 404.
    """
    embedding = get_student_embedding_from_csv(student_id)
    if embedding is None:
        return jsonify({
            "status": "error",
            "message": f"Embedding not found for student_id '{student_id}'."
        }), 404

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "embedding": embedding.tolist()  # JSON serializable
    }), 200
