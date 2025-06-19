// frontend/src/pages/SearchPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom';
import Pagination from '../components/Pagination';

interface IService {
  id: number;
  name: string;
  description: string;
  base_price: number;
}

const SearchPage: React.FC = () => {
  const [services, setServices] = useState<IService[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  useEffect(() => {
    if (!query) {
      setLoading(false);
      return;
    }

    const fetchResults = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/v1/services/all/?search=${query}&page=${currentPage}`);
        setServices(response.data.results);
        setTotalResults(response.data.count);
        setTotalPages(Math.ceil(response.data.count / 12)); // 12 - PAGE_SIZE
      } catch (error) {
        console.error("Failed to fetch search results:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query, currentPage]); // Перезапрос при изменении запроса или страницы

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="bg-dark-bg">
      <div className="container mx-auto px-4 py-24 pt-40">
        <h1 className="text-3xl md:text-5xl font-black text-white text-center mb-4 uppercase">
          Результаты поиска
        </h1>
        <p className="text-center text-light-gray mb-12">
          По запросу <span className="text-primary-red font-bold">"{query}"</span> найдено: {totalResults}
        </p>

        {loading ? (
          <p className="text-center text-white">Идет поиск...</p>
        ) : services.length > 0 ? (
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
        ) : (
          <p className="text-center text-white">По вашему запросу ничего не найдено.</p>
        )}
      </div>
    </div>
  );
};

export default SearchPage;