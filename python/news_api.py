# File to get New aggregation

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()



class NewsAPI:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2'
    
    # category, business, entertainment, general, health, science, sports, technology
    def get_top_headlines(self, country='us', category='business', page_size=20):
        """
        Fetch top headlines from NewsAPI
        Returns:
            dict: JSON response containing the news articles
        """
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
            
        endpoint = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'country': country,
            'pageSize': page_size
        }
        
        if category:
            params['category'] = category
            
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return None

# Example usage
if __name__ == "__main__":
    news_api = NewsAPI()
    headlines_list = []
    headlines_business = news_api.get_top_headlines(category='business')
    headlines_sports = news_api.get_top_headlines(category='sports')
    headlines_list.append(headlines_business)
    headlines_list.append(headlines_sports)
    
    for headlines in headlines_list:
        if headlines and headlines.get('articles'):
            for article in headlines['articles']:
                print(f"Title: {article['title']}")
            print(f"Source: {article['source']['name']}")
            print(f"URL: {article['url']}")
            print("---")
