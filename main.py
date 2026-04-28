from fastapi import FastAPI
from routes import status, intents, merch, chat, jadwal, pemain, search
from core.embeddings import store_embeddings_from_docs
from core.docs_watcher import start_docs_watcher

app = FastAPI(title="Chatbot Persib API")

@app.on_event("startup")
def startup():
    # Hanya embed file yang belum di-embed atau ada perubahan
    print("Mengecek embeddings dokumen...")
    store_embeddings_from_docs()
    print("Pengecekan selesai.")

    # Jalankan watcher di background
    start_docs_watcher(docs_folder="docs")

app.include_router(status.router)
app.include_router(intents.router)
app.include_router(merch.router)
app.include_router(chat.router)
app.include_router(jadwal.router)
app.include_router(pemain.router)
app.include_router(search.router)