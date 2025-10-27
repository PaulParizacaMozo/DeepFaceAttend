import uuid
from app import db
from app.models.schedule import Schedule
from app.models.attendance import Attendance

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    semester = db.Column(db.String(20), nullable=True)

    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=True)
    teacher = db.relationship('Teacher', back_populates='courses')

    # Relaciones
    schedules = db.relationship('Schedule', back_populates='course', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")
    attendances = db.relationship('Attendance', back_populates='course', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.course_code} {self.course_name}>"
