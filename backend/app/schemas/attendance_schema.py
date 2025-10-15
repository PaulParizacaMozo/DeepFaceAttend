from app import ma
from app.models.attendance import Attendance

class AttendanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attendance
        load_instance = True
        include_fk = True

attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)
