from flask import Blueprint, request, jsonify
from app import db
from app.models.unknown_face import UnknownFace
from app.models.schedule import Schedule
from app.schemas.unknown_face_schema import unknown_face_schema
from datetime import datetime

unknown_face_bp = Blueprint('unknown_face_bp', __name__, url_prefix='/unknown-faces')

@unknown_face_bp.route('', methods=['POST'])
def create_unknown_face():
    data = request.get_json() or {}

    schedule_id = data.get('schedule_id')
    embedding = data.get('embedding')
    image_path = data.get('image_path')
    detected_at_str = data.get('detected_at')

    # Validaciones mínimas
    if not schedule_id or not embedding or not image_path:
        return jsonify({"error": "Fields 'schedule_id', 'embedding' and 'image_path' are required."}), 400

    # Verificar que el schedule existe
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": f"Schedule with id {schedule_id} not found."}), 404

    # Parsear detected_at si viene, sino usar ahora
    if detected_at_str:
        try:
            detected_at = datetime.fromisoformat(detected_at_str)
        except ValueError:
            return jsonify({"error": "Invalid 'detected_at' format. Use ISO 8601."}), 400
    else:
        detected_at = datetime.utcnow()

    unknown_face = UnknownFace(
        schedule_id=schedule_id,
        embedding=embedding,
        image_path=image_path,
        detected_at=detected_at
    )

    db.session.add(unknown_face)
    db.session.commit()

    return unknown_face_schema.jsonify(unknown_face), 201
