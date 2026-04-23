from fastapi import APIRouter
from pydantic import BaseModel
from langchain_classic.schema import HumanMessage
from core.intents import detect_intent, extract_lawan
from core.db import check_merch_stock, get_jadwal_terdekat, get_jadwal_terdekat, get_jadwal_by_lawan
from core.rag import llm
from core.memory import load_history, save_context, clear_history
from core.embeddings import semantic_search


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
    intent, score = detect_intent(query)

    history = load_history(session_id, limit=5)
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

    elif intent == "info_jadwal_terdekat":
        jadwal = get_jadwal_terdekat()
        if jadwal:
            data_jadwal = f"""Pertandingan terdekat:
- Lawan: {jadwal['lawan']}
- Tanggal: {jadwal['tanggal_jam']}
- Lokasi: {jadwal['lokasi']}
- Kompetisi: {jadwal['kompetisi']}
- Status: {jadwal['status_pertandingan']}"""
        else:
            data_jadwal = "Tidak ada jadwal pertandingan yang akan datang."
        
        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Jawab selalu dalam Bahasa Indonesia.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_jadwal}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""
        
    elif intent == "info_jadwal":
        nama_lawan = extract_lawan(query)
        jadwal_list = get_jadwal_by_lawan(nama_lawan) if nama_lawan else None

        if jadwal_list:
            data_jadwal = "\n".join([
                f"""Pertandingan {idx + 1}:
- Lawan: {j['lawan']}
- Tanggal: {j['tanggal_jam']}
- Lokasi: {j['lokasi']}
- Kompetisi: {j['kompetisi']}
- Status: {j['status_pertandingan']}"""
                for idx, j in enumerate(jadwal_list)
            ])
        else:
            data_jadwal = f"Tidak ada jadwal pertandingan melawan '{nama_lawan}' yang ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Jawab selalu dalam Bahasa Indonesia.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_jadwal}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
    else:
        # Ambil context dari pgvector
        search_results = semantic_search(query, top_k=3)

        if search_results:
            context = "\n\n".join(
                f"[Sumber: {r['source']}]\n{r['content']}"
                for r in search_results
            )
        else:
            context = "Tidak ada informasi yang relevan ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah dan helpful.
Jawab selalu dalam Bahasa Indonesia, singkat, dan natural.
Gunakan HANYA informasi dari konteks berikut untuk menjawab.
Jika informasi tidak ada di konteks, katakan dengan jujur bahwa kamu tidak tahu.

Konteks:
{context}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan: {query}
Jawaban:"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    # Simpan ke PostgreSQL
    save_context(session_id, query, answer)

    return {"intent": intent, "score": score, "response": answer, "session_id": session_id}

@router.delete("/chat/history/{session_id}")
def delete_history(session_id: str):
    clear_history(session_id)
    return {"message": f"History untuk session '{session_id}' berhasil dihapus"}