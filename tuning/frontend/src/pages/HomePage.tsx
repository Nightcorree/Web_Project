// frontend/src/pages/HomePage.tsx
import React from 'react';
import Hero from '../components/Hero';
import ServicesSection from '../components/ServicesSection';
import RecentWorkSection from '../components/RecentWorkSection';
import ArticlesSection from '../components/ArticlesSection';

const HomePage: React.FC = () => {
  return (
    
    <div> 
      <Hero />
      <ServicesSection />
      <RecentWorkSection />
      <ArticlesSection /> {/* <-- Добавляем секцию */}
    </div>
  );
};


export default HomePage;