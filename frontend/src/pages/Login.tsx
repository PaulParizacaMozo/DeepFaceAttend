import { useState, type FormEvent } from 'react';
import { useAuth } from '../hooks/useAuth';
import unsaBgURL from '../assets/unsa_bg2.avif';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError(''); // Limpiar errores previos
    const success = login(email, password);
    if (!success) {
      setError('Correo electrónico o contraseña incorrectos.');
    }
  };

  return (
    <div className="relative min-h-screen w-full">
      {/* Capa 1: Fondo con imagen */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${unsaBgURL})` }}
      ></div>

      {/* Capa 2: Superposición con opacidad y desenfoque */}
      <div className="absolute inset-0 bg-gray-400/60 backdrop-blur-sm"></div>

      {/* Capa 3: Contenido centrado */}
      <div className="relative flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-md space-y-8 rounded-2xl bg-white/90 p-6 shadow-2xl ring-1 ring-black/5 sm:p-10">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">
              Control de Asistencia
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Inicia sesión para continuar
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Campo de Email */}
            <div>
              <label
                htmlFor="email-address"
                className="block text-sm font-medium text-gray-700"
              >
                Correo Electrónico
              </label>
              <div className="mt-1">
                <input
                  id="email-address"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="block w-full appearance-none rounded-lg border border-gray-300 px-3 py-2.5 placeholder-gray-400 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm"
                  placeholder="ejemplo@unsa.edu.pe"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            {/* Campo de Contraseña */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                Contraseña
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="block w-full appearance-none rounded-lg border border-gray-300 px-3 py-2.5 placeholder-gray-400 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <p className="text-center text-sm text-red-600">{error}</p>
            )}

            {/* Botón de envío */}
            <div>
              <button
                type="submit"
                className="flex w-full justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 cursor-pointer"
              >
                Iniciar Sesión
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Pie de página con el texto de la UNSA */}
      <footer className="absolute bottom-4 right-6 text-xs text-gray-100/80">
        <p>Plataforma desarrollada para la UNSA</p>
      </footer>
    </div>
  );
};

export default Login;
