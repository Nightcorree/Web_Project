// frontend/src/pages/BlogPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ArticleCard from '../components/ArticleCard'; // Используем наш готовый компонент

// Интерфейс для данных, которые мы получаем с бэкенда
interface IBlogPost {
  id: number;
  title: string;
  short_content: string;
  image_url: string | null;
}

const BlogPage: React.FC = () => {
  const [posts, setPosts] = useState<IBlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загружаем ВСЕ статьи с нового API
    axios.get('http://127.0.0.1:8000/api/v1/blog/all/')
      .then(response => {
        setPosts(response.data);
      })
      .catch(error => console.error("Failed to fetch blog posts:", error))
      .finally(() => setLoading(false));
  }, []); // Пустой массив зависимостей - эффект выполнится один раз

  return (
    <div className="bg-dark-bg">
      <div className="container mx-auto px-4 py-24 pt-40">
        <h1 className="text-5xl font-black text-white text-center mb-16 uppercase">
          Статьи
        </h1>

        {loading ? (
          <p className="text-center text-white">Загрузка статей...</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map(post => (
              <ArticleCard key={post.id} {...post} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BlogPage;