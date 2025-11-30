// frontend/src/pages/EditAttendance.tsx
import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Student, Course, AttendanceRecord } from '../types';
import api from '../services/api';
import Header from '../components/Header';
import { generateSemesterDates } from '../utils/attendanceHelpers';

const EditAttendance = () => {
  const { courseCode } = useParams<{ courseCode: string }>();
  const navigate = useNavigate();

  // Estados
  const [students, setStudents] = useState<Student[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  // Mapa de asistencia editable en memoria
  const [attendanceMap, setAttendanceMap] = useState<{ [studentId: string]: { [date: string]: string } }>({});
  const [attendanceDates, setAttendanceDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Cargar datos (similar a Attendance.tsx pero sin polling)
  const fetchAllData = useCallback(async () => {
    if (!courseCode) return;
    
    try {
      setLoading(true);
      const courseRes = await api.get(`/courses/${courseCode}`);
      const courseData = courseRes.data;
      const courseId = courseData.id;

      const [studentsRes, enrollmentsRes, attendanceRes] = await Promise.all([
        api.get('/students'),
        api.get('/enrollments'),
        api.post('/attendance/search', { course_id: courseId })
      ]);

      // Formatear Curso
      const formattedCourse: Course = { 
        id: courseData.id, 
        title: courseData.course_name, 
        code: courseData.course_code, 
        schedules: courseData.schedules 
      };
      setCourse(formattedCourse);
      
      // Generar fechas
      if (formattedCourse.schedules && formattedCourse.schedules.length > 0) {
        const daysOfWeek = formattedCourse.schedules.map(s => s.day_of_week);
        setAttendanceDates(generateSemesterDates('2025-09-01', '2025-12-20', [...new Set(daysOfWeek)]));
      }

      // Filtrar estudiantes
      const enrollmentsForCourse = enrollmentsRes.data.filter((e: any) => e.course_id === courseId);
      const studentIdsForCourse = new Set(enrollmentsForCourse.map((e: any) => e.student_id));
      const filteredStudents = studentsRes.data
        .filter((s: Student) => studentIdsForCourse.has(s.id))
        .sort((a: Student, b: Student) => a.last_name.localeCompare(b.last_name)); // Ordenar alfabéticamente
      
      setStudents(filteredStudents);

      // Mapear asistencia existente
      const initialMap: { [studentId: string]: { [date: string]: string } } = {};
      attendanceRes.data.forEach((record: AttendanceRecord) => {
        if (!initialMap[record.student_id]) { 
          initialMap[record.student_id] = {}; 
        }
        initialMap[record.student_id][record.attendance_date] = record.status;
      });
      setAttendanceMap(initialMap);

    } catch (err) {
      console.error("Error loading edit data:", err);
      alert("Error al cargar los datos para edición.");
    } finally {
      setLoading(false);
    }
  }, [courseCode]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Manejar cambio en un Select
  const handleStatusChange = (studentId: string, date: string, newStatus: string) => {
    setAttendanceMap(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [date]: newStatus
      }
    }));
  };

  // Guardar cambios masivos
  const handleSaveChanges = async () => {
    if (!course) return;
    setSaving(true);

    try {
      // Convertir el mapa a un array plano de registros para enviar al backend
      const recordsToUpdate = [];
      
      for (const student of students) {
        for (const date of attendanceDates) {
          const status = attendanceMap[student.id]?.[date];
          // Solo enviamos si hay un estatus definido (o si el backend acepta vacíos para borrar)
          if (status) {
            recordsToUpdate.push({
              student_id: student.id,
              course_id: course.id,
              attendance_date: date,
              status: status
            });
          }
        }
      }

      // Asumimos un endpoint batch. Si no existe, tendrías que hacer loop de llamadas (no recomendado)
      // o adaptar tu backend para recibir un array en /attendance/batch
      await api.post('/attendance/batch', { records: recordsToUpdate });
      
      alert('Cambios guardados correctamente');
      navigate(-1); // Volver a la página anterior
    } catch (err) {
      console.error("Error saving attendance:", err);
      alert("Error al guardar los cambios. Intente nuevamente.");
    } finally {
      setSaving(false);
    }
  };

  // Helper para colores del select
  const getSelectClass = (status: string | undefined) => {
    const base = "block w-full py-1 px-2 text-sm border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md shadow-sm cursor-pointer font-medium ";
    switch (status) {
      case 'presente': return base + "bg-green-50 text-green-700 border-green-200";
      case 'tarde': return base + "bg-yellow-50 text-yellow-700 border-yellow-200";
      case 'ausente': return base + "bg-red-50 text-red-700 border-red-200";
      default: return base + "bg-white text-gray-500 border-gray-200";
    }
  };

  if (loading) return <div className="p-10 text-center">Cargando modo edición...</div>;

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header
        title={`Editar Asistencia - ${course?.title || '...'}`}
        showBackButton
        onBack={() => navigate(-1)}
      />

      <main className="max-w-[95%] mx-auto mt-24 px-4">
        
        {/* Barra superior de acciones */}
        <div className="flex justify-between items-center mb-4 bg-white p-4 rounded-lg shadow-sm border border-gray-200 sticky top-20 z-30">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">Modo Edición Manual</h2>
            <p className="text-sm text-gray-500">Modifique los valores y haga clic en Guardar.</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition cursor-pointer"
            >
              Cancelar
            </button>
            <button
              onClick={handleSaveChanges}
              disabled={saving}
              className="px-6 py-2 bg-green-600 text-white font-bold rounded-md hover:bg-green-700 shadow-md transition disabled:bg-green-300 flex items-center gap-2 cursor-pointer"
            >
              {saving ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Guardando...
                </>
              ) : (
                'Guardar Cambios'
              )}
            </button>
          </div>
        </div>

        {/* Tabla estilo Excel */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div className="overflow-x-auto max-h-[70vh]">
            <table className="min-w-full border-collapse">
              {/* Header Sticky */}
              <thead className="bg-gray-100 sticky top-0 z-20">
                <tr>
                  <th className="sticky left-0 z-30 bg-gray-100 p-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-r border-gray-300 w-20 shadow-[1px_0_2px_rgba(0,0,0,0.1)]">
                    CUI
                  </th>
                  <th className="sticky left-[5rem] z-30 bg-gray-100 p-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-r border-gray-300 min-w-[200px] shadow-[2px_0_5px_rgba(0,0,0,0.1)]">
                    Estudiante
                  </th>
                  {attendanceDates.map(date => {
                     const dateObj = new Date(date + 'T00:00:00');
                     const dayName = dateObj.toLocaleDateString('es-ES', { weekday: 'short' });
                     const dayNum = dateObj.getDate();
                     const month = dateObj.toLocaleDateString('es-ES', { month: 'short' });

                     return (
                      <th key={date} className="px-2 py-3 text-center border-b border-gray-200 min-w-[100px]">
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] uppercase font-bold text-gray-400">{dayName}</span>
                          <span className="text-sm font-bold text-gray-700">{dayNum} {month}</span>
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>

              {/* Body */}
              <tbody className="divide-y divide-gray-200">
                {students.map((student) => (
                  <tr key={student.id} className="hover:bg-blue-50/30 transition-colors">
                    {/* CUI Sticky */}
                    <td className="sticky left-0 z-10 bg-white text-xs font-medium text-gray-600 p-3 border-r border-gray-200 whitespace-nowrap shadow-[1px_0_2px_rgba(0,0,0,0.05)]">
                      {student.cui}
                    </td>
                    {/* Nombre Sticky */}
                    <td className="sticky left-[5rem] z-10 bg-white text-sm font-semibold text-gray-800 p-3 border-r border-gray-200 whitespace-nowrap shadow-[2px_0_5px_rgba(0,0,0,0.05)]">
                      {student.last_name}, {student.first_name}
                    </td>
                    
                    {/* Celdas Editables */}
                    {attendanceDates.map((date) => {
                      const currentStatus = attendanceMap[student.id]?.[date] || "";
                      
                      return (
                        <td key={`${student.id}-${date}`} className="p-1 border-r border-gray-100 text-center min-w-[100px]">
                          <select
                            value={currentStatus}
                            onChange={(e) => handleStatusChange(student.id, date, e.target.value)}
                            className={getSelectClass(currentStatus)}
                          >
                            <option value="">-</option>
                            <option value="presente">Presente</option>
                            <option value="tarde">Tarde</option>
                            <option value="ausente">Ausente</option>
                          </select>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EditAttendance;