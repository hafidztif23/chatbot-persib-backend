import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Asisten Persib")

LANGUAGE_INSTRUCTION = (
    "Identifikasi bahasa yang digunakan oleh user dalam pertanyaannya. "
    "Jawablah menggunakan bahasa yang sama dengan pertanyaan user tersebut, "
    "tetapi batasi pilihan bahasa jawaban HANYA ke dalam tiga bahasa ini: "
    "Bahasa Indonesia, English (Bahasa Inggris), atau Bahasa Sunda. "
    "Jika user bertanya menggunakan bahasa selain ketiga bahasa tersebut, jawablah menggunakan Bahasa Indonesia. "
    "Gunakan bahasa yang formal tapi tetap ramah, mudah dipahami, natural, tidak kaku, "
    "dan sesuaikan gaya bahasa dengan konteks percakapan agar terasa lebih personal."
)