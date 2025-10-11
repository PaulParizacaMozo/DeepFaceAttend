import CourseCard from '../components/CourseCard';
import Header from '../components/Header';
import { type Course } from '../types';

// Datos de los cursos por defecto
const courses: Course[] = [
  { title: 'Trabajo Interdisciplinar 3', code: '1705267' },
  { title: 'Cloud Computing', code: '1705265' },
  { title: 'Internet de las Cosas', code: '1705268' },
  { title: 'Robotica (E)', code: '1705269' },
  { title: 'Topicos en Ciberserguridad (E)', code: '1705270' },
];

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Mis Cursos" />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {courses.map((course) => (
            <CourseCard key={course.code} course={course} />
          ))}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;