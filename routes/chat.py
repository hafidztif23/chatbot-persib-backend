from fastapi import APIRouter
from pydantic import BaseModel
from langchain_classic.schema import HumanMessage
from core.intents import detect_intent
from core.db import check_merch_stock
from core.rag import llm, rag_qa

router = APIRouter()

item_map = {
    "stok_jersey": "Jersey Persib 2025",
    "stok_scarf": "Scarf Maung Bandung",
    "stok_topi": "Topi Persib"
}

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
def chat(req: QueryRequest):
    query = req.query
    intent, score = detect_intent(query)

    if intent in item_map:
        item_name = item_map[intent]
        stock = check_merch_stock(item_name)
        if stock is not None:
            prompt = f"""
Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.
Data: Merchandise {item_name}, Stok saat ini: {stock} pcs.
Jawaban harus ramah dan langsung memberikan jumlah stok.
Jawab selalu dalam Bahasa Indonesia.
Pertanyaan user: '{query}'
"""
        else:
            prompt = f"""
Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Data: Merchandise {item_name} tidak tersedia.
Jawaban harus ramah dan beri tahu user bahwa merchandise tidak ditemukan.
Jawab selalu dalam Bahasa Indonesia.
Pertanyaan user: '{query}'
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"intent": intent, "score": score, "response": response.content.strip()}

    # Default → RAG
    response = rag_qa.run(query)
    return {"intent": intent, "score": score, "response": response}