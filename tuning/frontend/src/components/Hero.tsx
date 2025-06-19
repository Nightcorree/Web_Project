// frontend/src/components/Hero.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // <-- 1. Импортируем хук

const Hero: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState(''); // <-- 2. Состояние для поискового запроса
  const navigate = useNavigate(); // <-- 3. Хук для навигации

  // 4. Функция для обработки отправки формы
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Предотвращаем стандартную перезагрузку страницы
    if (searchQuery.trim()) {
      // Переходим на страницу результатов, передавая запрос в URL
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <section
      className="relative bg-dark-bg text-white flex items-center overflow-hidden mt-20"
    >
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-2xl"> {/* Немного увеличим ширину блока */}
          <h1 className="text-6xl md:text-8xl font-black uppercase leading-none pt-9">
            Тюнинг ателье
          </h1>
          <h2 className="text-6xl md:text-8xl font-black uppercase text-primary-red leading-none mt-2">
            Slick Auto
          </h2>
          <p className="mt-6 text-lg text-light-gray max-w-md">
            Выполняем полный спектр услуг по тюнингу Вашего автомобиля. Быстро, качественно, за разумную цену!
          </p>

          {/* --- 5. ДОБАВЛЯЕМ ФОРМУ ПОИСКА --- */}
          <form onSubmit={handleSearchSubmit} className="mt-8 mb-6 flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Найти услугу, например, 'полировка фар'"
              className="flex-grow bg-dark-card border border-white/20 rounded-md py-3 px-4 text-white placeholder-light-gray/50 focus:outline-none focus:ring-2 focus:ring-primary-red"
            />
            <button
              type="submit"
              className="bg-primary-red text-white font-bold py-3 px-8 rounded-md hover:bg-red-700 transition-colors"
            >
              Найти
            </button>
          </form>

        </div>
      </div>

      {/* Машина и фон */}
      <div className="absolute hidden xl:block">
        <img
          src="/hero-car.png"
          alt="Tuned Mercedes Car"
          className="object-contain"
          style={{
            transform: 'translateX(10%)',
            width: 1700,
            height: 600,
            top: -50,
            right: -200,
          }}
        />
      </div>
    </section>
  );
};

export default Hero;
