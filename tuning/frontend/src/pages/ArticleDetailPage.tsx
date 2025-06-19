// frontend/src/pages/ArticleDetailPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

// Интерфейс для данных ОДНОЙ статьи. Нам нужен полный content.
interface IBlogPostDetail {
  id: number;
  title: string;
  content: string; // <-- Полное содержание
  image_url: string | null;
  publication_date: string;
}

const ArticleDetailPage: React.FC = () => {
  // useParams() - это хук из react-router-dom, который достает параметры из URL (в нашем случае :articleId)
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<IBlogPostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!articleId) return;

    const fetchArticle = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/v1/blog/${articleId}/`);
        setArticle(response.data);
      } catch (err) {
        setError('Не удалось загрузить статью.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [articleId]); // Эффект будет перезапускаться, если ID в URL изменится

  if (loading) {
    return <div className="text-center py-40">Загрузка...</div>;
  }

  if (error) {
    return <div className="text-center py-40 text-red-500">{error}</div>;
  }

  if (!article) {
    return <div className="text-center py-40">Статья не найдена.</div>;
  }

  return (
        <div className="bg-dark-bg text-white">
          <div className="container mx-auto px-4 py-24 pt-40">
            <h1 className="text-4xl md:text-6xl font-black text-center mb-12">{article.title}</h1>
    
            {article.image_url && (
                <div className="mb-8">
                    <img src={article.image_url} alt={article.title} className="w-full max-h-[500px] h-auto object-cover rounded-lg" />
                </div>
            )}

            {/* Контейнер для всего текста статьи */}
            <div 
                className="prose prose-invert max-w-none mx-auto text-light-gray leading-relaxed"
                // Заменяем переносы строк на теги <br> и вставляем как HTML
                dangerouslySetInnerHTML={{ __html: article.content.replace(/\n/g, '<br />') }} 
            />
          </div>
        </div>
      );
};

export default ArticleDetailPage;