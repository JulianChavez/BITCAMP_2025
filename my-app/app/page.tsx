'use client';
import { useEffect, useState } from 'react';
import ScrapeButton from '@/components/ScrapeButton';

const categories = [
  'business',
  'science',
  'technology',
  'health',
  'sports',
  'entertainment'
];

export default function Home() {
  const [news, setNews] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('business');
  const [pageSize, setPageSize] = useState(5);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchNews(selectedCategory, pageSize);
  }, [selectedCategory, pageSize]);

  const fetchNews = async (category: string, pageSize: number) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/news?category=${category}&pageSize=${pageSize}`);
      const data = await response.json();
      setNews(data.articles || []);
    } catch (error) {
      console.error('Error fetching news:', error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-blue-600">
          News Podcast
        </h1>
        
        <div className="mb-8 flex gap-4">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="flex-1 p-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
          
          <select 
            value={pageSize}
            onChange={(e) => setPageSize(parseInt(e.target.value))}
            className="w-24 p-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={5}>5 articles</option>
            <option value={10}>10 articles</option>
            <option value={15}>15 articles</option>
          </select>
        </div>

        {loading ? (
          <div className="text-center">Loading...</div>
        ) : (
          <div className="grid gap-6">
            {news.map((article: any) => (
              <div
                key={article.url}
                className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
              >
                <h2 className="text-xl font-semibold mb-2 text-gray-800">
                  {article.title}
                </h2>
                <p className="text-gray-600 mb-4">{article.description}</p>
                <div className="flex items-center gap-4">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700"
                  >
                    Read more →
                  </a>
                  <ScrapeButton articleUrl={article.url} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
