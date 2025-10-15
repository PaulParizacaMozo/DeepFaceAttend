// src/components/CourseCard.tsx

import { useNavigate } from 'react-router-dom';
import type { Course } from '../types';

interface CourseCardProps {
  course: Course;
}

const CourseCard = ({ course }: CourseCardProps) => {
  const navigate = useNavigate();

  const handleViewAttendance = () => {
    navigate(`/attendance/${course.code}`);
  };

  return (
    <div
      className="bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-between hover:shadow-xl transition-shadow duration-300 cursor-pointer"
      onClick={handleViewAttendance}
    >
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">{course.title}</h3>
        <p className="text-sm text-gray-500 font-mono">{course.code}</p>
      </div>
      <div className="mt-4">
        <button
          className="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700"
          onClick={(e) => { e.stopPropagation(); handleViewAttendance(); }}
        >
          Ver Asistencia
        </button>
      </div>
    </div>
  );
};

export default CourseCard;
