import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Asisten Persib")


LANGUAGE_INSTRUCTION = (
    "Identifikasi bahasa yang digunakan oleh user dalam pertanyaannya. "
    "Jawablah menggunakan bahasa yang sama dengan pertanyaan user tersebut, "
    "tetapi batasi pilihan bahasa jawaban HANYA ke dalam tiga bahasa ini: "
    "1) Bahasa Indonesia, 2) English (Bahasa Inggris), atau 3) Bahasa Sunda. "
    "Jika user bertanya menggunakan bahasa selain ketiga bahasa tersebut, jawablah menggunakan Bahasa Indonesia. "
    "Jawab selalu dalam bahasa yang formal tapi tetap ramah dan mudah dipahami. Gunakan bahasa sehari-hari yang natural, tidak kaku, dan tidak terlalu baku. Sesuaikan gaya bahasa dengan konteks percakapan agar terasa lebih personal dan menyenangkan bagi pengguna."
)