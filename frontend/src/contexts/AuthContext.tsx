// src/contexts/AuthContext.tsx
import { createContext, useState, useEffect, type ReactNode, type FC } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

// 1. Definimos un tipo para el perfil del usuario
interface UserProfile {
  id: string;
  email: string;
  role: 'student' | 'teacher';
  first_name: string;
  last_name: string;
  cui?: string; // CUI solo para estudiantes
}

interface LoginCredentials {
  email: string;
  pass: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserProfile | null; // 2. Añadimos el usuario al contexto
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => !!localStorage.getItem('authToken'));
  const [user, setUser] = useState<UserProfile | null>(null); // 3. Estado para el perfil
  const navigate = useNavigate();

  // 4. useEffect para obtener el perfil del usuario si hay un token al cargar la app
  useEffect(() => {
    const fetchUserProfile = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const response = await api.get('/auth/profile');
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Token inválido o expirado, cerrando sesión.', error);
          logout(); // Limpia el token inválido
        }
      }
    };

    fetchUserProfile();
  }, []);


  const login = async ({ email, pass }: LoginCredentials): Promise<void> => {
    try {
      const response = await api.post('/auth/login', { email, password: pass });

      if (response.data && response.data.token) {
        const { token } = response.data;
        localStorage.setItem('authToken', token);
        
        // Después de guardar el token, obtenemos el perfil del usuario
        const profileResponse = await api.get('/auth/profile');
        setUser(profileResponse.data);
        setIsAuthenticated(true);
        navigate('/dashboard');
      }
    } catch (error: any) {
      console.error('Error de inicio de sesión:', error);
      const errorMessage = error.response?.data?.message || 'Error en el servidor.';
      throw new Error(errorMessage);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    setUser(null); // 5. Limpiamos el usuario al cerrar sesión
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};