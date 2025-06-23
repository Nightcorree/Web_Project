// frontend/src/App.tsx
// Этот файл теперь отвечает за навигацию и общую структуру

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header'; // <-- Убедитесь, что вы создали этот файл
import HomePage from './pages/HomePage';   // <-- И этот тоже
import ServicesPage from './pages/ServicesPage'; // И все остальные страницы, которые мы будем использовать
import PortfolioPage from './pages/PortfolioPage';
import Footer from './components/Footer';
import BlogPage from './pages/BlogPage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import SearchPage from './pages/SearchPage'
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import OrderCreatePage from './pages/OrderCreatePage';
import OrderEditPage from './pages/OrderEditPage';
import ReviewsPage from './pages/ReviewsPage';

function App() {
  return (
    // <Router> включает всю логику навигации
    <Router>
      <div className="flex flex-col min-h-screen bg-dark-bg text-white">
        {/* Header будет отображаться на всех страницах */}
        <Header />

        {/* <main> - это основное содержимое, которое будет меняться */}
        <main className="flex-grow">
          <Routes>
            {/* В зависимости от URL, React Router будет рендерить нужный компонент */}
            <Route path="/" element={<HomePage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/reviews" element={<ReviewsPage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/blog/:articleId" element={<ArticleDetailPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Защищенные роуты */}
            <Route element={<ProtectedRoute />}>
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/orders/create" element={<OrderCreatePage />} />
              <Route path="/orders/edit/:orderId" element={<OrderEditPage />} /> 
            </Route>
          </Routes>
        </main>
        
        <Footer /> 
      </div>
    </Router>
  );
}

export default App;