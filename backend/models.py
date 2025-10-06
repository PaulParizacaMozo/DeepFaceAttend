import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cui = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    filepath_embeddings = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"
