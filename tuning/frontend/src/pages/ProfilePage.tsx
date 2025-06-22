// frontend/src/pages/ProfilePage.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // `Link` здесь не нужен, но `useNavigate` нужен

// Интерфейс для данных о заказе
interface IOrder {
  id: number;
  client: string;
  car: string;
  status: string;
  urgency: string;
  created_at: string;
  total_cost: number | null;
  performers: string[];
}

const ProfilePage: React.FC = () => {
    const { user } = useAuth();
    const [orders, setOrders] = useState<IOrder[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    // Выносим загрузку заказов в отдельную функцию, чтобы ее можно было переиспользовать
    const fetchOrders = () => {
        setLoading(true); // Показываем индикатор загрузки при каждом запросе
        axios.get('/api/v1/orders/')
            .then(response => {
                if (response.data && Array.isArray(response.data.results)) {
                    setOrders(response.data.results);
                } else if (Array.isArray(response.data)) {
                    setOrders(response.data);
                }
            })
            .catch(error => {
                console.error("Failed to fetch orders:", error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    // Загружаем заказы при первой загрузке страницы
    useEffect(() => {
        fetchOrders();
    }, []);

    // Функция для перехода на страницу создания заказа
    const handleAddOrderClick = () => {
        navigate('/orders/create');
    };

    // Функция для удаления заказа
    const handleDeleteOrder = async (orderId: number) => {
        if (window.confirm(`Вы уверены, что хотите удалить заказ #${orderId}?`)) {
            try {
                await axios.delete(`/api/v1/orders/${orderId}/`);
                // После успешного удаления перезагружаем список заказов, чтобы он обновился
                fetchOrders(); 
                alert('Заказ успешно удален!');
            } catch (error) {
                console.error("Failed to delete order:", error);
                alert('Ошибка при удалении заказа.');
            }
        }
    };

    const isAdmin = user?.roles.includes('Администратор');

    return (
        <div className="container mx-auto px-4 py-24 pt-40">
            <h1 className="text-4xl font-black mb-4">Личный кабинет</h1>
            {user && (
                <div className="bg-dark-card p-6 rounded-lg mb-8">
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Имя:</strong> {user.full_name}</p>
                    <p><strong>Роли:</strong> {user.roles.join(', ')}</p>
                </div>
            )}

            <div className="flex justify-between items-center mb-6">
                 <h2 className="text-3xl font-bold">
                    {isAdmin ? 'Все заказы' : 'Мои заказы'}
                </h2>
                {isAdmin && (
                    <button onClick={handleAddOrderClick} className="bg-primary-red text-white font-bold py-2 px-4 rounded-md hover:bg-red-700 transition-colors">
                        + Добавить заказ
                    </button>
                )}
            </div>
            
            <div className="bg-dark-card rounded-lg p-6">
                {loading ? (
                    <p>Загрузка заказов...</p>
                ) : orders.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-light-gray uppercase border-b border-white/10">
                                <tr>
                                    <th className="py-3 px-4">ID</th>
                                    <th className="py-3 px-4">Клиент</th>
                                    <th className="py-3 px-4">Авто</th>
                                    <th className="py-3 px-4">Статус</th>
                                    <th className="py-3 px-4">Исполнители</th>
                                    <th className="py-3 px-4">Стоимость</th>
                                    {isAdmin && <th className="py-3 px-4">Действия</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {orders.map(order => (
                                    <tr key={order.id} className="border-b border-white/10 hover:bg-white/5">
                                        <td className="py-3 px-4 font-bold">#{order.id}</td>
                                        <td className="py-3 px-4">{order.client}</td>
                                        <td className="py-3 px-4">{order.car}</td>
                                        <td className="py-3 px-4">{order.status}</td>
                                        <td className="py-3 px-4">{order.performers.join(', ')}</td>
                                        <td className="py-3 px-4">{order.total_cost ? `${new Intl.NumberFormat('ru-RU').format(order.total_cost)} руб.` : 'Не рассчитана'}</td>
                                        
                                        {/* Блок с кнопками "Редактировать" и "Удалить" */}
                                        {isAdmin && (
                                            <td className="py-3 px-4">
                                                <div className="flex items-center space-x-4">
                                                    <button 
                                                        onClick={() => navigate(`/orders/edit/${order.id}`)}
                                                        className="text-blue-400 hover:text-blue-300 text-xs font-semibold"
                                                    >
                                                        Редактировать
                                                    </button>
                                                    <button 
                                                        onClick={() => handleDeleteOrder(order.id)}
                                                        className="text-red-500 hover:text-red-400 text-xs font-semibold"
                                                    >
                                                        Удалить
                                                    </button>
                                                </div>
                                            </td>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p>Нет доступных заказов.</p>
                )}
            </div>
        </div>
    );
};

export default ProfilePage;