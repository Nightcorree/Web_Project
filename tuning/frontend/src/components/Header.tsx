// frontend/src/components/Header.tsx
import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { FaMapMarkerAlt, FaVk } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const linkStyles = "hover:text-primary-red transition-colors py-2";
  const activeLinkStyles = { color: '#FF0024', borderBottom: '2px solid #FF0024' };

  return (
    <header className="bg-dark-bg/90 backdrop-blur-sm text-white fixed top-0 left-0 right-0 z-50">
      {/* Верхняя полоска */}
      <div className="bg-dark-card">
        <div className="container mx-auto px-4 flex justify-between items-center text-sm text-light-gray py-1">
          <div className="flex items-center space-x-4">
            <p>Полный спектр услуг по автотюнингу в Москве</p>
            <a href="#" className="hover:text-white"><FaVk size={18} /></a>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <FaMapMarkerAlt className="text-primary-red" />
              <span>г. Москва</span>
            </div>
            <div>
              {user ? (
                  <div className="flex items-center space-x-4">
                      <Link to="/profile" className="font-bold hover:text-primary-red">{user.email}</Link>
                      <button onClick={logout} className="bg-primary-red py-2 px-4 text-sm rounded">Выйти</button>
                  </div>
              ) : (
                  <div className="flex items-center space-x-2">
                      <Link to="/login" className="py-2 px-4 text-sm">Войти</Link>
                      <Link to="/register" className="bg-primary-red py-2 px-4 text-sm rounded">Регистрация</Link>
                  </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Основная навигация */}
      <div className="container mx-auto px-4 flex justify-between items-center py-3">
        <Link to="/" className="text-2xl font-black">
          Slick Auto
        </Link>
        <nav className="hidden md:flex items-center space-x-8 text-sm font-bold uppercase">
          <NavLink to="/" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Главная</NavLink>
          <NavLink to="/services" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Услуги</NavLink>
          <NavLink to="/about" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>О нас</NavLink>
          <NavLink to="/portfolio" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Наши работы</NavLink>
          <NavLink to="/reviews" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Отзывы</NavLink>
          <NavLink to="/actions" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Акции</NavLink>
          <NavLink to="/blog" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Статьи</NavLink>
          <NavLink to="/contacts" className={linkStyles} style={({ isActive }) => isActive ? activeLinkStyles : undefined}>Контакты</NavLink>
        </nav>
        <div className="md:hidden">
          {/* Mobile menu button */}
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" /></svg>
        </div>
      </div>
    </header>
  );
};

export default Header;