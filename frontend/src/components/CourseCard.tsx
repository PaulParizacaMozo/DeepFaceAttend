import { Link } from 'react-router-dom';
import type { Course } from '../types';

interface CourseCardProps {
  course: Course;
}

const CourseCard = ({ course }: CourseCardProps) => {
  return (
    <Link to={`/course/${course.code}`} className="block group">
      <div className="bg-white p-6 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border border-transparent hover:border-primary/50 h-full">
        <h3 className="text-xl font-medium text-gray-900 group-hover:text-primary transition-colors">
          {course.title}
        </h3>
        <p className="text-gray-custom mt-2">{course.code}</p>
      </div>
    </Link>
  );
};

export default CourseCard;