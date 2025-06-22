import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { AxiosError } from 'axios';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const [errors, setErrors] = useState<any>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({}); // Очищаем старые ошибки перед новым запросом
    try {
      await login({ email, password });
      navigate('/profile');
    } catch (error) {
      console.error('Failed to login', error);
      // --- 2. ОБРАБАТЫВАЕМ ОШИБКУ ---
      if (error instanceof AxiosError && error.response) {
        // Если это ошибка от Axios с ответом сервера, сохраняем ее
        setErrors(error.response.data);
      } else {
        // Для других ошибок (например, нет сети)
        setErrors({ non_field_errors: ['Произошла неизвестная ошибка.'] });
      }
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <form onSubmit={handleSubmit} className="p-8 bg-dark-card rounded-lg shadow-lg w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-6 text-center text-white">Вход</h2>
        
        {/* --- 3. ОТОБРАЖАЕМ ОБЩИЕ ОШИБКИ ФОРМЫ --- */}
        {errors.non_field_errors && (
          <div className="bg-red-500/20 p-3 rounded mb-4 text-red-400 text-sm">
            {errors.non_field_errors.join(' ')}
          </div>
        )}

        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Пароль" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
        
        <button type="submit" className="w-full p-3 bg-primary-red rounded text-white font-bold">Войти</button>
        <p className="text-center mt-4 text-sm text-light-gray">Нет аккаунта? <Link to="/register" className="text-primary-red">Зарегистрироваться</Link></p>
      </form>
    </div>
  );
};

export default LoginPage;