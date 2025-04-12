import boto3
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class S3CacheManager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        self.cache_duration = timedelta(minutes=10)

    def _get_cache_key(self, category):
        return f"summaries/{category}.json"

    def get_cached_summary(self, category):
        try:
            cache_key = self._get_cache_key(category)
            response = self.s3.get_object(Bucket=self.bucket_name, Key=cache_key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Check if the cache is still valid
            cache_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cache_time <= self.cache_duration:
                return data['summary']
            return None
        except Exception as e:
            print(f"Error retrieving from cache: {e}")
            return None

    def cache_summary(self, category, summary):
        try:
            cache_key = self._get_cache_key(category)
            data = {
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=cache_key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error caching summary: {e}") 