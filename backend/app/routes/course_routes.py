from flask import Blueprint, request, jsonify
from app import db
from app.models.course import Course
from app.schemas.course_schema import course_schema, courses_schema

courses_bp = Blueprint('courses_bp', __name__, url_prefix='/courses')

@courses_bp.route('/', methods=['POST'])
def add_course():
    data = request.get_json()
    new_course = course_schema.load(data, session=db.session)
    db.session.add(new_course)
    db.session.commit()
    return course_schema.jsonify(new_course), 201

@courses_bp.route('/', methods=['GET'])
def get_courses():
    all_courses = Course.query.all()
    return courses_schema.jsonify(all_courses), 200

@courses_bp.route('/<string:course_code>', methods=['GET'])
def get_course_by_code(course_code):
    course = Course.query.filter_by(course_code=course_code).first_or_404()
    return course_schema.jsonify(course)
