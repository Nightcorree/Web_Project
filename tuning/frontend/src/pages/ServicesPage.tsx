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
  const [categories, setCategories] = useState<IServiceCategory[]>([]);
  const [loading, setLoading] = useState(true);
  
  // --- НОВЫЕ СОСТОЯНИЯ ДЛЯ ФИЛЬТРОВ ---
  // Состояние для ID выбранной категории (пустая строка - 'Все')
  const [selectedCategory, setSelectedCategory] = useState<string>(''); 
  // Состояние для сортировки (пустая строка - 'По умолчанию')
  const [ordering, setOrdering] = useState<string>('');

  // Состояния для пагинации
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  // 1. Загрузка списка категорий (выполняется один раз)
  useEffect(() => {
    axios.get('/api/v1/service-categories/')
      .then(response => {
        setCategories(response.data);
      })
      .catch(error => console.error("Failed to fetch categories:", error));
  }, []);

  // 2. Загрузка списка УСЛУГ (выполняется при изменении фильтра, сортировки или страницы)
  useEffect(() => {
    setLoading(true);
    
    // Формируем URL с параметрами
    const params = new URLSearchParams({
        page: String(currentPage),
    });

    if (selectedCategory) {
        params.append('category', selectedCategory);
    }
    if (ordering) {
        params.append('ordering', ordering);
    }

    const url = `/api/v1/services/all/?${params.toString()}`;

    axios.get(url)
      .then(response => {
        setServices(response.data.results);
        setTotalPages(Math.ceil(response.data.count / 12)); // 12 - PAGE_SIZE из settings.py
      })
      .catch(error => console.error("Failed to fetch services:", error))
      .finally(() => setLoading(false));

    // Сбрасываем на первую страницу при изменении фильтров
  }, [selectedCategory, ordering, currentPage]);

  // Сбрасываем страницу на 1 при изменении фильтров
  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  // --- Рендеринг компонента ---
  return (
    <div className="bg-dark-bg">
      <div className="container mx-auto px-4 py-24 pt-40">
        <h1 className="text-5xl font-black text-white text-center mb-12 uppercase">
          Наши Услуги
        </h1>

        {/* --- ОСНОВНОЙ КОНТЕЙНЕР С РАЗДЕЛЕНИЕМ НА ФИЛЬТРЫ И КОНТЕНТ --- */}
        <div className="flex flex-col md:flex-row gap-8">

          {/* --- БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ --- */}
          <aside className="w-full md:w-1/4 lg:w-1/5">
            <div className="bg-dark-card p-6 rounded-lg sticky top-28">
              <h3 className="font-bold text-xl mb-4">Фильтры</h3>
              <div className="space-y-4">
                {/* Фильтр по категории */}
                <div>
                  <label htmlFor="category-filter" className="block text-sm font-medium text-light-gray mb-1">Категория</label>
                  <select
                    id="category-filter"
                    value={selectedCategory}
                    onChange={(e) => { setSelectedCategory(e.target.value); handleFilterChange(); }}
                    className="w-full p-2 bg-dark-bg border border-white/20 rounded text-white"
                  >
                    <option value="">Все категории</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Фильтр по цене (сортировка) */}
                <div>
                  <label htmlFor="ordering-filter" className="block text-sm font-medium text-light-gray mb-1">Цена</label>
                  <select
                    id="ordering-filter"
                    value={ordering}
                    onChange={(e) => { setOrdering(e.target.value); handleFilterChange(); }}
                    className="w-full p-2 bg-dark-bg border border-white/20 rounded text-white"
                  >
                    <option value="">По умолчанию</option>
                    <option value="base_price">Сначала дешевые</option>
                    <option value="-base_price">Сначала дорогие</option>
                  </select>
                </div>
              </div>
            </div>
          </aside>

          {/* --- КОНТЕНТ: СПИСОК УСЛУГ --- */}
          <main className="flex-grow">
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
                  onPageChange={setCurrentPage}
                />
              </>
            ) : (
              <p className="text-center text-white">Услуги по заданным критериям не найдены.</p>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default ServicesPage;