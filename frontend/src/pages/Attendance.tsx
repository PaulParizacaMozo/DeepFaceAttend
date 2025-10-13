import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import type { Student, Course, AttendanceRecord } from '../types';
import Header from '../components/Header';

// --- Funciones de Utilidad ---
const generateSemesterDates = (start: string, end: string, daysOfWeek: number[]): string[] => {
  const dates = [];
  const currentDate = new Date(`${start}T00:00:00Z`);
  const endDate = new Date(`${end}T00:00:00Z`);

  while (currentDate <= endDate) {
    // getUTCDay() es la versión UTC de getDay() -> Domingo=0, Lunes=1..
    const day = currentDate.getUTCDay() === 0 ? 7 : currentDate.getUTCDay();

    if (daysOfWeek.includes(day)) {
      // Usamos toISOString para obtener el formato YYYY-MM-DD
      dates.push(currentDate.toISOString().split('T')[0]);
    }
    // Sumamos el día en UTC para mantener la consistencia
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

  const [students, setStudents] = useState<Student[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [attendance, setAttendance] = useState<{ [studentId: string]: { [date: string]: string } }>({});
  const [attendanceDates, setAttendanceDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!courseCode) return;

    const fetchData = async () => {
      try {
        setLoading(true);

        // 1. Obtener datos del curso para conseguir su ID (UUID)
        const courseRes = await axios.get(`http://localhost:5000/courses/${courseCode}`);
        const courseData = courseRes.data;
        const courseId = courseData.id;

        // 2. Obtener el resto de los datos en paralelo
        const [studentsRes, enrollmentsRes, attendanceRes] = await Promise.all([
          axios.get('http://localhost:5000/students'),
          axios.get('http://localhost:5000/enrollments'),
          axios.post('http://localhost:5000/attendance/search', { course_id: courseId })
        ]);

        // 3. Procesar datos del curso y generar fechas
        const formattedCourse: Course = {
          id: courseData.id,
          title: courseData.course_name,
          code: courseData.course_code,
          schedules: courseData.schedules,
        };
        setCourse(formattedCourse);

        if (formattedCourse.schedules && formattedCourse.schedules.length > 0) {
          const daysOfWeek = formattedCourse.schedules.map(s => s.day_of_week);
          const uniqueDays = [...new Set(daysOfWeek)];
          console.log('Días de la semana usados para generar el calendario:', uniqueDays);
          setAttendanceDates(generateSemesterDates('2025-09-01', '2025-12-20', uniqueDays));
        }

        // 4. Filtrar estudiantes matriculados en este curso
        const allStudents: Student[] = studentsRes.data;
        const enrollmentsForCourse = enrollmentsRes.data.filter((e: any) => e.course_id === courseId);
        const studentIdsForCourse = new Set(enrollmentsForCourse.map((e: any) => e.student_id));
        const studentsInCourse = allStudents.filter(s => studentIdsForCourse.has(s.id));
        setStudents(studentsInCourse);

        // 5. Procesar los registros de asistencia en un mapa para búsqueda rápida
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
        return <span className="text-gray-300 text-2xl" title="Sin registro">-</span>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header
        title={`Asistencia - ${course?.title || 'Cargando...'}`}
        showBackButton
        onBack={() => navigate('/dashboard')}
      />


      {/* CARD */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden p-4">

        {/* ENCABEZADO IZQ + CONTENIDO, TODO ALINEADO */}
        <div className="flex">

          {/* PANEL IZQUIERDO (FIJO) */}
          <div className="w-[26rem]">
            {/* Header izquierdo */}
            <div className="grid grid-cols-[8rem_18rem] h-12 bg-gray-50 border-b border-gray-200">
              <div className="px-4 flex items-center font-semibold text-gray-700 border-r">CUI</div>
              <div className="px-4 flex items-center font-semibold text-gray-700">Apellidos y Nombres</div>
            </div>

            {/* Filas izquierda */}
            {students.map((s) => {
              const fullName = `${s.last_name}, ${s.first_name}`;
              return (
                <div key={s.id} className="grid grid-cols-[8rem_18rem] h-14 border-b border-gray-200">
                  <div className="px-4 flex items-center text-sm text-gray-800">{s.cui}</div>
                  <div className="px-4 flex items-center text-sm font-medium text-gray-900 border-l border-gray-200">
                    <span className="truncate w-full" title={fullName}>{fullName}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* PANEL DERECHO (ÚNICO SCROLL PARA HEADER + FILAS) */}
          <div className="flex-1 border-l border-gray-200 overflow-x-auto">
            <div className="min-w-max">
              {/* Header de fechas - dentro del MISMO contenedor scrollable */}
              <div className="flex h-12 bg-gray-50 border-b border-gray-200">
                {attendanceDates.map((date) => (
                  <div key={date} className="w-16 px-2 flex items-center justify-center text-center font-semibold text-gray-700">
                    {formatDateHeader(date)}
                  </div>
                ))}
              </div>

              {/* Filas derecha (asistencia) */}
              {students.map((s) => (
                <div key={s.id} className="flex h-14 border-b border-gray-200">
                  {attendanceDates.map((date) => (
                    <div key={date} className="w-16 px-2 flex items-center justify-center">
                      {getStatusSymbol(s.id, date)}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>

  );
};

export default Attendance;
