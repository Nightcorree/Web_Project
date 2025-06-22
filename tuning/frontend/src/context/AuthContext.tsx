import React, { createContext, useState, useContext, useEffect, type ReactNode } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/v1/';

interface User {
  id: number;
  email: string;
  full_name: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      axios.get(API_URL + 'users/me/')
        .then(response => setUser(response.data))
        .catch(() => {
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (data: any) => {
    try {
      const response = await axios.post(API_URL + 'auth/login/', data);
      const { key } = response.data;
      localStorage.setItem('token', key);
      axios.defaults.headers.common['Authorization'] = `Token ${key}`;
      const userResponse = await axios.get(API_URL + 'users/me/');
      setUser(userResponse.data);
      // Возвращаем успех (можно ничего не возвращать)
      return Promise.resolve(); 
    } catch (error) {
      // --- ИЗМЕНЕНИЕ ---
      // Если произошла ошибка, пробрасываем ее дальше
      return Promise.reject(error);
    }
  };

  const register = async (data: any) => {
    try {
      // Для регистрации нам не нужен ответ, мы просто логинимся после
      await axios.post(API_URL + 'auth/registration/', data);
      // После успешной регистрации сразу пытаемся войти
      await login({ email: data.email, password: data.password });
       // Возвращаем успех
      return Promise.resolve();
    } catch (error) {
      // --- ИЗМЕНЕНИЕ ---
      // Если произошла ошибка, пробрасываем ее дальше
      return Promise.reject(error);
    }
  };

  const logout = () => {
    axios.post(API_URL + 'auth/logout/').finally(() => {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    });
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};