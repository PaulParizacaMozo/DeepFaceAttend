import { useState, useEffect } from 'react';
import axios from 'axios';
import CourseCard from '../components/CourseCard';
import Header from '../components/Header';
import type { Course } from '../types';

const Dashboard = () => {
  // 1. Estados para manejar los datos, la carga y los errores
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 2. useEffect para obtener los datos cuando el componente se monta
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        // Hacemos la llamada al backend
        const response = await axios.get('http://localhost:5000/courses');

        // Mapeamos los datos del backend a la estructura que espera el frontend
        const formattedCourses: Course[] = response.data.map((course: any) => ({
          id: course.id, // Guardamos el ID para la navegación
          title: course.course_name,
          code: course.course_code,
          schedules: course.schedules, // Incluimos los horarios
        }));

        setCourses(formattedCourses);
        setError(null);
      } catch (err) {
        console.error("Error fetching courses:", err);
        setError('No se pudo conectar con el servidor. Por favor, inténtalo más tarde.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []); // El array vacío asegura que se ejecute solo una vez

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Mis Cursos" />
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* 3. Renderizado condicional basado en el estado */}
        {loading && <p className="text-center text-gray-500">Cargando cursos...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}
        {!loading && !error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.length > 0 ? (
              courses.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))
            ) : (
              <p className="col-span-full text-center text-gray-500">No se encontraron cursos registrados.</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
