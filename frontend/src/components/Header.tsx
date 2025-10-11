import { useAuth } from "../hooks/useAuth";

interface HeaderProps {
    title: string;
    showBackButton?: boolean;
    onBack?: () => void;
}

const Header = ({ title, showBackButton = false, onBack }: HeaderProps) => {
  const { logout } = useAuth();

  return (
    <header className="bg-white shadow-sm p-4 mb-8 flex justify-between items-center">
      <div className="flex items-center gap-4">
        {showBackButton && (
          <button
            onClick={onBack}
            className="p-2 rounded-full hover:bg-gray-200 transition-colors"
            aria-label="Volver"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
        <h1 className="text-2xl font-medium text-gray-800">{title}</h1>
      </div>
      <button
        onClick={logout}
        className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-opacity-90 transition-colors cursor-pointer"
      >
        Cerrar Sesión
      </button>
    </header>
  );
};

export default Header;