'use client'

import { useState } from 'react'

interface ScrapeButtonProps {
    articleUrl: string
}

export default function ScrapeButton({ articleUrl }: ScrapeButtonProps) {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleScrape = async () => {
        try {
            setIsLoading(true)
            setError(null)
            
            const response = await fetch('/api/scrapeNews', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: articleUrl }),
            })

            const data = await response.json()
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to scrape article')
            }

            // Create a new window with the scraped content
            const newWindow = window.open('', '_blank', 'width=800,height=600')
            if (newWindow) {
                newWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>${data.title || 'Scraped Article'}</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    line-height: 1.6;
                                    max-width: 800px;
                                    margin: 0 auto;
                                    padding: 20px;
                                }
                                h1 {
                                    color: #333;
                                    border-bottom: 2px solid #eee;
                                    padding-bottom: 10px;
                                }
                                .meta {
                                    color: #666;
                                    font-size: 0.9em;
                                    margin-bottom: 20px;
                                }
                                .content {
                                    white-space: pre-wrap;
                                }
                            </style>
                        </head>
                        <body>
                            <h1>${data.title || 'No Title Available'}</h1>
                            <div class="meta">
                                <p><strong>Authors:</strong> ${data.authors?.join(', ') || 'Unknown'}</p>
                                <p><strong>Published:</strong> ${data.publish_date ? new Date(data.publish_date).toLocaleDateString() : 'Unknown'}</p>
                            </div>
                            <div class="content">
                                ${data.text || data.summary || 'No content available'}
                            </div>
                        </body>
                    </html>
                `)
                newWindow.document.close()
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="relative">
            <button
                onClick={handleScrape}
                disabled={isLoading}
                className="text-blue-500 hover:text-blue-700 disabled:text-gray-400"
            >
                {isLoading ? 'Scraping...' : 'Scrape Article'}
            </button>

            {error && (
                <div className="absolute top-full left-0 mt-1 p-2 bg-red-100 text-red-700 text-sm rounded shadow-lg z-10">
                    {error}
                </div>
            )}
        </div>
    )
} 