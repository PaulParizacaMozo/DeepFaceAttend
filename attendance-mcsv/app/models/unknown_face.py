from app import db
from datetime import datetime

class UnknownFace(db.Model):
    __tablename__ = 'unknown_faces'

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.String(36), db.ForeignKey('schedules.id'), nullable=False)

    # Embedding serializado como string "v1;v2;...;v512"
    embedding = db.Column(db.Text, nullable=False)

    # Ruta absoluta o relativa en el microservicio de facedetection
    image_path = db.Column(db.String(512), nullable=False)

    # Momento en que se capturó la cara
    detected_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Para el futuro: cuando asocies este unknown a un estudiante real
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    resolved = db.Column(db.Boolean, nullable=False, default=False)

    # Relaciones opcionales (si quieres navegarlas)
    schedule = db.relationship('Schedule', backref='unknown_faces', lazy=True)
    student = db.relationship('Student', backref='unknown_faces', lazy=True)

