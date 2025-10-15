from app import ma
from app.models.course import Course
from .schedule_schema import ScheduleSchema

class CourseSchema(ma.SQLAlchemyAutoSchema):
    schedules = ma.Nested(ScheduleSchema, many=True)
    class Meta:
        model = Course
        load_instance = True
        include_fk = True

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
