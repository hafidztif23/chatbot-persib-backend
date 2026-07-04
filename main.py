from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import status, intents, merch, chat, jadwal, pemain, search, ticket
from routes.auth import router as auth_router
from routes.eskalasi import router as eskalasi_router
from routes.docs import router as docs_router
from core.embeddings import store_embeddings_from_docs
from core.docs_watcher import start_docs_watcher

app = FastAPI(title="Chatbot Persib API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0].get("msg", "Input tidak valid.") if errors else "Input tidak valid."
    msg = msg.replace("Value error, ", "")
    return JSONResponse(
        status_code=422,
        content={
            "intent": "error",
            "score": 0.0,
            "response": msg,
            "escalated": False
        }
    )

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