import uuid
from app import db

class Schedule(db.Model):
    __tablename__ = "schedules"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False) # 1=Lunes, 7=Domingo
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=True)

    # Relaciones
    course = db.relationship('Course', back_populates='schedules')
