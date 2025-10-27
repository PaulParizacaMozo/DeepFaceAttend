from flask import Blueprint, request, jsonify, current_app
from ..services.recognition_service import recognize_faces_in_frame_2, capture_and_recognize_faces
import cv2
import sqlite3
import numpy as np
import threading
from .. import config
from app.services import database_service
recognition_bp = Blueprint('recognition_bp', __name__)

@recognition_bp.route('/process_frame', methods=['POST'])
def process_frame():
    schedule_id = request.form.get('schedule_id')
    if 'image' not in request.files:
        return jsonify({"error": "Image file not found in the request."}), 400
    file = request.files['image']
    face_model = current_app.face_model
    known_matrix = None
    known_labels = None
    if schedule_id:
        conn = None
        course_id = None
        try:
            conn = sqlite3.connect(config.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT course_id FROM schedules WHERE id = ?", (schedule_id,))
            result = cursor.fetchone()
            if result is None:
                print(f"[ERROR] schedule_id '{schedule_id}' no encontrado en la base de datos.")
                return jsonify({"error": f"Invalid schedule_id: {schedule_id}"}), 404
            course_id = result[0]
            print(f"[INFO] schedule_id '{schedule_id}' corresponde al course_id '{course_id}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Error de base de datos: {e}")
            return jsonify({"error": "Fallo al consultar la base de datos."}), 500
        finally:
            if conn:
                conn.close()
        course_db = database_service.load_known_faces_from_csv(course_id)
        if not course_db:
            return jsonify({"error": f"No known faces found for course_id: {course_id}"}), 404
        course_matrix, course_labels = database_service.prepare_vectorized_db(course_db)
        known_labels = course_labels
        known_matrix = course_matrix
    else:
        known_matrix = current_app.known_matrix
        known_labels = current_app.known_labels

    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Could not decode image."}), 400
    results = recognize_faces_in_frame_2(frame, face_model, known_matrix, known_labels)
    return jsonify({"recognized_faces": results})


@recognition_bp.route('/start_attendance_capture', methods=['POST'])
def start_attendance_capture():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required."}), 400

    scheduler_id = data.get('scheduler_id')

    if not scheduler_id:
        return jsonify({"error": "Fields 'scheduler_id' is required."}), 400

    thread = threading.Thread(
        target=capture_and_recognize_faces,
        args=(scheduler_id,),
        daemon=True
    )
    thread.start()

    return jsonify({
        "status": "started",
        "message": f"Attendance capture started for course {scheduler_id}"
    }), 200