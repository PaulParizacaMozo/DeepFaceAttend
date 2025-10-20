// src/pages/Dashboard.tsx
import { useState, useEffect } from 'react';
import api from '../services/api'; // Importamos nuestra instancia de api
import CourseCard from '../components/CourseCard';
import Header from '../components/Header';
import type { Course } from '../types';

const Dashboard = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const response = await api.get('/courses');

        const formattedCourses: Course[] = response.data.map((course: any) => ({
          id: course.id,
          title: course.course_name,
          code: course.course_code,
          schedules: course.schedules,
        }));

        setCourses(formattedCourses);
        setError(null);
      } catch (err) {
        console.error("Error fetching courses:", err);
        setError('No se pudo conectar con el servidor.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Mis Cursos" />
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {loading && <p className="text-center text-gray-500">Cargando cursos...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}
        {!loading && !error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.length > 0 ? (
              courses.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))
            ) : (
              <p className="col-span-full text-center text-gray-500">No se encontraron cursos.</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
