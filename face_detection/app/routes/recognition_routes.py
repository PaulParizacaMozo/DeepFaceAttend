from flask import Blueprint, request, jsonify, current_app
from ..services.recognition_service import recognize_faces_in_frame
import cv2
import numpy as np

recognition_bp = Blueprint('recognition_bp', __name__)

@recognition_bp.route('/process_frame', methods=['POST'])
def process_frame():
    face_model = current_app.face_model
    known_db = current_app.known_db

    if 'image' not in request.files:
        return jsonify({"error": "Image file not found in the request."}), 400
    
    file = request.files['image']
    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Could not decode image."}), 400
    
    results = recognize_faces_in_frame(frame, face_model, known_db)
    
    return jsonify({"recognized_faces": results})