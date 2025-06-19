// frontend/src/pages/ServicesPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Pagination from '../components/Pagination'; // Наш компонент пагинации
import { Link } from 'react-router-dom';

interface IService {
  id: number;
  name: string;
  description: string;
  base_price: number;
}

const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<IService[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
    const fetchServices = async () => {
      setLoading(true);
      try {
        // Загружаем данные для ТЕКУЩЕЙ страницы
        const response = await axios.get(`http://127.0.0.1:8000/api/v1/services/all/?page=${currentPage}`);
        setServices(response.data.results);
        // Рассчитываем общее количество страниц
        const totalCount = response.data.count;
        setTotalPages(Math.ceil(totalCount / 12)); // 12 - это PAGE_SIZE из настроек Django
      } catch (error) {
        console.error("Failed to fetch services:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, [currentPage]); // Перезапрашиваем данные при изменении currentPage

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="bg-dark-bg">
      <div className="container mx-auto px-4 py-24 pt-40">
        <h1 className="text-5xl font-black text-white text-center mb-16 uppercase">
          Наши Услуги
        </h1>

        {loading ? (
          <p className="text-center text-white">Загрузка услуг...</p>
        ) : (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {services.map(service => (
                <Link to={`/service/${service.id}`} key={service.id} className="bg-dark-card p-6 group hover:border-primary-red/50 border border-transparent transition-all">
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary-red">{service.name}</h3>
                  <p className="text-light-gray text-sm mb-4 h-16 overflow-hidden">{service.description}</p>
                  <p className="text-primary-red font-bold text-lg">{new Intl.NumberFormat('ru-RU').format(service.base_price)} руб.</p>
                </Link>
              ))}
            </div>
            
            <Pagination 
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default ServicesPage;