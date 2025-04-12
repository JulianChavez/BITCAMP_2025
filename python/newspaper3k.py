from flask import Flask, request, jsonify
from flask_cors import CORS 
from newspaper import Article
import json
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        print(data)
        url = data.get('url')
        
        app.logger.info(f"Processing URL: {url}")
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        article = Article(url)
        article.download()
        article.parse()
        
        return jsonify({
            'title': article.title,
            'text': article.text,
            'authors': article.authors,
            'publish_date': str(article.publish_date),
            'summary': article.summary
        })
        
    except Exception as e:
        app.logger.error(f"Error scraping URL {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

    
