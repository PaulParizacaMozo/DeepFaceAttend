const monthAbbreviations: { [key: string]: string } = { 
  '01': 'ene', '02': 'feb', '03': 'mar', '04': 'abr', '05': 'may', '06': 'jun', 
  '07': 'jul', '08': 'ago', '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dic' 
};

const formatDateHeader = (dateString: string) => {
  const [_, month, day] = dateString.split('-');
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <span className="font-bold text-gray-800">{day}</span>
      <span className="text-xs font-medium text-gray-500 uppercase">
        {monthAbbreviations[month] || ''}
      </span>
    </div>
  );
};

interface AttendanceTableHeaderProps {
  attendanceDates: string[];
}

const AttendanceTableHeader = ({ attendanceDates }: AttendanceTableHeaderProps) => {
  return (
    <thead className="border-b-2 border-gray-200">
      <tr>
        <th className="sticky left-0 z-10 px-4 py-3 font-semibold text-gray-700 bg-gray-50 w-32">CUI</th>
        <th className="sticky left-0 z-10 px-4 py-3 font-semibold text-gray-700 bg-gray-50 w-72 border-r border-gray-200">
          Apellidos y Nombres
        </th>
        {attendanceDates.map((date) => (
          <th key={date} className="px-2 py-2 font-semibold text-gray-700 text-center w-16">
            {formatDateHeader(date)}
          </th>
        ))}
      </tr>
    </thead>
  );
};

export default AttendanceTableHeader;