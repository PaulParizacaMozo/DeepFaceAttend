import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import type { Course, AttendanceRecord } from '../types';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth'; 

// --- Funciones de Utilidad (sin cambios) ---
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
  const { user } = useAuth();

  const [course, setCourse] = useState<Course | null>(null);
  const [myAttendance, setMyAttendance] = useState<{ [date: string]: string }>({});
  
  // --- NUEVO ESTADO PARA FECHAS AGRUPADAS ---
  const [datesByMonth, setDatesByMonth] = useState<{ [key: string]: string[] }>({});
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!courseCode || !user?.cui) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        
        const courseRes = await api.get(`/courses/${courseCode}`);
        const courseData = courseRes.data;
        const courseId = courseData.id;

        const studentsRes = await api.get('/students');
        const myStudentProfile = studentsRes.data.find((s: any) => s.cui === user.cui);
        
        if (!myStudentProfile) {
          throw new Error("No se pudo encontrar tu perfil de estudiante.");
        }
        const myStudentId = myStudentProfile.id;

        const attendanceRes = await api.post('/attendance/search', { course_id: courseId });

        const attendanceMap: { [date: string]: string } = {};
        attendanceRes.data
          .filter((record: AttendanceRecord) => record.student_id === myStudentId)
          .forEach((record: AttendanceRecord) => {
            attendanceMap[record.attendance_date] = record.status;
          });
        setMyAttendance(attendanceMap);

        const formattedCourse: Course = {
          id: courseData.id,
          title: courseData.course_name,
          code: courseData.course_code,
          schedules: courseData.schedules,
        };
        setCourse(formattedCourse);

        if (formattedCourse.schedules && formattedCourse.schedules.length > 0) {
          const daysOfWeek = formattedCourse.schedules.map(s => s.day_of_week);
          const allDates = generateSemesterDates('2025-09-01', '2025-12-20', [...new Set(daysOfWeek)]);

          // --- LÓGICA PARA AGRUPAR FECHAS POR MES ---
          const groupedDates = allDates.reduce((acc, date) => {
            const monthKey = date.substring(0, 7); // "2025-09"
            if (!acc[monthKey]) {
              acc[monthKey] = [];
            }
            acc[monthKey].push(date);
            return acc;
          }, {} as { [key: string]: string[] });
          
          setDatesByMonth(groupedDates);
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
  }, [courseCode, user?.cui]);

  return (
    <div className="min-h-screen bg-gray-100 pb-12">
      <Header
        title={`Mi Asistencia - ${course?.title || 'Cargando...'}`}
        showBackButton
        onBack={() => navigate('/dashboard')}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {loading && <p className="p-8 text-center text-gray-600">Cargando mi registro...</p>}
          {error && <p className="p-8 text-center text-red-600">{error}</p>}
          
          {!loading && !error && (
            // --- REFACTORIZACIÓN DEL CONTENEDOR ---
            // 1. Ahora es un contenedor de secciones por mes
            <div className="space-y-6 lg:space-y-8 p-4 lg:p-8">
              
              {/* 2. Bucle exterior sobre cada mes */}
              {Object.keys(datesByMonth).sort().map(monthKey => {
                const monthDates = datesByMonth[monthKey];
                
                // Formatear el título del mes (ej. "Septiembre 2025")
                const monthDate = new Date(`${monthKey}-02T00:00:00Z`);
                const monthName = monthDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric', timeZone: 'UTC' });

                return (
                  <section key={monthKey}>
                    {/* Título del Mes */}
                    <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">
                      {monthName.charAt(0).toUpperCase() + monthName.slice(1)}
                    </h2>
                    
                    {/* 3. La cuadrícula/lista responsiva (ahora DENTRO del bucle de mes) */}
                    <div className="divide-y divide-gray-200 lg:divide-y-0 lg:grid lg:grid-cols-3 xl:grid-cols-4 lg:gap-4">
                      
                      {/* 4. Bucle interior sobre las fechas de ESE mes */}
                      {monthDates.map((date) => {
                        const [year, month, day] = date.split('-');
                        const status = myAttendance[date];
                        return (
                          // La tarjeta de asistencia (sin cambios)
                          <div 
                            key={date} 
                            className="p-4 flex justify-between items-center hover:bg-gray-50 
                                       lg:flex-col lg:justify-center lg:border lg:border-gray-200 lg:rounded-lg lg:shadow-sm lg:p-4 lg:gap-2"
                          >
                            <div className="flex items-center lg:flex-col">
                              <div className="flex flex-col items-center justify-center bg-gray-100 rounded-lg w-16 h-16 p-2 mr-4 lg:mr-0">
                                <span className="text-xs font-bold text-gray-500 uppercase">{monthAbbreviations[month] || ''}</span>
                                <span className="text-2xl font-bold text-gray-800">{day}</span>
                              </div>
                              <div className="lg:text-center lg:mt-2">
                                <p className="font-semibold text-gray-900">
                                  {new Date(date + 'T00:00:00Z').toLocaleDateString('es-ES', { weekday: 'long', timeZone: 'UTC' })}
                                </p>
                                <p className="text-sm text-gray-500 lg:hidden">{`${day} de ${new Date(date + 'T00:00:00Z').toLocaleDateString('es-ES', { month: 'long', timeZone: 'UTC' })} de ${year}`}</p>
                              </div>
                            </div>
                            <div className="text-right lg:text-center lg:text-lg">
                              {getStatusComponent(status)}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </section>
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