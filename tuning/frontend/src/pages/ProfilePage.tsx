import React from 'react';
import { useAuth } from '../context/AuthContext';

const ProfilePage: React.FC = () => {
    const { user } = useAuth();

    return (
        <div className="container mx-auto px-4 py-24 pt-40">
            <h1 className="text-4xl font-bold mb-4">Личный кабинет</h1>
            {user && (
                <div className="bg-dark-card p-6 rounded-lg">
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Имя:</strong> {user.full_name}</p>
                    <p><strong>Роли:</strong> {user.roles.join(', ')}</p>
                </div>
            )}
        </div>
    );
};

export default ProfilePage;