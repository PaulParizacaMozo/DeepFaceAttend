// frontend/src/components/attendance/AttendanceControls.tsx
import { useNavigate } from 'react-router-dom';
import ExportPDFButton from '../ExportPDFButton';
import ExportExcelButton from '../ExportExcelButton';
import type { Course, Student, User } from '../../types';

interface AttendanceControlsProps {
  course: Course;
  students: Student[];
  attendanceDates: string[];
  attendance: { [studentId: string]: { [date: string]: string } };
  user: User;
  loading: boolean;
  activeSchedule: any;
  isTakingAttendance: boolean;
  onTakeAttendance: () => void;
}

const AttendanceControls = ({
  course,
  students,
  attendanceDates,
  attendance,
  user,
  loading,
  activeSchedule,
  isTakingAttendance,
  onTakeAttendance
}: AttendanceControlsProps) => {
  const navigate = useNavigate();

  if (user?.role !== 'teacher') return null;

  return (
    <div className="mb-6 flex flex-col sm:flex-row justify-between items-center gap-4">
      <div className="flex gap-2">
        <ExportPDFButton
          course={course}
          students={students}
          attendanceDates={attendanceDates}
          attendance={attendance}
          user={user}
          loading={loading}
        />
        <ExportExcelButton 
          course={course}
          students={students}
          attendanceDates={attendanceDates}
          attendance={attendance}
          user={user}
          loading={loading}
        />
      </div>
      
      <div className="flex gap-3">
        {/* BOTÓN CORREGIDO: La ruta debe coincidir con App.tsx */}
        <button
          onClick={() => navigate(`/attendance/${course.code}/edit`)}
          className="flex items-center gap-2 bg-green-600 text-white font-semibold py-2 px-5 rounded-lg hover:bg-green-700 transition-colors shadow-sm cursor-pointer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
          </svg>
          Editar Asistencia
        </button>

        <button
          onClick={onTakeAttendance}
          disabled={!activeSchedule || isTakingAttendance}
          className="bg-green-600 text-white font-semibold py-2 px-5 rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed shadow-sm"
          title={!activeSchedule ? "Solo se puede tomar asistencia durante el horario de clase" : ""}
        >
          {isTakingAttendance ? 'Iniciando...' : 'Tomar Asistencia Ahora'}
        </button>
      </div>
    </div>
  );
};

export default AttendanceControls;