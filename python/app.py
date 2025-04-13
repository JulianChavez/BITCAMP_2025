from flask import Flask, request, jsonify
from flask_cors import CORS
from news_api import NewsAPI
from summarizer import ArticleSummarizer
from elevenLabs import ElevenLabs
from s3_cache import S3CacheManager
import os
from openai import OpenAI
from perplexity import PerplexityAPI
import json
import re

app = Flask(__name__)

# Configure CORS to allow all origins during development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Add error handling middleware
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

def sanitize_filename(topic: str) -> str:
    """Remove invalid characters from the topic to create a valid filename."""
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^\w\s-]', '_', topic)
    # Replace multiple spaces or underscores with a single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

news_api = NewsAPI()
summarizer = ArticleSummarizer()
cache_manager = S3CacheManager()
perplexity_api = PerplexityAPI()

@app.route('/api/news', methods=['GET'])
def get_news():
    category = request.args.get('category', 'business')
    page_size = int(request.args.get('pageSize', 5))
    
    try:
        response = news_api.get_top_headlines(category=category, page_size=page_size)
        if response and 'articles' in response:
            return jsonify({'articles': response['articles']})
        return jsonify({'error': 'No articles found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_articles():
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        category = data.get('category', '')
        
        if not articles or not category:
            return jsonify({'error': 'Articles and category are required'}), 400
        
        # Check cache first
        cached_summary = cache_manager.get_cached_summary(category)
        audio_url = cache_manager.get_audio_url(category)
        
        if cached_summary and audio_url:
            return jsonify({
                'summary': cached_summary,
                'cached': True,
                'audio_url': audio_url
            })
            
        # Generate new summary if not in cache
        summary = summarizer.generate_podcast_script(articles, category)
        if summary:
            # Generate audio
            elevenlabs = ElevenLabs(summary)
            audio_file = f"podcast_output_{category}.mp3"
            elevenlabs.create_conversation(audio_file)
            
            # Cache both summary and audio
            cache_manager.cache_summary(category, summary)
            cache_manager.cache_audio(category, audio_file)
            
            # Get the new audio URL
            audio_url = cache_manager.get_audio_url(category)
            
            # Clean up local audio file
            if os.path.exists(audio_file):
                os.remove(audio_file)
            
            return jsonify({
                'summary': summary,
                'cached': False,
                'audio_url': audio_url
            })
        return jsonify({'error': 'Failed to generate summary'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/explore-topic', methods=['POST'])
def explore_topic():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Sanitize the topic for use in filenames
        sanitized_topic = sanitize_filename(topic)
        
        # Check cache first
        cached_exploration = cache_manager.get_cached_exploration(sanitized_topic)
        audio_url = cache_manager.get_audio_url(f"explore_{sanitized_topic}")
        
        if cached_exploration and audio_url:
            return jsonify({
                'exploration': cached_exploration,
                'cached': True,
                'audio_url': audio_url
            })
        
        # Use OpenAI to generate initial understanding
        openai_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable research assistant."},
                {"role": "user", "content": f"""Create a 30 seconds - 1 minute podcast script (50-100 words), not including the title and description and host names. The word count will be base on what the host says.
                about the topic: {topic}.
                The script should be in a conversational format between two hosts, Host A and Host B.
                Make it engaging and include 1-2 sentences of analysis or implications for each major point.
                Format the output as a script with clear speaker labels. Format the script with no markdown.
                Have the first line be "Host A" that will be describing the title and whats happening. When a Host is going to speak
                about the other host, use "Edward" for host A and "Mark" for host B.If the host is going to scream or laugh with using all caps, exclamation marks.
        Do not add symbols like *, #, or () in the script. Don't have the host's name in the script when they are speaking.
                
                Please provide a natural, engaging conversation that flows well and maintains listener interest."""}
            ]
        )
        
        initial_understanding = openai_response.choices[0].message.content
        
        # Use Perplexity API to gather research papers and deeper insights
        research_results = perplexity_api.search(topic)
        
        # Format research results into a readable format
        research_summary = "\n".join([
            f"- {paper.get('title', 'Untitled')}: {paper.get('abstract', 'No abstract available')}"
            for paper in research_results.get('papers', [])
        ])
        
        # Create a final podcast script combining the initial understanding and research
        final_script = f"""Host A: Today we're diving deep into {topic}. Let me give you an overview of what we'll be discussing.

{initial_understanding}

Host B: That's fascinating, Edward. Let me add some insights from recent research in this field.

{research_summary if research_summary else "Host B: While there's ongoing research in this field, let's focus on the key aspects we've discussed."}

Host A: Thanks for sharing those insights, Mark. It's clear that {topic} is a fascinating topic with many implications.

Host B: Absolutely, Edward. The information we've discussed today shows just how dynamic and important this topic is."""
        
        # Generate audio
        # Taking out perplexity_api. Only using OpenAI api fro now
        elevenlabs = ElevenLabs(initial_understanding)
        audio_file = f"podcast_explore_{sanitized_topic}.mp3"
        elevenlabs.create_conversation(audio_file)
        
        # Cache both exploration and audi | CHANGED
        cache_manager.cache_exploration(sanitized_topic, initial_understanding)
        cache_manager.cache_audio(f"explore_{sanitized_topic}", audio_file)
        
        # Get the new audio URL
        audio_url = cache_manager.get_audio_url(f"explore_{sanitized_topic}")
        
        # Clean up local audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        return jsonify({
            'exploration': initial_understanding,
            'cached': False,
            'audio_url': audio_url
        })
        
    except Exception as e:
        print(f"Error in explore_topic: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 