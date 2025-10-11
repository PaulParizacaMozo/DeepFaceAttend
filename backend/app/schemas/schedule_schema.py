from app import ma
from app.models.schedule import Schedule

class ScheduleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Schedule
        load_instance = True
        include_fk = True

schedule_schema = ScheduleSchema()
schedules_schema = ScheduleSchema(many=True)
