from fastapi import APIRouter
from pydantic import BaseModel
from core.embeddings import semantic_search, store_embeddings_from_docs

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

@router.post("/search/semantic")
def semantic_search_endpoint(req: SearchRequest):
    results = semantic_search(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "top_k": req.top_k,
        "results": results
    }

@router.post("/embeddings/refresh")
def refresh_embeddings():
    store_embeddings_from_docs()
    return {"message": "Embeddings berhasil diperbarui"}