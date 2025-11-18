import AttendanceTableHeader from './AttendanceTableHeader';
import AttendanceTableRow from './AttendanceTableRow';
import type { Student } from '../../types';

interface AttendanceTableProps {
  students: Student[];
  attendanceDates: string[];
  attendance: { [studentId: string]: { [date: string]: string } };
  loading: boolean;
  error: string | null;
}

const AttendanceTable = ({ 
  students, 
  attendanceDates, 
  attendance, 
  loading, 
  error 
}: AttendanceTableProps) => {
  if (loading) {
    return <p className="p-8 text-center text-gray-600">Cargando datos del curso...</p>;
  }

  if (error) {
    return <p className="p-8 text-center text-red-600">{error}</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left border-collapse">
        <AttendanceTableHeader attendanceDates={attendanceDates} />
        <tbody>
          {students.map((student) => (
            <AttendanceTableRow
              key={student.id}
              student={student}
              attendanceDates={attendanceDates}
              attendance={attendance}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AttendanceTable;