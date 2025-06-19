// frontend/src/components/Pagination.tsx
import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <div className="flex justify-center items-center space-x-2 mt-12">
      {pages.map(page => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${
            currentPage === page
              ? 'bg-primary-red text-white cursor-default'
              : 'bg-dark-card text-light-gray hover:bg-primary-red/50'
          }`}
        >
          {page}
        </button>
      ))}
    </div>
  );
};

export default Pagination;