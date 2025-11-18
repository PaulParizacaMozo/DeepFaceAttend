import AttendanceStatusCell from './AttendanceStatusCell';
import type { Student } from '../../types';

interface AttendanceTableRowProps {
  student: Student;
  attendanceDates: string[];
  attendance: { [studentId: string]: { [date: string]: string } };
}

const AttendanceTableRow = ({ student, attendanceDates, attendance }: AttendanceTableRowProps) => {
  return (
    <tr className="border-b border-gray-200 last:border-0 hover:bg-gray-50/70 transition-colors duration-150">
      <td className="sticky left-0 px-4 py-3 whitespace-nowrap text-sm text-gray-800 bg-white w-32">
        {student.cui}
      </td>
      <td className="sticky left-0 px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 bg-white w-72 border-r border-gray-200">
        <span className="truncate" title={`${student.last_name}, ${student.first_name}`}>
          {`${student.last_name}, ${student.first_name}`}
        </span>
      </td>
      {attendanceDates.map((date) => (
        <AttendanceStatusCell
          key={date}
          studentId={student.id}
          date={date}
          attendance={attendance}
        />
      ))}
    </tr>
  );
};

export default AttendanceTableRow;