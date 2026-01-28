import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')
print(f"🔑 Clé: {api_key[:20]}..." if api_key else "❌ Pas de clé!")

headers = {'Authorization': f'Bearer {api_key}'}
payload = {
    'model': 'sonar',
    'messages': [{'role': 'user', 'content': 'Bonjour'}]
}

response = requests.post(
    'https://api.perplexity.ai/chat/completions',
    json=payload,
    headers=headers,
    timeout=30
)

print(f"📊 Status: {response.status_code}")
print(f"📝 Response: {response.json()}")
