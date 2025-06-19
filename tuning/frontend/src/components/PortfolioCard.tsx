// frontend/src/components/PortfolioCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FaArrowRight } from 'react-icons/fa'; // Иконка для "Подробнее"

interface PortfolioCardProps {
  id: number; // Добавляем ID для ссылки
  image_url: string | null;
  project_name: string;
  work_description: string;
  price: number | null;
}

const PortfolioCard: React.FC<PortfolioCardProps> = ({ id, image_url, project_name, work_description, price }) => {
  const displayImage = image_url || 'https://via.placeholder.com/400x300.png?text=No+Image';

  // Вся карточка теперь - это ссылка на детальную страницу проекта
  return (
    <Link to={`/portfolio/${id}`} className="bg-dark-card group flex flex-col h-full border border-transparent hover:border-primary-red/50 transition-all duration-300">
      <div className="overflow-hidden">
        <img 
          src={displayImage} 
          alt={project_name}
          className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-500" 
        />
      </div>
      <div className="p-6 flex flex-col flex-grow">
        <h3 className="text-xl font-bold text-white mb-2 leading-tight">{project_name}</h3>
        <div className="w-10 h-1 bg-primary-red mb-4"></div>
        <p className="text-light-gray text-sm mb-4 flex-grow">{work_description}</p>
        {price && <p className="text-white font-bold">{new Intl.NumberFormat('ru-RU').format(price)} рублей</p>}
        
        {/* Футер карточки с "Подробнее" */}
        <div className="border-t border-white/10 mt-auto pt-4 flex justify-between items-center text-white/80 group-hover:text-white">
            <span className="font-bold uppercase text-sm">Подробнее</span>
            <FaArrowRight className="text-primary-red group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
};

export default PortfolioCard;