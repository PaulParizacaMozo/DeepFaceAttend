import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import type { Course, AttendanceRecord } from '../types';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth'; 

// --- Funciones de Utilidad ---
const generateSemesterDates = (start: string, end: string, daysOfWeek: number[]): string[] => {
  const dates: string[] = [];
  const currentDate = new Date(`${start}T00:00:00Z`);
  const endDate = new Date(`${end}T00:00:00Z`);
  while (currentDate <= endDate) {
    const day = currentDate.getUTCDay() === 0 ? 7 : currentDate.getUTCDay();
    if (daysOfWeek.includes(day)) {
      dates.push(currentDate.toISOString().split('T')[0]);
    }
    currentDate.setUTCDate(currentDate.getUTCDate() + 1);
  }
  return dates;
};

const monthAbbreviations: { [key: string]: string } = { '01': 'ENE', '02': 'FEB', '03': 'MAR', '04': 'ABR', '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AGO', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DIC' };

// Componente simple para mostrar el estado
const getStatusComponent = (status: string | undefined) => {
  switch (status) {
    case 'presente':
      return <span className="text-green-500 font-bold" title="Presente">Presente</span>;
    case 'tarde':
      return <span className="text-yellow-500 font-bold" title="Tarde">Tarde</span>;
    case 'ausente':
      return <span className="text-red-500 font-bold" title="Ausente">Ausente</span>;
    default:
      return <span className="text-gray-400 font-medium" title="Sin registro">Sin Registro</span>;
  }
};

// --- Componente Principal de Asistencia del Estudiante ---
const AttendanceStudent = () => {
  const { courseCode } = useParams<{ courseCode: string }>();
  const navigate = useNavigate();
  const { user } = useAuth(); // Obtiene el usuario logueado

  const [course, setCourse] = useState<Course | null>(null);
  const [myAttendance, setMyAttendance] = useState<{ [date: string]: string }>({});
  const [attendanceDates, setAttendanceDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // No hacer nada si no tenemos el código del curso o el CUI del usuario
    if (!courseCode || !user?.cui) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        
        // 1. Obtener la info del curso (para ID y horarios)
        const courseRes = await api.get(`/courses/${courseCode}`);
        const courseData = courseRes.data;
        const courseId = courseData.id;

        // 2. Obtener el ID de estudiante usando el CUI del usuario
        // (Esto asume que /students devuelve todos los estudiantes)
        const studentsRes = await api.get('/students');
        console.log(user.cui);
        const myStudentProfile = studentsRes.data.find((s: any) => s.cui === user.cui);
        
        if (!myStudentProfile) {
          throw new Error("No se pudo encontrar tu perfil de estudiante.");
        }
        const myStudentId = myStudentProfile.id;

        // 3. Obtener solo la asistencia de este curso
        const attendanceRes = await api.post('/attendance/search', { course_id: courseId });

        // 4. Filtrar la asistencia solo para el estudiante actual
        const attendanceMap: { [date: string]: string } = {};
        attendanceRes.data
          .filter((record: AttendanceRecord) => record.student_id === myStudentId)
          .forEach((record: AttendanceRecord) => {
            attendanceMap[record.attendance_date] = record.status;
          });
        setMyAttendance(attendanceMap);

        // 5. Configurar curso y fechas
        const formattedCourse: Course = {
          id: courseData.id,
          title: courseData.course_name,
          code: courseData.course_code,
          schedules: courseData.schedules,
        };
        setCourse(formattedCourse);

        if (formattedCourse.schedules && formattedCourse.schedules.length > 0) {
          const daysOfWeek = formattedCourse.schedules.map(s => s.day_of_week);
          // Usamos un rango de fechas de ejemplo, idealmente esto vendría del backend
          setAttendanceDates(generateSemesterDates('2025-09-01', '2025-12-20', [...new Set(daysOfWeek)]));
        }

        setError(null);
      } catch (err: any) {
        console.error("Error fetching student attendance:", err);
        setError(err.message || 'No se pudo cargar tu asistencia.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [courseCode, user?.cui]); // Depende del CUI del usuario

  return (
    <div className="min-h-screen bg-gray-100 pb-12">
      <Header
        title={`Mi Asistencia - ${course?.title || 'Cargando...'}`}
        showBackButton
        onBack={() => navigate('/dashboard')}
      />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {loading && <p className="p-8 text-center text-gray-600">Cargando mi registro...</p>}
          {error && <p className="p-8 text-center text-red-600">{error}</p>}
          
          {!loading && !error && (
            <div className="divide-y divide-gray-200">
              {/* Encabezado de la lista */}
              <div className="p-4 flex justify-between items-center bg-gray-50">
                <span className="font-semibold text-gray-700">Fecha de Clase</span>
                <span className="font-semibold text-gray-700">Estado</span>
              </div>
              
              {/* Renderiza la lista de asistencia */}
              {attendanceDates.map((date) => {
                const [year, month, day] = date.split('-');
                const status = myAttendance[date];
                return (
                  <div key={date} className="p-4 flex justify-between items-center hover:bg-gray-50">
                    <div className="flex items-center">
                      <div className="flex flex-col items-center justify-center bg-gray-100 rounded-lg w-16 h-16 p-2 mr-4">
                        <span className="text-xs font-bold text-gray-500 uppercase">{monthAbbreviations[month] || ''}</span>
                        <span className="text-2xl font-bold text-gray-800">{day}</span>
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">
                          {new Date(date + 'T00:00:00Z').toLocaleDateString('es-ES', { weekday: 'long', timeZone: 'UTC' })}
                        </p>
                        <p className="text-sm text-gray-500">{`${day} de ${new Date(date + 'T00:00:00Z').toLocaleDateString('es-ES', { month: 'long', timeZone: 'UTC' })} de ${year}`}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      {getStatusComponent(status)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AttendanceStudent;