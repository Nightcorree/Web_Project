// frontend/src/pages/PortfolioPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PortfolioCard from '../components/PortfolioCard'; // Используем наш готовый компонент

// Интерфейс для данных, которые мы получаем с бэкенда
interface IPortfolioProject {
  id: number;
  project_name: string;
  work_description: string;
  price: number | null;
  image_url: string | null;
}

const PortfolioPage: React.FC = () => {
  const [projects, setProjects] = useState<IPortfolioProject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загружаем ВСЕ проекты с нового API
    axios.get('http://127.0.0.1:8000/api/v1/portfolio/all/')
      .then(response => {
        setProjects(response.data);
      })
      .catch(error => console.error("Failed to fetch portfolio projects:", error))
      .finally(() => setLoading(false));
  }, []); // Пустой массив зависимостей - эффект выполнится один раз

  return (
    <div className="bg-dark-bg">
      <div className="container mx-auto px-4 py-24 pt-40">
        <h1 className="text-5xl font-black text-white text-center mb-16 uppercase">
          Наши работы
        </h1>

        {loading ? (
          <p className="text-center text-white">Загрузка работ...</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {projects.map(project => (
              <PortfolioCard key={project.id} {...project} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioPage;