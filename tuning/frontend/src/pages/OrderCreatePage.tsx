// frontend/src/pages/OrderCreatePage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Интерфейсы для данных
interface SelectOption { id: number; name: string; }
interface CarOption { id: number; display_name: string; }
interface ServiceOption extends SelectOption { base_price: number; }
interface OrderItemState {
    service_id: number;
    service_name: string;
    item_price: number;
    quantity: number;
    item_comment: string;
}

const OrderCreatePage: React.FC = () => {
    // --- Состояния формы ---
    const [client, setClient] = useState('');
    const [car, setCar] = useState('');
    const [status, setStatus] = useState('');
    const [urgency, setUrgency] = useState('NRM');
    const [plannedDate, setPlannedDate] = useState('');
    const [clientComment, setClientComment] = useState('');
    const [performer, setPerformer] = useState(''); // Был массив 'performers', стал строка 'performer'
    const [orderItems, setOrderItems] = useState<OrderItemState[]>([]);
    const [totalCost, setTotalCost] = useState(0);

    // --- Состояния для списков ---
    const [clientList, setClientList] = useState<SelectOption[]>([]);
    const [carList, setCarList] = useState<CarOption[]>([]);
    const [statusList, setStatusList] = useState<SelectOption[]>([]);
    const [performerList, setPerformerList] = useState<SelectOption[]>([]);
    const [serviceList, setServiceList] = useState<ServiceOption[]>([]);
    
    const navigate = useNavigate();

    useEffect(() => {
        const fetchInitialData = async () => {
            const [clientsRes, statusesRes, performersRes, servicesRes] = await Promise.all([
                axios.get('/api/v1/form-data/clients/'),
                axios.get('/api/v1/form-data/statuses/'),
                axios.get('/api/v1/form-data/performers/'),
                axios.get('/api/v1/form-data/services/'),
            ]);
            setClientList(clientsRes.data.map((c: any) => ({ id: c.id, name: c.full_name })));
            setStatusList(statusesRes.data);
            setPerformerList(performersRes.data.map((p: any) => ({ id: p.id, name: p.full_name })));
            setServiceList(servicesRes.data);
            if (statusesRes.data.length > 0) {
                setStatus(statusesRes.data[0].id);
            }
        };
        fetchInitialData().catch(console.error);
    }, []);

    useEffect(() => {
        if (client) {
            axios.get(`/api/v1/form-data/cars/?owner_id=${client}`)
                .then(res => setCarList(res.data.map((c: any) => ({ id: c.id, display_name: c.display_name }))));
        } else {
            setCarList([]);
        }
        setCar('');
    }, [client]);

    useEffect(() => {
        const cost = orderItems.reduce((sum, item) => sum + item.item_price * item.quantity, 0);
        setTotalCost(cost);
    }, [orderItems]);

    const addService = (serviceId: string) => {
        if (!serviceId || orderItems.find(item => item.service_id === +serviceId)) return;
        const service = serviceList.find((s: ServiceOption) => s.id === +serviceId);
        if (service) {
            setOrderItems([...orderItems, { service_id: service.id, service_name: service.name, item_price: service.base_price, quantity: 1, item_comment: '' }]);
        }
    };

    const removeService = (serviceIdToRemove: number) => {
        setOrderItems(prev => prev.filter(item => item.service_id !== serviceIdToRemove));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const payload = {
            client: client,
            car: car,
            status: status,
            urgency: urgency,
            planned_completion_date: plannedDate || null,
            client_comment: clientComment,
            performer_id: performer ? parseInt(performer) : null, // Отправляем performer_id
            order_items: orderItems.map(item => ({
                service_id: item.service_id,
                item_price: item.item_price,
                quantity: item.quantity,
                item_comment: item.item_comment
            })),
        };
        try {
            await axios.post('/api/v1/orders/create/', payload);
            alert('Заказ успешно создан!');
            navigate('/profile');
        } catch (error: any) {
            console.error("Failed to create order:", error);
            const errorData = error.response?.data;
            const errorString = JSON.stringify(errorData, null, 2);
            alert(`Ошибка при создании заказа:\n${errorString}`);
        }
    };

    return (
        <div className="container mx-auto px-4 py-24 pt-40">
            <h1 className="text-4xl font-black mb-8">Создание нового заказа</h1>
            <form onSubmit={handleSubmit} className="bg-dark-card p-8 rounded-lg space-y-6">
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div>
                        <label className="block mb-2 text-sm font-bold">Клиент</label>
                        <select value={client} onChange={(e) => setClient(e.target.value)} required className="w-full p-3 bg-dark-bg border border-white/20 rounded">
                            <option value="">Выберите клиента</option>
                            {clientList.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block mb-2 text-sm font-bold">Автомобиль</label>
                        <select value={car} onChange={(e) => setCar(e.target.value)} required disabled={!client} className="w-full p-3 bg-dark-bg border border-white/20 rounded disabled:opacity-50">
                            <option value="">{client ? "Выберите автомобиль" : "Сначала выберите клиента"}</option>
                            {carList.map(c => <option key={c.id} value={c.id}>{c.display_name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block mb-2 text-sm font-bold">Статус</label>
                        <select value={status} onChange={(e) => setStatus(e.target.value)} required className="w-full p-3 bg-dark-bg border border-white/20 rounded">
                            {statusList.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block mb-2 text-sm font-bold">Срочность</label>
                        <select value={urgency} onChange={(e) => setUrgency(e.target.value)} className="w-full p-3 bg-dark-bg border border-white/20 rounded">
                            <option value="NRM">Обычная</option>
                            <option value="URG">Срочная</option>
                            <option value="VUR">Очень срочная</option>
                        </select>
                    </div>
                    <div>
                        <label className="block mb-2 text-sm font-bold">Планируемая дата завершения</label>
                        <input type="date" value={plannedDate} onChange={(e) => setPlannedDate(e.target.value)} className="w-full p-3 bg-dark-bg border border-white/20 rounded" />
                    </div>
                    {/* Поле выбора исполнителя */}
                    <div>
                        <label className="block mb-2 text-sm font-bold">Исполнитель</label>
                        <select value={performer} onChange={(e) => setPerformer(e.target.value)} className="w-full p-3 bg-dark-bg border border-white/20 rounded">
                            <option value="">Не назначен</option>
                            {performerList.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block mb-2 text-sm font-bold">Комментарий клиента</label>
                    <textarea value={clientComment} onChange={(e) => setClientComment(e.target.value)} rows={3} className="w-full p-3 bg-dark-bg border border-white/20 rounded"></textarea>
                </div>
                
                <div>
                    <label className="block mb-2 text-sm font-bold">Добавить услугу в заказ</label>
                    <select onChange={(e) => { addService(e.target.value); e.target.value = ''; }} value="" className="w-full p-3 bg-dark-bg border border-white/20 rounded">
                        <option value="">Выберите услугу...</option>
                        {serviceList.map(s => <option key={s.id} value={s.id}>{s.name} ({new Intl.NumberFormat('ru-RU').format(s.base_price)} руб.)</option>)}
                    </select>
                </div>
                
                <div className="space-y-2">
                    <h3 className="font-bold">Позиции заказа:</h3>
                    {orderItems.length > 0 ? orderItems.map(item => (
                        <div key={item.service_id} className="flex justify-between items-center bg-dark-bg p-3 rounded">
                            <span>{item.service_name}</span>
                            <div className="flex items-center gap-4">
                                <span>{new Intl.NumberFormat('ru-RU').format(item.item_price)} руб. x {item.quantity}</span>
                                <button type="button" onClick={() => removeService(item.service_id)} className="text-red-500 hover:text-red-400 font-bold text-lg">×</button>
                            </div>
                        </div>
                    )) : <p className="text-sm text-light-gray">Услуги не добавлены.</p>}
                </div>

                <div className="text-right text-2xl font-bold">
                    Итого: {new Intl.NumberFormat('ru-RU').format(totalCost)} руб.
                </div>

                <button type="submit" className="w-full p-3 bg-primary-red rounded text-white font-bold text-lg hover:bg-red-700 transition-colors">
                    Создать заказ
                </button>
            </form>
        </div>
    );
};

export default OrderCreatePage;