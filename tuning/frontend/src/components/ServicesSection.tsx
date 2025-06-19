// frontend/src/components/ServicesSection.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaCarSide, FaPaintRoller, FaWind, FaScrewdriver, FaCarCrash } from 'react-icons/fa';
import { Link } from 'react-router-dom'; // <-- 1. Убедимся, что Link импортирован

interface IServiceCategory {
  id: number;
  name: string;
}

const icons = [
  FaCarCrash, FaPaintRoller, FaWind, FaScrewdriver, FaCarCrash, 
  FaPaintRoller, FaWind, FaScrewdriver, FaCarCrash, FaPaintRoller
];

const ServicesSection: React.FC = () => {
  const [categories, setCategories] = useState<IServiceCategory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/v1/service-categories/')
      .then(response => {
        setCategories(response.data);
      })
      .catch(error => console.error("Failed to fetch service categories:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="bg-dark-bg py-24">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl md:text-5xl font-black text-white text-center mb-20 uppercase">
          Услуги нашего центра
        </h2>
        
        {loading ? (
            <p className="text-center text-white">Загрузка...</p>
        ) : (
            <> {/* Оборачиваем в фрагмент, чтобы добавить кнопку после сетки */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-6 gap-y-12">
                {categories.map((category, index) => {
                    const IconComponent = icons[index] || FaCarSide;

                    return (
                    <Link to={`/services/category/${category.id}`} key={category.id} className="text-center text-light-gray cursor-pointer group flex flex-col items-center">
                        <div className="relative w-20 h-20 mb-5 flex items-center justify-center">
                          <div className="absolute inset-0 bg-primary-red/10 rounded-full group-hover:bg-primary-red/20 transition-all duration-300 transform scale-150"></div>
                          <IconComponent size={36} className="text-primary-red z-10"/>
                        </div>
                        <p className="font-semibold uppercase text-sm leading-tight group-hover:text-white transition-colors h-12 flex items-center text-center">
                          {category.name}
                        </p>
                    </Link>
                    );
                })}
                </div>

                {/* --- 2. ДОБАВЛЯЕМ КНОПКУ ЗДЕСЬ --- */}
                <div className="text-center mt-16">
                    <Link 
                        to="/services" 
                        className="bg-primary-red text-white font-bold py-3 px-10 rounded-md hover:bg-red-700 transition-colors text-lg"
                    >
                        Все услуги
                    </Link>
                </div>
            </>
        )}
      </div>
    </section>
  );
};

export default ServicesSection;