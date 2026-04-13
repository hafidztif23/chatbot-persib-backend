from fastapi import APIRouter
from pydantic import BaseModel
from langchain_classic.schema import HumanMessage
from core.intents import detect_intent
from core.db import check_merch_stock
from core.rag import llm, rag_qa
from core.memory import get_memory

router = APIRouter()

item_map = {
    "stok_jersey": "Jersey Persib 2025",
    "stok_scarf": "Scarf Maung Bandung",
    "stok_topi": "Topi Persib"
}

class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"

@router.post("/chat")
def chat(req: QueryRequest):
    query = req.query
    session_id = req.session_id
    memory = get_memory(session_id)

    intent, score = detect_intent(query)

    history = memory.load_memory_variables({}).get("chat_history", [])
    history_text = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Asisten'}: {m.content}"
        for m in history
    )

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

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'
"""
        else:
            prompt = f"""
Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Data: Merchandise {item_name} tidak tersedia.
Jawaban harus ramah dan beri tahu user bahwa merchandise tidak ditemukan.
Jawab selalu dalam Bahasa Indonesia.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    else:
        # RAG flow — inject history ke query
        query_with_history = f"""Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan sekarang: {query}""" if history_text else query

        answer = rag_qa.run(query_with_history)

    # Simpan ke memory
    memory.save_context({"input": query}, {"output": answer})

    return {"intent": intent, "score": score, "response": answer, "session_id": session_id}