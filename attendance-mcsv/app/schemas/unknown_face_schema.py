from app import ma
from app.models.unknown_face import UnknownFace

class UnknownFaceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UnknownFace
        load_instance = True
        include_fk = True

unknown_face_schema = UnknownFaceSchema()
unknown_faces_schema = UnknownFaceSchema(many=True)
