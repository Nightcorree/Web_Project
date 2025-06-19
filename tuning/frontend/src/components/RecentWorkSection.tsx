// frontend/src/components/RecentWorkSection.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PortfolioCard from './PortfolioCard';
import { Link } from 'react-router-dom';

interface IPortfolioProject {
    id: number;
    project_name: string;
    work_description: string;
    price: number | null;
    image_url: string | null;
}

const RecentWorkSection: React.FC = () => {
    const [projects, setProjects] = useState<IPortfolioProject[]>([]);

    useEffect(() => {
        axios.get('http://127.0.0.1:8000/api/v1/portfolio/recent/')
            .then(response => {
                setProjects(response.data);
            })
            .catch(error => console.error("Failed to fetch recent work:", error));
    }, []);

    return (
        <section className="bg-dark-bg pt-15">
            <div className="container mx-auto px-4">
                <h2 className="text-5xl font-black text-white text-center mb-16 uppercase">
                    Наши работы
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {projects.map(project => (
                        <PortfolioCard key={project.id} {...project} />
                    ))}
                </div>
                <div className="text-center mt-16">
                    <Link
                        to="/portfolio"
                        className="bg-primary-red text-white font-bold py-3 px-10 rounded-md hover:bg-red-700 transition-colors text-lg"
                    >
                        Больше работ
                    </Link>
                </div>
            </div>
        </section>
    );
};

export default RecentWorkSection;