import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { AxiosError } from 'axios';

const RegisterPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();
    const [errors, setErrors] = useState<any>({}); 

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({}); // Очищаем старые ошибки
        try {
            await register({ email, password, full_name: fullName });
            navigate('/profile');
        } catch (error) {
            console.error('Failed to register', error);
            // <-- 2. Обрабатываем ошибку
            if (error instanceof AxiosError && error.response) {
                setErrors(error.response.data);
            } else {
                setErrors({ detail: ['Произошла неизвестная ошибка. Попробуйте позже.'] });
            }
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <form onSubmit={handleSubmit} className="p-8 bg-dark-card rounded-lg shadow-lg w-full max-w-sm">
                <h2 className="text-2xl font-bold mb-6 text-center text-white">Регистрация</h2>
                
                {/* 3. Отображаем ошибки */}
                {errors.detail && <p className="text-red-400 text-sm mb-2">{errors.detail}</p>}
                
                <div className="mb-4">
                  <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Полное имя" required className="w-full p-3 bg-dark-bg border border-white/20 rounded text-white"/>
                  {errors.full_name && <p className="text-red-400 text-xs mt-1">{errors.full_name.join(' ')}</p>}
                </div>
                
                <div className="mb-4">
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required className="w-full p-3 bg-dark-bg border border-white/20 rounded text-white"/>
                  {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email.join(' ')}</p>}
                </div>

                <div className="mb-4">
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Пароль" required className="w-full p-3 bg-dark-bg border border-white/20 rounded text-white"/>
                  {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.join(' ')}</p>}
                </div>
                
                <button type="submit" className="w-full p-3 bg-primary-red rounded text-white font-bold">Зарегистрироваться</button>
                <p className="text-center mt-4 text-sm text-light-gray">Уже есть аккаунт? <Link to="/login" className="text-primary-red">Войти</Link></p>
            </form>
        </div>
    );
};

export default RegisterPage;