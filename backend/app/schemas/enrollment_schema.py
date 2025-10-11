from app import ma
from app.models.enrollment import Enrollment

class EnrollmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Enrollment
        load_instance = True
        include_fk = True

enrollment_schema = EnrollmentSchema()
enrollments_schema = EnrollmentSchema(many=True)
