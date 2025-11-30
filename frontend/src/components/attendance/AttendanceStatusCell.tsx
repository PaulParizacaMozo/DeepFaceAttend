interface AttendanceStatusCellProps {
  studentId: string;
  date: string;
  attendance: { [studentId: string]: { [date: string]: string } };
}

const AttendanceStatusCell = ({ studentId, date, attendance }: AttendanceStatusCellProps) => {
  const getStatusSymbol = () => {
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
    <td className="px-2 py-3 whitespace-nowrap text-center">
      {getStatusSymbol()}
    </td>
  );
};

export default AttendanceStatusCell;