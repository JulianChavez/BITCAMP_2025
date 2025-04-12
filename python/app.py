from flask import Flask, request, jsonify
from flask_cors import CORS
from news_api import NewsAPI
from summarizer import ArticleSummarizer

app = Flask(__name__)
CORS(app)

news_api = NewsAPI()
summarizer = ArticleSummarizer()

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
            
        summary = summarizer.generate_podcast_script(articles, category)
        if summary:
            return jsonify({'summary': summary})
        return jsonify({'error': 'Failed to generate summary'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 