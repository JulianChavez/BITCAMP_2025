import os
from openai import OpenAI

class PerplexityAPI:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        
    def search(self, query: str) -> dict:
        """
        Search for research papers and information about a topic using Perplexity API
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a research assistant that provides concise summaries of academic topics. "
                    "Focus on recent developments, key findings, and implications."
                ),
            },
            {   
                "role": "user",
                "content": f"Provide a brief summary of recent research and developments about {query}.",
            },
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="sonar",
                messages=messages,
            )
            
            # Format the response into a structure similar to research papers
            content = response.choices[0].message.content
            return {
                'papers': [{
                    'title': query,
                    'abstract': content
                }]
            }
        except Exception as e:
            print(f"Error searching Perplexity API: {str(e)}")
            # Return a default response if the API call fails
            return {
                'papers': [{
                    'title': query,
                    'abstract': f"While we couldn't fetch recent research, here's what we know about {query}: It's a topic of ongoing study with various implications across different fields."
                }]
            } 