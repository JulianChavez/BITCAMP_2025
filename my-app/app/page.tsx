'use client';
import { useEffect, useState, useRef } from 'react';
import ScrapeButton from '@/components/ScrapeButton';
import logo from '../public/images/podquirk-logo.png';
import Image from 'next/image';

const API_BASE_URL = 'http://localhost:5000';

const categories = [
  'business',
  'science',
  'technology',
  'health',
  'sports',
  'entertainment'
];

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good Morning';
  if (hour < 18) return 'Good Afternoon';
  return 'Good Evening';
};

export default function Home() {
  const [news, setNews] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('business');
  const [pageSize, setPageSize] = useState(5);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState('');
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [explorationMode, setExplorationMode] = useState<'news' | 'topic'>('news');
  const [topic, setTopic] = useState('');
  const [exploration, setExploration] = useState('');
  const [isExploring, setIsExploring] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (explorationMode === 'news') {
      fetchNews(selectedCategory, pageSize);
    }
  }, [selectedCategory, pageSize, explorationMode]);

  const fetchNews = async (category: string, pageSize: number) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/news?category=${category}&pageSize=${pageSize}`);
      const data = await response.json();
      setNews(data.articles || []);
    } catch (error) {
      console.error('Error fetching news:', error);
    }
    setLoading(false);
  };

  const handleSummarize = async () => {
    if (news.length === 0) return;
    
    setIsSummarizing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          articles: news,
          category: selectedCategory,
        }),
      });
      
      const data = await response.json();
      if (data.summary) {
        setSummary(data.summary);
        setAudioUrl(data.audio_url);
        if (data.cached) {
          console.log('Using cached summary');
          alert('Using cached summary (generated within last 10 minutes)');
        } else {
          console.log('Generated new summary');
          alert('Generated new summary');
        }
      }
    } catch (error) {
      console.error('Error generating summary:', error);
    }
    setIsSummarizing(false);
  };

  const handleExploreTopic = async () => {
    if (!topic.trim()) return;
    
    setIsExploring(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/explore-topic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
        }),
      });
      
      const data = await response.json();
      if (data.exploration) {
        setExploration(data.exploration);
        setAudioUrl(data.audio_url);
        if (data.cached) {
          console.log('Using cached exploration');
          alert('Using cached exploration (generated within last 10 minutes)');
        } else {
          console.log('Generated new exploration');
          alert('Generated new exploration');
        }
      }
    } catch (error) {
      console.error('Error exploring topic:', error);
    }
    setIsExploring(false);
  };

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col items-center mb-8">
          <Image
            src={logo}
            alt="PodQuirk Logo"
            width={300}
            height={100}
            priority
            style={{
              maxWidth: '100%',
              height: 'auto',
            }}
          />
          <h1 className="text-4xl font-bold text-center text-blue-600 mt-4">
            {getGreeting()}, Welcome to PodQuirk
          </h1>
        </div>
        
        <div className="mb-8 flex justify-center gap-4">
          <button
            onClick={() => setExplorationMode('news')}
            className={`px-4 py-2 rounded-lg ${
              explorationMode === 'news'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Top Headlines
          </button>
          <button
            onClick={() => setExplorationMode('topic')}
            className={`px-4 py-2 rounded-lg ${
              explorationMode === 'topic'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Explore Topic
          </button>
        </div>

        {explorationMode === 'news' ? (
          <>
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

              <button
                onClick={handleSummarize}
                disabled={isSummarizing || news.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isSummarizing ? 'Summarizing...' : 'Summarize'}
              </button>
            </div>

            {summary && (
              <div className="mb-8 bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Podcast Summary</h2>
                <div className="whitespace-pre-line text-gray-700 mb-4">{summary}</div>
                
                {audioUrl && (
                  <div className="flex items-center gap-4">
                    <button
                      onClick={togglePlay}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                    >
                      {isPlaying ? (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Pause
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Play
                        </>
                      )}
                    </button>
                    <audio
                      ref={audioRef}
                      src={audioUrl}
                      onEnded={() => setIsPlaying(false)}
                      className="hidden"
                    />
                  </div>
                )}
              </div>
            )}

            {loading ? (
              <div className="text-center">Loading...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {news.map((article: any) => (
                  <div
                    key={article.url}
                    className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden"
                  >
                    {article.urlToImage && (
                      <div className="relative aspect-square">
                        <Image
                          src={article.urlToImage}
                          alt={article.title}
                          fill
                          className="object-cover"
                        />
                      </div>
                    )}
                    <div className="p-4">
                      <h2 className="text-xl font-semibold mb-2 text-gray-800 line-clamp-2">
                        {article.title}
                      </h2>
                      <p className="text-gray-600 mb-4 line-clamp-3">{article.description}</p>
                      <div className="flex items-center justify-between">
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
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="space-y-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter a topic to explore..."
                className="flex-1 p-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleExploreTopic}
                disabled={isExploring || !topic.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isExploring ? 'Exploring...' : 'Explore Topic'}
              </button>
            </div>

            {exploration && (
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Topic Exploration</h2>
                <div className="whitespace-pre-line text-gray-700 mb-4">{exploration}</div>
                
                {audioUrl && (
                  <div className="flex items-center gap-4">
                    <button
                      onClick={togglePlay}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                    >
                      {isPlaying ? (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Pause
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Play
                        </>
                      )}
                    </button>
                    <audio
                      ref={audioRef}
                      src={audioUrl}
                      onEnded={() => setIsPlaying(false)}
                      className="hidden"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
