from fastapi import FastAPI
from routes import status, intents, merch, chat

app = FastAPI(title="Chatbot Persib API")

app.include_router(status.router)
app.include_router(intents.router)
app.include_router(merch.router)
app.include_router(chat.router)