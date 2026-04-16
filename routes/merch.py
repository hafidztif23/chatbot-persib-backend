from fastapi import APIRouter
from sqlalchemy import text
from core.db import engine
from core.embeddings import store_embeddings_from_docs

router = APIRouter()

@router.get("/merchandise")
def get_merchandise():
    items = []
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT name, stock FROM merchandise")).mappings().all()
        for row in rows:
            items.append({"name": row["name"], "stock": row["stock"]})
    return {"merchandise": items}

@router.post("/embeddings/refresh")
def refresh_embeddings():
    store_embeddings_from_docs()
    return {"message": "Embeddings berhasil diperbarui"}