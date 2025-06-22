import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    // Если пользователя нет, перенаправляем на страницу входа
    return <Navigate to="/login" replace />;
  }

  // Если пользователь есть, показываем дочерний компонент (например, ProfilePage)
  return <Outlet />;
};

export default ProtectedRoute;