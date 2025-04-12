import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ArticleSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def generate_podcast_script(self, articles, category):
        # Prepare the articles content
        articles_content = "\n\n".join([
            f"Title: {article['title']}\nDescription: {article['description']}\nContent: {article.get('content', '')}"
            for article in articles
        ])
        
        # Create the prompt for GPT-4
        prompt = f"""Create a 6-8 minute podcast script (1000-1200 words), not including the title and description and host names. The word count will be base on what the host says.
          summarizing the following news articles about {category}.
        The script should be in a conversational format between two hosts, Host A and Host B.
        Make it engaging and include 1-2 sentences of analysis or implications for each major point.
        Format the output as a script with clear speaker labels.
        
        Articles to summarize:
        {articles_content}
        
        Please provide a natural, engaging conversation that flows well and maintains listener interest.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional podcast script writer who creates engaging, conversational content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None 