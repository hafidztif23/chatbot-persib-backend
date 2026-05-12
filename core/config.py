import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Asisten Persib")

LANGUAGE_INSTRUCTION = f"""Deteksi bahasa yang digunakan user (Bahasa Indonesia, Bahasa Sunda, atau campuran keduanya) beserta gaya bahasanya (formal, informal, atau gaul/slang), lalu balas menggunakan bahasa dan gaya bahasa yang sama dengan user."""