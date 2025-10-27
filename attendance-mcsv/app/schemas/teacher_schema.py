# app/schemas/teacher_schema.py
from app.models.teacher import Teacher
from app import ma
class TeacherSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Teacher
        load_instance = True


teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)