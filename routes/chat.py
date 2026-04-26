from fastapi import APIRouter
from pydantic import BaseModel
from langchain_classic.schema import HumanMessage
from core.intents import detect_intent, extract_lawan, extract_nama_pemain, extract_posisi, extract_status_pemain
from core.db import check_merch_stock, get_jadwal_terdekat, get_jadwal_terdekat, get_jadwal_by_lawan, get_pemain_by_nama, get_pemain_by_posisi, get_pemain_by_status
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
        
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
        
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

    elif intent == "info_pemain":
        nama = extract_nama_pemain(query)
        pemain = get_pemain_by_nama(nama) if nama else None

        if pemain:
            data_pemain = f"""Data pemain:
- Nama: {pemain['nama_pemain']}
- Nomor Punggung: {pemain['nomor_punggung']}
- Posisi: {pemain['posisi']}
- Kewarganegaraan: {pemain['kewarganegaraan']}
- Tanggal Lahir: {pemain['tanggal_lahir']}
- Status: {pemain['status']}"""
        else:
            data_pemain = f"Pemain dengan nama '{nama}' tidak ditemukan di skuad Persib."

        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Jawab selalu dalam Bahasa Indonesia.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_pemain}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "info_pemain_posisi":
        posisi = extract_posisi(query)
        pemain_list = get_pemain_by_posisi(posisi) if posisi else []

        if pemain_list:
            data_pemain = f"Daftar pemain posisi {posisi}:\n" + "\n".join(
                f"- #{p['nomor_punggung']} {p['nama_pemain']} ({p['kewarganegaraan']})"
                for p in pemain_list
            )
        else:
            data_pemain = f"Tidak ada data pemain untuk posisi '{posisi}'."

        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Jawab selalu dalam Bahasa Indonesia.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_pemain}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "info_pemain_status":
        status = extract_status_pemain(query)
        pemain_list = get_pemain_by_status(status) if status else []

        if pemain_list:
            data_pemain = f"Daftar pemain dengan status {status}:\n" + "\n".join(
                f"- #{p['nomor_punggung']} {p['nama_pemain']} ({p['posisi']})"
                for p in pemain_list
            )
        else:
            data_pemain = f"Tidak ada pemain dengan status '{status}'."

        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah, singkat, dan natural.
Jawab selalu dalam Bahasa Indonesia.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_pemain}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
    
    elif intent in {
        "info_membersib",
        "info_passport_persib", 
        "benefit_membersib",
        "benefit_passport_persib",
        "harga_keanggotaan",
        "cara_daftar_membersib",
        "cara_daftar_passport",
        "perbandingan_keanggotaan"
    }:
        # Buat query yang lebih spesifik berdasarkan intent
        intent_query_map = {
            "info_membersib": "MemberSIB program keanggotaan digital Persib",
            "info_passport_persib": "Passport Persib program keanggotaan premium",
            "benefit_membersib": "manfaat keuntungan benefit MemberSIB",
            "benefit_passport_persib": "manfaat keuntungan benefit Passport Persib",
            "harga_keanggotaan": "harga biaya keanggotaan MemberSIB Passport Persib",
            "cara_daftar_membersib": "cara daftar pendaftaran MemberSIB",
            "cara_daftar_passport": "cara daftar pendaftaran Passport Persib",
            "perbandingan_keanggotaan": "perbedaan MemberSIB Passport Persib perbandingan"
        }

        # Gunakan query yang diperkaya untuk semantic search
        enriched_query = intent_query_map.get(intent, query)
        search_results = semantic_search(enriched_query, top_k=5)

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
    
    elif intent in {
        "info_stadion_gbla",
        "peraturan_penonton_boleh",
        "peraturan_penonton_dilarang",
        "sanksi_pelanggaran",
        "fasilitas_stadion",
        "info_parkir_stadion",
        "info_tiket_stadion",
        "info_media_stadion"
    }:
        intent_query_map = {
            "info_stadion_gbla": "informasi umum stadion Gelora Bandung Lautan Api kapasitas",
            "peraturan_penonton_boleh": "barang yang boleh dibawa penonton ke stadion diizinkan",
            "peraturan_penonton_dilarang": "barang yang dilarang dibawa penonton larangan stadion",
            "sanksi_pelanggaran": "denda sanksi pelanggaran stadion GBLA",
            "fasilitas_stadion": "fasilitas stadion GBLA toilet musholla medis disabilitas",
            "info_parkir_stadion": "area parkir stadion GBLA kapasitas motor mobil bus",
            "info_tiket_stadion": "aturan tiket masuk stadion penonton anak-anak kategori",
            "info_media_stadion": "aturan media wartawan fotografer akreditasi drone stadion"
        }

        enriched_query = intent_query_map.get(intent, query)
        search_results = semantic_search(enriched_query, top_k=7)

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