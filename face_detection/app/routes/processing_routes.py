from flask import Blueprint, request, jsonify, current_app
from ..services.embedding_service import process_and_save_embeddings

processing_bp = Blueprint('processing_bp', __name__)

@processing_bp.route('/process-images', methods=['POST'])
def process_images_endpoint():
    face_model = current_app.face_model

    if 'student_id' not in request.form:
        return jsonify({"error": "Field 'student_id' is required."}), 400
    
    student_id = request.form['student_id']
    images = request.files.getlist('images')

    if not images:
        return jsonify({"error": "No images provided in the 'images' field."}), 400

    filepath = process_and_save_embeddings(images, student_id, face_model)

    if filepath:
        return jsonify({
            "status": "success",
            "filepath": filepath,
            "message": f"Embeddings for '{student_id}' saved successfully."
        }), 200
    else:
        return jsonify({
            "error": "Could not extract any high-quality embeddings from the provided images."
        }), 400