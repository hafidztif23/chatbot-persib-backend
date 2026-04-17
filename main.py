from fastapi import FastAPI
from routes import status, intents, merch, chat, jadwal
from core.embeddings import store_embeddings_from_docs


app = FastAPI(title="Chatbot Persib API")

@app.on_event("startup")
def startup():
    print("Menyimpan embeddings dokumen ke PostgreSQL...")
    store_embeddings_from_docs()
    print("Embeddings siap.")

app.include_router(status.router)
app.include_router(intents.router)
app.include_router(merch.router)
app.include_router(chat.router)
app.include_router(jadwal.router)