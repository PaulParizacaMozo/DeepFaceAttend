from app import ma
from app.models.student import Student

class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True
        include_fk = True

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
