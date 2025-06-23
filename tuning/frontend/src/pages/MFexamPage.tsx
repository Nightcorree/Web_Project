// frontend/src/pages/MFexamPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Интерфейс для данных об одном экзамене
interface IExam {
  id: number;
  title: string;
  exam_date: string;
  task_image_url: string | null;
  examinees: string[];
}

const MFexamPage: React.FC = () => {
  const [exams, setExams] = useState<IExam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Загружаем список опубликованных экзаменов
    axios.get('/api/v1/mfexams/')
      .then(response => {
        setExams(response.data);
      })
      .catch(err => {
        console.error("Failed to fetch exams:", err);
        setError("Не удалось загрузить данные об экзаменах.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-dark-bg text-white">
      <div className="container mx-auto px-4 py-24 pt-40">
        
        {/* Заголовок с вашими данными */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-black uppercase">
            Фарафонов Максим Евгеньевич
          </h1>
          <p className="text-2xl text-light-gray mt-2">
            Группа 231-322
          </p>
        </div>

        {/* Отображение данных */}
        {loading && <p className="text-center">Загрузка экзаменов...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}
        
        {!loading && !error && (
          <div className="space-y-8 max-w-4xl mx-auto">
            {exams.length > 0 ? (
              exams.map(exam => (
                <div key={exam.id} className="bg-dark-card p-6 rounded-lg shadow-lg">
                  <h2 className="text-2xl font-bold text-primary-red mb-4">{exam.title}</h2>
                  
                  {/* Изображение, если оно есть */}
                  {exam.task_image_url && (
                    <div className="mb-4">
                      <p className="text-sm font-bold text-light-gray mb-2">Изображение с заданием:</p>
                      <img 
                        src={exam.task_image_url} 
                        alt={`Задание для ${exam.title}`} 
                        className="max-w-full h-auto rounded-md"
                      />
                    </div>
                  )}

                  <div className="text-light-gray space-y-2">
                    <p>
                      <strong>Дата проведения:</strong> 
                      {/* Форматируем дату в более читаемый вид */}
                      {new Date(exam.exam_date).toLocaleString('ru-RU', {
                        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                      })}
                    </p>
                    <div>
                      <strong>Участники экзамена:</strong>
                      {exam.examinees.length > 0 ? (
                        <ul className="list-disc list-inside ml-4 mt-1">
                          {exam.examinees.map((name, index) => (
                            <li key={index}>{name}</li>
                          ))}
                        </ul>
                      ) : (
                        <span className="ml-2">Не назначены</span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-light-gray">Нет опубликованных экзаменов.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MFexamPage;