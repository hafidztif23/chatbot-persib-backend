import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Asisten Persib")