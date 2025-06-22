// frontend/src/pages/ServicesPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Pagination from '../components/Pagination';
import { Link } from 'react-router-dom';

// Интерфейсы для наших данных
interface IService {
  id: number;
  name: string;
  description: string;
  base_price: number;
}

interface IServiceCategory {
  id: number;
  name: string;
}

const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<IService[]>([]);
  const [categories, setCategories] = useState<IServiceCategory[]>([]); // Состояние для категорий
  const [loading, setLoading] = useState(true);
  
  // Состояния для фильтра и пагинации
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null); // ID выбранной категории
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  // 1. Загрузка списка категорий (выполняется один раз)
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/v1/service-categories/')
      .then(response => {
        setCategories(response.data);
      })
      .catch(error => console.error("Failed to fetch categories:", error));
  }, []);

  // 2. Загрузка списка УСЛУГ (выполняется при изменении фильтра или страницы)
  useEffect(() => {
    setLoading(true);
    // Формируем URL с параметрами
    let url = `http://127.0.0.1:8000/api/v1/services/all/?page=${currentPage}`;
    if (selectedCategory) {
      url += `&category=${selectedCategory}`;
    }

    axios.get(url)
      .then(response => {
        setServices(response.data.results);
        setTotalPages(Math.ceil(response.data.count / 12)); // 12 - PAGE_SIZE
      })
      .catch(error => console.error("Failed to fetch services:", error))
      .finally(() => setLoading(false));

  }, [selectedCategory, currentPage]); // Перезапрос при изменении этих состояний

  // 3. Функции для обработки кликов
  const handleCategoryClick = (categoryId: number | null) => {
    setSelectedCategory(categoryId);
    setCurrentPage(1); // Сбрасываем на первую страницу при смене фильтра
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // --- Рендеринг компонента ---
  return (
    <div className="bg-dark-bg">
      <div className="container mx-auto px-4 py-24 pt-40">
        <h1 className="text-5xl font-black text-white text-center mb-8 uppercase">
          Наши Услуги
        </h1>

        {/* 4. Блок с кнопками фильтров */}
        <div className="flex justify-center flex-wrap gap-2 mb-12">
          <button
            onClick={() => handleCategoryClick(null)}
            className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${
              selectedCategory === null
                ? 'bg-primary-red text-white'
                : 'bg-dark-card text-light-gray hover:bg-primary-red/50'
            }`}
          >
            Все услуги
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => handleCategoryClick(category.id)}
              className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${
                selectedCategory === category.id
                  ? 'bg-primary-red text-white'
                  : 'bg-dark-card text-light-gray hover:bg-primary-red/50'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* 5. Отображение услуг и пагинации */}
        {loading ? (
          <p className="text-center text-white">Загрузка услуг...</p>
        ) : services.length > 0 ? (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {services.map(service => (
                <Link to={`/service/${service.id}`} key={service.id} className="bg-dark-card p-6 group hover:border-primary-red/50 border border-transparent transition-all">
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary-red">{service.name}</h3>
                  <p className="text-light-gray text-sm mb-4 h-16 overflow-hidden">{service.description || 'Описание отсутствует.'}</p>
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
        ) : (
          <p className="text-center text-white">Услуги в данной категории не найдены.</p>
        )}
      </div>
    </div>
  );
};

export default ServicesPage;