import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const RegisterPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await register({ email, password, full_name: fullName });
            navigate('/profile');
        } catch (error) {
            console.error('Failed to register', error);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <form onSubmit={handleSubmit} className="p-8 bg-dark-card rounded-lg shadow-lg w-full max-w-sm">
                <h2 className="text-2xl font-bold mb-6 text-center text-white">Регистрация</h2>
                <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Полное имя" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Пароль" required className="w-full p-3 mb-4 bg-dark-bg border border-white/20 rounded text-white"/>
                <button type="submit" className="w-full p-3 bg-primary-red rounded text-white font-bold">Зарегистрироваться</button>
                <p className="text-center mt-4 text-sm text-light-gray">Уже есть аккаунт? <Link to="/login" className="text-primary-red">Войти</Link></p>
            </form>
        </div>
    );
};

export default RegisterPage;