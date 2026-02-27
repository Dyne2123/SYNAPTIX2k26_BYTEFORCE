import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SARVAM")
URL = "https://api.sarvam.ai/v1/chat/completions"

def get_reply(user_message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are a edu bot which helps student to clarifi doubts"},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print(result["choices"][0]["message"]["content"])
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"
    
