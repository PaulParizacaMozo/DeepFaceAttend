# app/models/teacher.py
import uuid
from app import db

class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    # Clave foránea para la relación uno a uno con User
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Relacion de vuelta a User
    user = db.relationship('User', back_populates='teacher')

    # Puedes agregar relaciones con cursos que dicta, etc.
    courses = db.relationship('Course', back_populates='teacher')

    def __repr__(self):
        return f"<Teacher {self.first_name} {self.last_name}>"