import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ email, password });
      navigate('/profile');
    } catch (error) {
      console.error('Failed to login', error);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <form onSubmit={handleSubmit} className="p-8 bg-dark-card rounded-lg shadow-lg w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-6 text-center text-white">Вход</h2>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Пароль" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
        <button type="submit" className="w-full p-3 bg-primary-red rounded text-white font-bold">Войти</button>
        <p className="text-center mt-4 text-sm text-light-gray">Нет аккаунта? <Link to="/register" className="text-primary-red">Зарегистрироваться</Link></p>
      </form>
    </div>
  );
};

export default LoginPage;