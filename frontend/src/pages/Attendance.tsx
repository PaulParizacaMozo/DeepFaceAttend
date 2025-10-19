import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import type { Student, Course, AttendanceRecord } from '../types';
import Header from '../components/Header';

// --- Funciones de Utilidad (Versión más reciente y robusta) ---
const generateSemesterDates = (start: string, end: string, daysOfWeek: number[]): string[] => {
  const dates = [];
  // Usar UTC para evitar problemas con zonas horarias
  const currentDate = new Date(`${start}T00:00:00Z`);
  const endDate = new Date(`${end}T00:00:00Z`);

  while (currentDate <= endDate) {
    // getUTCDay() es la versión UTC de getDay() -> Domingo=0, Lunes=1..
    // Se ajusta para que Lunes sea 1 y Domingo 7
    const day = currentDate.getUTCDay() === 0 ? 7 : currentDate.getUTCDay();

    if (daysOfWeek.includes(day)) {
      dates.push(currentDate.toISOString().split('T')[0]);
    }
    currentDate.setUTCDate(currentDate.getUTCDate() + 1);
  }
  return dates;
};

const monthAbbreviations: { [key: string]: string } = {
  '01': 'ene', '02': 'feb', '03': 'mar', '04': 'abr',
  '05': 'may', '06': 'jun', '07': 'jul', '08': 'ago',
  '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dic',
};

const formatDateHeader = (dateString: string) => {
  const [_, month, day] = dateString.split('-');
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <span className="font-bold text-gray-800">{day}</span>
      <span className="text-xs font-medium text-gray-500 uppercase">{monthAbbreviations[month] || ''}</span>
    </div>
  );
};

// --- Componente Principal ---
const Attendance = () => {
  const { courseCode } = useParams<{ courseCode: string }>();
  const navigate = useNavigate();

  // Estados para manejar toda la información dinámica
  const [students, setStudents] = useState<Student[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [attendance, setAttendance] = useState<{ [studentId: string]: { [date: string]: string } }>({});
  const [attendanceDates, setAttendanceDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hook para obtener todos los datos necesarios de la API
  useEffect(() => {
    if (!courseCode) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const courseRes = await axios.get(`http://localhost:5000/courses/${courseCode}`);
        const courseData = courseRes.data;
        const courseId = courseData.id;

        const [studentsRes, enrollmentsRes, attendanceRes] = await Promise.all([
          axios.get('http://localhost:5000/students'),
          axios.get('http://localhost:5000/enrollments'),
          axios.post('http://localhost:5000/attendance/search', { course_id: courseId })
        ]);

        const formattedCourse: Course = {
          id: courseData.id,
          title: courseData.course_name,
          code: courseData.course_code,
          schedules: courseData.schedules,
        };
        setCourse(formattedCourse);

        if (formattedCourse.schedules && formattedCourse.schedules.length > 0) {
          const daysOfWeek = formattedCourse.schedules.map(s => s.day_of_week);
          setAttendanceDates(generateSemesterDates('2025-09-01', '2025-12-20', [...new Set(daysOfWeek)]));
        }

        const enrollmentsForCourse = enrollmentsRes.data.filter((e: any) => e.course_id === courseId);
        const studentIdsForCourse = new Set(enrollmentsForCourse.map((e: any) => e.student_id));
        setStudents(studentsRes.data.filter((s: Student) => studentIdsForCourse.has(s.id)));

        const attendanceMap: { [studentId: string]: { [date: string]: string } } = {};
        attendanceRes.data.forEach((record: AttendanceRecord) => {
          if (!attendanceMap[record.student_id]) {
            attendanceMap[record.student_id] = {};
          }
          attendanceMap[record.student_id][record.attendance_date] = record.status;
        });
        setAttendance(attendanceMap);

        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError('No se pudo cargar la información. Revisa la consola para más detalles.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [courseCode]);

  // Función para obtener el símbolo de asistencia basado en datos reales
  const getStatusSymbol = (studentId: string, date: string) => {
    const status = attendance[studentId]?.[date];
    switch (status) {
      case 'presente':
        return <span className="text-green-500 text-2xl" title="Presente">●</span>;
      case 'tarde':
        return <span className="text-yellow-500 text-2xl" title="Tarde">●</span>;
      case 'ausente':
        return <span className="text-red-500 text-2xl" title="Ausente">●</span>;
      default:
        return <span className="text-gray-300 text-lg font-semibold" title="Sin registro">-</span>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 pb-12">
      <Header
        title={`Asistencia - ${course?.title || 'Cargando...'}`}
        showBackButton
        onBack={() => navigate('/dashboard')}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {loading && <p className="p-8 text-center text-gray-600">Cargando datos del curso...</p>}
          {error && <p className="p-8 text-center text-red-600">{error}</p>}
          
          {!loading && !error && (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left border-collapse">
                <thead className="border-b-2 border-gray-200">
                  <tr>
                    {/* --- Cabeceras Fijas --- */}
                    <th className="sticky left-0 z-10 px-4 py-3 font-semibold text-gray-700 bg-gray-50 w-32">
                      CUI
                    </th>
                    <th className="sticky left-0 z-10 px-4 py-3 font-semibold text-gray-700 bg-gray-50 w-72 border-r border-gray-200">
                      Apellidos y Nombres
                    </th>

                    {/* --- Cabeceras de Fecha con Scroll --- */}
                    {attendanceDates.map((date) => (
                      <th key={date} className="px-2 py-2 font-semibold text-gray-700 text-center w-16">
                        {formatDateHeader(date)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr key={student.id} className="border-b border-gray-200 last:border-0 hover:bg-gray-50/70 transition-colors duration-150">
                      
                      {/* --- Celdas Fijas --- */}
                      <td className="sticky left-0 px-4 py-3 whitespace-nowrap text-sm text-gray-800 bg-white group-hover:bg-gray-50/70 w-32">
                        {student.cui}
                      </td>
                      <td className="sticky left-0 px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 bg-white group-hover:bg-gray-50/70 w-72 border-r border-gray-200">
                        <span className="truncate" title={`${student.last_name}, ${student.first_name}`}>
                          {`${student.last_name}, ${student.first_name}`}
                        </span>
                      </td>

                      {/* --- Celdas de Asistencia con Scroll --- */}
                      {attendanceDates.map((date) => (
                        <td key={date} className="px-2 py-3 whitespace-nowrap text-center">
                          {getStatusSymbol(student.id, date)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Attendance;