// src/pages/Dashboard.tsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import CourseCard from "../components/CourseCard";
import Header from "../components/Header";
import type { Course } from "../types";
import { useAuth } from "../hooks/useAuth";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkingBiometrics, setCheckingBiometrics] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBiometricStatus = async () => {
      // Si no hay usuario o no es estudiante, saltamos la validación
      if (!user || user.role !== "student") {
        setCheckingBiometrics(false);
        return;
      }

      try {
        // Llamada al endpoint solicitado
        const response = await api.get(`/students/check-embeddings/${user.id}`);

        const hasEmbeddings = response.data.has_embeddings;

        if (!hasEmbeddings) {
          // Si es false, forzamos la redirección a la vista de subir fotos
          console.log("Biometría incompleta, redirigiendo...");
          navigate("/update-biometrics");
        } else {
          // Si es true, permitimos cargar el dashboard
          setCheckingBiometrics(false);
        }
      } catch (err) {
        console.error("Error verificando biometría:", err);
        // En caso de error (ej. servidor caído), decidimos si bloquear o dejar pasar.
        // Por seguridad, dejamos pasar pero logueamos el error, o mostramos alerta.
        setCheckingBiometrics(false);
      }
    };

    checkBiometricStatus();
  }, [user, navigate]);

  useEffect(() => {
    const fetchMyCourses = async () => {
      try {
        setLoading(true);
        // --- CAMBIO CLAVE AQUÍ ---
        // Llamamos al nuevo endpoint que devuelve los cursos del usuario logueado.
        const response = await api.get("/auth/profile/courses");
        console.log("Fetched courses:", response.data);

        // El resto de la lógica para formatear los datos no necesita cambios.
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
        setError("No se pudo conectar con el servidor.");
      } finally {
        setLoading(false);
      }
    };

    fetchMyCourses();
  }, []); // El array de dependencias vacío asegura que se ejecute solo una vez.

  // Si estamos verificando biometría, mostramos un loader de pantalla completa o simple
  if (checkingBiometrics) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-gray-600 font-medium animate-pulse">
          Verificando estado biométrico...
        </p>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Mis Cursos" />
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {loading && (
          <p className="text-center text-gray-500">Cargando cursos...</p>
        )}
        {error && <p className="text-center text-red-500">{error}</p>}
        {!loading && !error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.length > 0 ? (
              courses.map((course) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  userRole={user?.role}
                />
              ))
            ) : (
              <p className="col-span-full text-center text-gray-500">
                No tienes cursos asignados o matriculados.
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
