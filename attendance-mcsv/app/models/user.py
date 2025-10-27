# app/models/user.py
import uuid
import enum 
from app import db
from .teacher import Teacher
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class UserRole(enum.Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False) # Quitamos el default para forzar la elección

    # Relaciones uno a uno. Si se borra un User, se borra su perfil asociado.
    student = db.relationship('Student', back_populates='user', uselist=False, cascade="all, delete-orphan")
    teacher = db.relationship('Teacher', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email} - {self.role.value}>'