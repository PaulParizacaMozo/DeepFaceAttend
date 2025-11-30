// src/components/Header.tsx
import { useAuth } from "../hooks/useAuth";
import { useLocation, useNavigate } from "react-router-dom";

interface HeaderProps {
  title: string;
  showBackButton?: boolean;
  onBack?: () => void;
}

const Header = ({ title, showBackButton = false, onBack }: HeaderProps) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  console.log("User in <Header />:", user);

  const roleBadgeStyles =
    user?.role === "student"
      ? "bg-yellow-100 text-yellow-800" // Estilo para Estudiante
      : "bg-rose-100 text-rose-800"; // Estilo para Profesor

  const showRecoveryButton =
    user?.role === "student" && location.pathname === "/dashboard";

  return (
    <header className="bg-white shadow-sm p-4 mb-8 flex justify-between items-center fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center gap-4">
        {showBackButton && (
          <button
            onClick={onBack}
            className="p-2 rounded-full hover:bg-gray-200 transition-colors cursor-pointer"
            aria-label="Volver"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
        )}
        <h1 className="text-2xl font-medium text-gray-800">{title}</h1>
      </div>

      {/* Contenedor para el nombre, rol y botón de logout */}
      <div className="flex items-center gap-4 w-full sm:w-auto justify-end">
        {showRecoveryButton && (
          <button
            onClick={() => navigate("/attendance-recovery")}
            className="hidden sm:flex items-center gap-2 bg-white border border-primary text-primary px-4 py-2 rounded-lg 
    hover:bg-primary hover:text-white hover:shadow-md active:scale-95 transition-all duration-300 
    text-sm font-semibold shadow-sm cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-5 h-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
              />
            </svg>
            Actualizar Asistencia
          </button>
        )}
        {user && (
          <div className="items-center gap-3 hidden md:flex">
            <span className="text-gray-800 font-bold tracking-wider">
              {`${user.first_name} ${user.last_name}`}
            </span>
            <span
              className={`px-2.5 py-1 uppercase text-xs font-semibold rounded-full ${roleBadgeStyles}`}
            >
              {user.role}
            </span>
          </div>
        )}
        <button
          onClick={logout}
          className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-opacity-90 transition-colors cursor-pointer text-sm whitespace-nowrap"
        >
          Cerrar Sesión
        </button>
      </div>

      {showRecoveryButton && (
        <button
          onClick={() => navigate("/attendance-recovery")}
          className="sm:hidden w-full flex justify-center items-center gap-2 bg-white border border-primary text-primary px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm font-semibold shadow-sm"
        >
          Actualizar Asistencia
        </button>
      )}
    </header>
  );
};

export default Header;
