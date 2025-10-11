import uuid
from app import db
from app.models.enrollment import Enrollment

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cui = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    filepath_embeddings = db.Column(db.String(255), nullable=False)

    # Relaciones
    enrollments = db.relationship('Enrollment', back_populates='student', cascade="all, delete-orphan")
    attendances = db.relationship('Attendance', back_populates='student', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.cui} {self.first_name}>"
