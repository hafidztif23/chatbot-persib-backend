from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import status, intents, merch, chat, jadwal, pemain, search, ticket
from routes.auth import router as auth_router
from routes.eskalasi import router as eskalasi_router
from routes.docs import router as docs_router
from core.embeddings import store_embeddings_from_docs
from core.docs_watcher import start_docs_watcher

app = FastAPI(title="Chatbot Persib API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "https://maungbot-project.web.app",
        "https://maungbot-project.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    # Embed semua dokumen dari GCS (skip kalau hash sama)
    print("[STARTUP] Mengecek embeddings dokumen dari GCS...")
    store_embeddings_from_docs()
    print("[STARTUP] Pengecekan selesai.")

    # Jalankan polling watcher GCS di background
    start_docs_watcher()


app.include_router(auth_router)
app.include_router(docs_router)
app.include_router(status.router)
app.include_router(intents.router)
app.include_router(merch.router)
app.include_router(chat.router)
app.include_router(jadwal.router)
app.include_router(pemain.router)
app.include_router(search.router)
app.include_router(ticket.router)
app.include_router(eskalasi_router)