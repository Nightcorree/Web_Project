// frontend/src/components/ArticlesSection.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ArticleCard from './ArticleCard';
import { Link } from 'react-router-dom';

interface IBlogPost {
    id: number;
    title: string;
    short_content: string;
    image_url: string | null;
}

const ArticlesSection: React.FC = () => {
    const [posts, setPosts] = useState<IBlogPost[]>([]);

    useEffect(() => {
        axios.get('http://127.0.0.1:8000/api/v1/blog/recent/')
            .then(response => {
                setPosts(response.data);
            })
            .catch(error => console.error("Failed to fetch recent blog posts:", error));
    }, []);

    return (
        <section className="bg-dark-bg py-24">
            <div className="container mx-auto px-4">
                <h2 className="text-5xl font-black text-white text-center mb-16 uppercase">
                    Статьи
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {posts.map(post => (
                        <ArticleCard key={post.id} {...post} />
                    ))}
                </div>
                <div className="text-center mt-16">
                    <Link
                        to="/blog"
                        className="bg-primary-red text-white font-bold py-3 px-10 rounded-md hover:bg-red-700 transition-colors text-lg"
                    >
                        Все статьи
                    </Link>
                </div>
            </div>
        </section>
    );
};

export default ArticlesSection;