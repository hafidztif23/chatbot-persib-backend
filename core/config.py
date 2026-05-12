import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Asisten Persib")

LANGUAGE_INSTRUCTION = f"""Jawab selalu dalam bahasa Indonesia yang formal tapi tetap ramah dan mudah dipahami. Gunakan bahasa sehari-hari yang natural, tidak kaku, dan tidak terlalu baku. Sesuaikan gaya bahasa dengan konteks percakapan agar terasa lebih personal dan menyenangkan bagi pengguna."""