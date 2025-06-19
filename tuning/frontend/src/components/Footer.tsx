// frontend/src/components/Footer.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { FaVk, FaEnvelope } from 'react-icons/fa';

interface IService {
    id: number;
    name: string;
}

const Footer: React.FC = () => {
    const [services, setServices] = useState<IService[]>([]);

    useEffect(() => {
        // Используем пагинированный URL
        axios.get('http://127.0.0.1:8000/api/v1/services/all/')
            .then(response => {
                // --- ГЛАВНОЕ ИЗМЕНЕНИЕ ---
                // Проверяем, что в ответе есть поле 'results' и оно является массивом
                if (response.data && Array.isArray(response.data.results)) {
                    // Берем массив из поля 'results' и уже у него вызываем slice
                    setServices(response.data.results.slice(0, 8));
                }
            })
            .catch(error => console.error("Failed to fetch services for footer:", error));
    }, []);

    // ... остальная часть компонента без изменений ...
    return (
        <footer className="bg-dark-card text-white">
            <div className="container mx-auto px-4 pt-16 pb-8">
                <div className="flex flex-col md:flex-row justify-between items-start gap-12">
                    <div className="space-y-4 w-full md:w-1/4">
                        <Link to="/" className="flex items-center space-x-2">
                            <span className="text-2xl font-black">Slick Auto</span>
                        </Link>
                        <p className="text-light-gray text-sm">
                            Полный спектр услуг по автотюнингу в Москве
                        </p>
                        <a href="#" className="text-light-gray hover:text-white transition-colors">
                            <FaVk size={24} />
                        </a>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-8 md:gap-16 text-sm">
                        <div>
                            <h4 className="font-bold text-lg mb-4 uppercase">Услуги</h4>
                            <ul className="space-y-2 text-light-gray grid grid-cols-2 gap-x-8">
                                {services.map(service => (
                                    <li key={service.id}>
                                        <Link to={`/services/${service.id}`} className="hover:text-primary-red transition-colors">{service.name}</Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-bold text-lg mb-4 uppercase">О нас</h4>
                            <ul className="space-y-2 text-white font-bold">
                                <li><Link to="/portfolio" className="hover:text-primary-red transition-colors">НАШИ РАБОТЫ</Link></li>
                                <li><Link to="/actions" className="hover:text-primary-red transition-colors">АКЦИИ</Link></li>
                                <li><Link to="/blog" className="hover:text-primary-red transition-colors">СТАТЬИ</Link></li>
                                <li><Link to="/contacts" className="hover:text-primary-red transition-colors">КОНТАКТЫ</Link></li>
                            </ul>
                        </div>
                    </div>
                    <div className="w-full md:w-1/4 flex justify-start md:justify-end">
                        <a href="mailto:info@tuning.ru" className="flex items-center space-x-2 text-light-gray hover:text-white">
                            <FaEnvelope className="text-primary-red" size={18} />
                            <span>INFO@TUNING.RU</span>
                        </a>
                    </div>
                </div>
                <div className="border-t border-white/10 mt-12 pt-6 text-xs text-light-gray/50">
                    <p>
                        Все материалы данного сайта являются объектами авторского права (в том числе дизайн). Запрещается копирование, распространение (в том числе путем копирования на другие сайты и ресурсы в Интернете) или любое иное использование информации и объектов без предварительного согласия правообладателя.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;