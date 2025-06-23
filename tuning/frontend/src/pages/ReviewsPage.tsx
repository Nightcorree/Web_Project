// frontend/src/pages/ReviewsPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { FaStar, FaPlus, FaTimes } from 'react-icons/fa';

// Интерфейсы для данных
interface IReview {
    id: number;
    user: string;
    user_id: number;
    order_info: string;
    rating: number;
    review_text: string;
    review_date: string;
}

interface IOrderForReview {
    id: number;
    car: string;
    created_at: string;
}

const ReviewsPage: React.FC = () => {
    const { user } = useAuth();
    const [reviews, setReviews] = useState<IReview[]>([]);
    const [averageRating, setAverageRating] = useState(0);
    const [loading, setLoading] = useState(true);
    
    // --- НОВОЕ СОСТОЯНИЕ ДЛЯ УПРАВЛЕНИЯ ВИДИМОСТЬЮ ФОРМЫ ---
    const [isFormVisible, setIsFormVisible] = useState(false);

    // Состояния для формы добавления отзыва
    const [ordersForReview, setOrdersForReview] = useState<IOrderForReview[]>([]);
    const [selectedOrder, setSelectedOrder] = useState('');
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [formError, setFormError] = useState('');

    const fetchReviews = useCallback(async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/v1/reviews/');
            setReviews(response.data.reviews);
            setAverageRating(response.data.average_rating);
        } catch (error) {
            console.error("Failed to fetch reviews:", error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchReviews();
        if (user) {
            axios.get('/api/v1/form-data/my-orders-for-review/')
                .then(res => {
                    // ИСПРАВЛЕНИЕ: Правильно обрабатываем ответ с пагинацией или без
                    if (res.data && Array.isArray(res.data.results)) {
                        setOrdersForReview(res.data.results);
                    } else if (Array.isArray(res.data)) {
                        setOrdersForReview(res.data);
                    }
                })
                .catch(err => console.error("Failed to fetch orders for review:", err));
        }
    }, [user, fetchReviews]);

    const handleAddReview = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedOrder) {
            setFormError('Пожалуйста, выберите заказ.');
            return;
        }
        setFormError('');
        
        try {
            await axios.post('/api/v1/reviews/', {
                order: selectedOrder,
                rating: rating,
                review_text: comment
            });
            // Обновляем список отзывов и сбрасываем форму
            fetchReviews();
            setComment('');
            setRating(10);
            setSelectedOrder('');
            setIsFormVisible(false); // Закрываем форму после успешной отправки
            // Обновляем список доступных для отзыва заказов
            setOrdersForReview(orders => orders.filter(o => o.id !== +selectedOrder));
        } catch (error: any) {
            const errorMsg = error.response?.data?.order?.[0] || 'Произошла ошибка при добавлении отзыва.';
            setFormError(errorMsg);
            console.error("Failed to add review:", error);
        }
    };
    
    const handleDeleteReview = async (reviewId: number) => {
        if (window.confirm('Вы уверены, что хотите удалить этот отзыв?')) {
            try {
                await axios.delete(`/api/v1/reviews/${reviewId}/`);
                fetchReviews(); // Обновляем список
            } catch (error) {
                console.error("Failed to delete review:", error);
                alert('Не удалось удалить отзыв.');
            }
        }
    };

    return (
        <div className="bg-dark-bg text-white">
            <div className="container mx-auto px-4 py-24 pt-40">
                <h1 className="text-5xl font-black text-white text-center mb-4 uppercase">
                    Отзывы клиентов
                </h1>

                {/* Блок со средним рейтингом */}
                <div className="flex justify-center items-center gap-4 mb-12">
                    <FaStar className="text-yellow-400" size={32} />
                    <span className="text-3xl font-bold">{averageRating} / 5</span>
                    <span className="text-light-gray">Средний рейтинг на основе {reviews.length} отзывов</span>
                </div>

                {/* Блок с кнопкой и формой (только для авторизованных) */}
                {user && (
                    <div className="max-w-2xl mx-auto mb-12">
                        {/* Показываем кнопку или форму в зависимости от состояния isFormVisible */}
                        {!isFormVisible ? (
                            <button
                                onClick={() => setIsFormVisible(true)}
                                className="w-full p-4 bg-primary-red font-bold rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2 text-lg"
                            >
                                <FaPlus /> Оставить отзыв
                            </button>
                        ) : (
                            <div className="bg-dark-card p-6 rounded-lg">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-2xl font-bold">Оставить отзыв</h3>
                                    <button onClick={() => setIsFormVisible(false)} className="text-light-gray hover:text-white">
                                        <FaTimes size={20} />
                                    </button>
                                </div>
                                <form onSubmit={handleAddReview} className="space-y-4">
                                    <div>
                                        <label htmlFor="order-select" className="block text-sm font-bold mb-2">Выберите выполненный заказ</label>
                                        <select 
                                            id="order-select" 
                                            value={selectedOrder} 
                                            onChange={e => setSelectedOrder(e.target.value)}
                                            className="w-full p-3 bg-dark-bg border border-white/20 rounded"
                                        >
                                            <option value="">-- Выберите заказ --</option>
                                            {ordersForReview.length > 0 ? (
                                                ordersForReview.map(order => (
                                                    <option key={order.id} value={order.id}>
                                                        Заказ #{order.id} ({order.car}) от {new Date(order.created_at).toLocaleDateString()}
                                                    </option>
                                                ))
                                            ) : (
                                                <option disabled>Нет заказов, доступных для отзыва</option>
                                            )}
                                        </select>
                                    </div>
                                    <div>
                                        <label htmlFor="rating-select" className="block text-sm font-bold mb-2">Ваша оценка</label>
                                        <select 
                                            id="rating-select" 
                                            value={rating} 
                                            onChange={e => setRating(Number(e.target.value))}
                                            className="w-full p-3 bg-dark-bg border border-white/20 rounded"
                                        >
                                            {[...Array(5).keys()].map(i => (
                                                <option key={i + 1} value={i + 1}>{i + 1}</option>
                                            )).reverse()}
                                        </select>
                                    </div>
                                    <div>
                                        <label htmlFor="comment-text" className="block text-sm font-bold mb-2">Комментарий</label>
                                        <textarea
                                            id="comment-text"
                                            rows={4}
                                            value={comment}
                                            onChange={e => setComment(e.target.value)}
                                            className="w-full p-3 bg-dark-bg border border-white/20 rounded"
                                            placeholder="Поделитесь вашими впечатлениями..."
                                        ></textarea>
                                    </div>
                                    {formError && <p className="text-red-400 text-sm">{formError}</p>}
                                    <button type="submit" className="w-full p-3 bg-primary-red font-bold rounded hover:bg-red-700 transition-colors">
                                        Отправить отзыв
                                    </button>
                                </form>
                            </div>
                        )}
                    </div>
                )}


                {/* Список отзывов */}
                <div className="space-y-6">
                    {loading ? (
                        <p className="text-center">Загрузка отзывов...</p>
                    ) : (
                        reviews.map(review => (
                            <div key={review.id} className="bg-dark-card p-6 rounded-lg">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <p className="font-bold text-lg">{review.user}</p>
                                        <p className="text-sm text-light-gray">{review.order_info}</p>
                                    </div>
                                    <div className="flex items-center gap-2 text-yellow-400">
                                        <FaStar />
                                        <span className="text-lg font-bold text-white">{review.rating}</span>
                                    </div>
                                </div>
                                <p className="mt-4 text-light-gray">{review.review_text}</p>
                                <div className="flex justify-between items-center mt-4 pt-4 border-t border-white/10">
                                    <p className="text-xs text-light-gray/50">
                                        {new Date(review.review_date).toLocaleString()}
                                    </p>
                                    {/* Кнопки управления (только для владельца или админа) */}
                                    {(user && (user.id === review.user_id || user.roles.includes('Администратор'))) && (
                                        <div className="flex gap-4">
                                            {/* <button className="text-blue-400 hover:text-blue-300 text-xs font-semibold">Редактировать</button> */}
                                            <button 
                                                onClick={() => handleDeleteReview(review.id)}
                                                className="text-red-500 hover:text-red-400 text-xs font-semibold"
                                            >
                                                Удалить
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>

            </div>
        </div>
    );
};

export default ReviewsPage;