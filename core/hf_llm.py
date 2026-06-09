import requests
import os

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACEHUB_API_TOKEN')}"
}

def query_hf(prompt: str):
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 256
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    result = response.json()

    # Handle output format
    if isinstance(result, list):
        return result[0]["generated_text"]
    return str(result)