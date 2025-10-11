import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import type { Student } from '../types';
import Header from '../components/Header';

// --- Funciones de Utilidad (sin cambios) ---
const generateSemesterDates = (start: string, end: string, daysOfWeek: number[]): string[] => {
  const dates = [];
  let currentDate = new Date(start);
  const endDate = new Date(end);
  while (currentDate <= endDate) {
    if (daysOfWeek.includes(currentDate.getDay())) {
      dates.push(currentDate.toISOString().split('T')[0]);
    }
    currentDate.setDate(currentDate.getDate() + 1);
  }
  return dates;
};

const attendanceDates = generateSemesterDates('2025-09-01', '2025-12-31', [1, 3]);

const monthAbbreviations: { [key: string]: string } = {
  '01': 'ene', '02': 'feb', '03': 'mar', '04': 'abr',
  '05': 'may', '06': 'jun', '07': 'jul', '08': 'ago',
  '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dic',
};

const formatDateHeader = (dateString: string) => {
  const [_, month, day] = dateString.split('-');
  const monthAbbr = monthAbbreviations[month] || '';
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <span className="font-bold text-gray-800">{day}</span>
      <span className="text-xs font-medium text-gray-500 uppercase">{monthAbbr}</span>
    </div>
  );
};

// --- Datos del Componente (sin cambios) ---
const courseDetails: { [key: string]: string } = {
  '1705267': 'Trabajo Interdisciplinar 3',
  '1705265': 'Cloud Computing',
  '1705268': 'Internet de las Cosas',
  '1705269': 'Robotica (E)',
  '1705270': 'Topicos en Ciberserguridad (E)',
};


const Attendance = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const courseTitle = courseId ? courseDetails[courseId] : 'Curso no encontrado';

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/students');
        setStudents(response.data);
        setError(null);
      } catch (err) {
        console.error("Error fetching students:", err);
        setError('No se pudo cargar la lista de estudiantes. Asegúrate de que el backend esté funcionando.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  const getStatusSymbol = (studentId: string, date: string) => {
    const hash = (studentId + date).split('').reduce((acc, char) => char.charCodeAt(0) + ((acc << 5) - acc), 0);
    const value = hash % 10;
    if (value < 7) return <span className="text-green-500 text-2xl" title="Presente">●</span>;
    if (value < 9) return <span className="text-yellow-500 text-2xl" title="Tarde">●</span>;
    return <span className="text-red-500 text-2xl" title="Ausente">●</span>;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title={`Asistencia - ${courseTitle}`} showBackButton={true} onBack={() => navigate('/dashboard')} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {loading && <p className="p-8 text-center text-gray-600">Cargando estudiantes...</p>}
          {error && <p className="p-8 text-center text-red-600">{error}</p>}
          {!loading && !error && (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left border-collapse">
                <thead className="border-b border-gray-200">
                  <tr>
                    {/* --- Cabeceras Fijas (AQUÍ ESTÁ EL CAMBIO) --- */}
                    <th className="sticky left-0 z-10 px-4 py-3 font-semibold text-gray-700 bg-gray-50 w-32 border-r border-gray-200">
                      CUI
                    </th>
                    <th className="sticky left-0 z-10 px-4 py-3 font-semibold text-gray-700 bg-gray-50 w-72">
                      Apellidos y Nombres
                    </th>

                    {/* --- Cabeceras de Fecha con Scroll --- */}
                    {attendanceDates.map((date, index) => (
                      <th key={`${date}-${index}`} className="px-2 py-2 font-semibold text-gray-700 text-center w-16">
                        {formatDateHeader(date)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {students.map((student) => (
                    <tr key={student.id} className="hover:bg-gray-50/70 transition-colors duration-150">
                      {/* --- Celdas Fijas (AQUÍ ESTÁ EL CAMBIO) --- */}
                      <td className="sticky left-0 px-4 py-3 whitespace-nowrap text-sm text-gray-800 bg-white hover:bg-gray-50/70 w-32 border-r border-gray-200">
                        {student.cui}
                      </td>
                      <td className="sticky left-0 px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 bg-white hover:bg-gray-50/70 w-72">
                        {`${student.last_name}, ${student.first_name}`}
                      </td>

                      {/* --- Celdas de Asistencia con Scroll --- */}
                      {attendanceDates.map((date, index) => (
                        <td key={`${date}-${index}`} className="px-2 py-3 whitespace-nowrap text-center">
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