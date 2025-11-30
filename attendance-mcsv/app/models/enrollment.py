from app import db
from app.models.course import Course

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), primary_key=True)

    # Relaciones
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
