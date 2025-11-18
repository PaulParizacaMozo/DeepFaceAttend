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
  if (user?.role !== 'teacher') return null;
  

  return (
    <div className="mb-6 flex justify-between items-center">
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
      
      <button
        onClick={onTakeAttendance}
        disabled={!activeSchedule || isTakingAttendance}
        className="bg-green-600 text-white font-semibold py-2 px-5 rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        title={!activeSchedule ? "Solo se puede tomar asistencia durante el horario de clase" : ""}
      >
        {isTakingAttendance ? 'Iniciando...' : 'Tomar Asistencia Ahora'}
      </button>
    </div>
  );
};

export default AttendanceControls;