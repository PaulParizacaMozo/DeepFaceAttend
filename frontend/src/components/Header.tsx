// src/components/Header.tsx
import { useAuth } from "../hooks/useAuth";

interface HeaderProps {
    title: string;
    showBackButton?: boolean;
    onBack?: () => void;
}

const Header = ({ title, showBackButton = false, onBack }: HeaderProps) => {
  const { user, logout } = useAuth();
  console.log("User in <Header />:", user);

  const roleBadgeStyles = user?.role === 'student'
    ? 'bg-yellow-100 text-yellow-800' // Estilo para Estudiante
    : 'bg-rose-100 text-rose-800'; // Estilo para Profesor

  return (
    <header className="bg-white shadow-sm p-4 mb-8 flex justify-between items-center">
      <div className="flex items-center gap-4">
        {showBackButton && (
          <button
            onClick={onBack}
            className="p-2 rounded-full hover:bg-gray-200 transition-colors cursor-pointer"
            aria-label="Volver"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
        <h1 className="text-2xl font-medium text-gray-800">{title}</h1>
      </div>
      
      {/* Contenedor para el nombre, rol y botón de logout */}
      <div className="flex items-center gap-4">
        {user && (
          // Contenedor para alinear nombre y rol
          <div className="items-center gap-3 hidden sm:flex">
            <span className="text-gray-800 font-bold tracking-wider">
              {`${user.first_name} ${user.last_name}`}
            </span>
            <span className={`px-2.5 py-1 uppercase text-xs font-semibold rounded-full ${roleBadgeStyles}`}>
              {user.role}
            </span>
          </div>
        )}
        <button
          onClick={logout}
          className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-opacity-90 transition-colors cursor-pointer"
        >
          Cerrar Sesión
        </button>
      </div>
    </header>
  );
};

export default Header;