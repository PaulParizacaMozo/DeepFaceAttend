import uuid
from app import db
import datetime

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    # Status puede ser: 'presente', 'tarde', 'ausente'
    status = db.Column(db.String(10), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Relaciones
    student = db.relationship('Student', back_populates='attendances')
    course = db.relationship('Course', back_populates='attendances')
