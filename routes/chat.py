from fastapi import APIRouter, Depends
from pydantic import BaseModel
from langchain_classic.schema import HumanMessage
from core.config import CHATBOT_NAME, LANGUAGE_INSTRUCTION
from core.intents import detect_intent, extract_lawan, extract_nama_pemain, extract_posisi, extract_status_pemain, extract_tribun
from core.rag import llm
from core.memory import load_history, save_context, clear_history
from core.dependencies import get_current_account
from core.api_client import (
    get_merch_stock,
    get_jadwal_terdekat,
    get_jadwal_by_lawan,
    get_pemain_by_nama,
    get_pemain_by_posisi,
    get_pemain_by_status,
    semantic_search_api,
    get_stok_tiket_terdekat,
    get_stok_tiket_by_lawan
)

router = APIRouter()

item_map = {
    "stok_jersey": "Jersey Persib 2025",
    "stok_scarf":  "Scarf Maung Bandung",
    "stok_topi":   "Topi Persib"
}

class QueryRequest(BaseModel):
    query: str

def is_first_message(id_account: int) -> bool:
    history = load_history(id_account, limit=1)
    return len(history) == 0

@router.post("/chat")
def chat(
    req: QueryRequest,
    account: dict = Depends(get_current_account)
):
    query      = req.query
    id_account = account["id_account"]
    intent, score = detect_intent(query)

    history = load_history(id_account, limit=5)
    history_text = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Asisten'}: {m.content}"
        for m in history
    )

    if intent in item_map:
        item_name = item_map[intent]
        stock = get_merch_stock(item_name)
        
        if stock is not None:
            prompt = f"""
Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.
Data: Merchandise {item_name}, Stok saat ini: {stock} pcs.
Jawaban harus ramah dan langsung memberikan jumlah stok.
{LANGUAGE_INSTRUCTION}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'
"""
        else:
            prompt = f"""
Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
Data: Merchandise {item_name} tidak tersedia.
Jawaban harus ramah dan beri tahu user bahwa merchandise tidak ditemukan.
{LANGUAGE_INSTRUCTION}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "stok_tiket":
        nama_tribun = extract_tribun(query)
        data = get_stok_tiket_terdekat()

        if data and "tribun" in data:
            if nama_tribun:
                tribun_filter = [t for t in data["tribun"] if t["nama_tribun"] == nama_tribun]
                if tribun_filter:
                    detail_tribun = f"- {tribun_filter[0]['nama_tribun']}: {tribun_filter[0]['stok']:,} tiket"
                else:
                    detail_tribun = f"Data tribun '{nama_tribun}' tidak ditemukan."
            else:
                detail_tribun = "\n".join(
                    f"- {t['nama_tribun']}: {t['stok']:,} tiket"
                    for t in data["tribun"]
                )

            konteks = f"""Informasi stok tiket pertandingan terdekat:
Lawan: {data['lawan']}
Tanggal: {data['tanggal_jam']}
Status: {data['status_pertandingan']}
Stok tiket{f' tribun {nama_tribun}' if nama_tribun else ' per tribun'}:
{detail_tribun}
{f"Total stok semua tribun: {data['total_stok']:,} tiket" if not nama_tribun else ""}"""
        else:
            konteks = "Tidak ada data stok tiket untuk pertandingan yang akan datang."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{konteks}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "stok_tiket_by_jadwal":
        nama_lawan  = extract_lawan(query)
        nama_tribun = extract_tribun(query)
        data = get_stok_tiket_by_lawan(nama_lawan) if nama_lawan else None

        if data and "tribun" in data:
            if nama_tribun:
                tribun_filter = [t for t in data["tribun"] if t["nama_tribun"] == nama_tribun]
                detail_tribun = (
                    f"- {tribun_filter[0]['nama_tribun']}: {tribun_filter[0]['stok']:,} tiket"
                    if tribun_filter else f"Data tribun '{nama_tribun}' tidak ditemukan."
                )
            else:
                detail_tribun = "\n".join(
                    f"- {t['nama_tribun']}: {t['stok']:,} tiket"
                    for t in data["tribun"]
                )

            konteks = f"""Informasi stok tiket pertandingan Persib vs {data['lawan']}:
Tanggal: {data['tanggal_jam']}
Status: {data['status_pertandingan']}
Stok tiket{f' tribun {nama_tribun}' if nama_tribun else ' per tribun'}:
{detail_tribun}
{f"Total stok semua tribun: {data['total_stok']:,} tiket" if not nama_tribun else ""}"""
        else:
            konteks = f"Tidak ada data stok tiket untuk pertandingan melawan '{nama_lawan}'."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{konteks}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent in {
        "cara_beli_tiket",
        "kebijakan_pembatalan_tiket",
        "kebijakan_data_pembeli",
        "kebijakan_evoucher",
        "kebijakan_privasi"
    }:
        intent_query_map = {
            "cara_beli_tiket":            "cara beli tiket Persib jalur resmi aplikasi website",
            "kebijakan_pembatalan_tiket": "pembatalan tiket refund pengembalian uang potongan administrasi",
            "kebijakan_data_pembeli":     "data pembeli NIK nama email nomor handphone tidak bisa diubah",
            "kebijakan_evoucher":         "e-voucher barcode gelang penanda penukaran tiket elektronik",
            "kebijakan_privasi":          "kebijakan privasi data konsumen penggunaan data keamanan kontak"
        }
        enriched_query = intent_query_map.get(intent, query)
        search_results = semantic_search_api(enriched_query, top_k=5)
        context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results) if search_results else "Tidak ada informasi yang relevan ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah dan helpful.
{LANGUAGE_INSTRUCTION}
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
    
    elif intent == "info_jadwal_terdekat":
        jadwal = get_jadwal_terdekat()
        data_jadwal = f"""Pertandingan terdekat:
- Lawan: {jadwal['lawan']}
- Tanggal: {jadwal['tanggal_jam']}
- Lokasi: {jadwal['lokasi']}
- Kompetisi: {jadwal['kompetisi']}
- Status: {jadwal['status_pertandingan']}""" if jadwal else "Tidak ada jadwal pertandingan yang akan datang."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_jadwal}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
        
    elif intent == "info_jadwal":
        nama_lawan  = extract_lawan(query)
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

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_jadwal}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "info_pemain":
        nama   = extract_nama_pemain(query)
        pemain = get_pemain_by_nama(nama) if nama else None

        data_pemain = f"""Data pemain:
- Nama: {pemain['nama_pemain']}
- Nomor Punggung: {pemain['nomor_punggung']}
- Posisi: {pemain['posisi']}
- Kewarganegaraan: {pemain['kewarganegaraan']}
- Tanggal Lahir: {pemain['tanggal_lahir']}
- Status: {pemain['status']}""" if pemain else f"Pemain dengan nama '{nama}' tidak ditemukan di skuad Persib."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_pemain}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "info_pemain_posisi":
        posisi      = extract_posisi(query)
        pemain_list = get_pemain_by_posisi(posisi) if posisi else []

        data_pemain = (
            f"Daftar pemain posisi {posisi}:\n" +
            "\n".join(f"- #{p['nomor_punggung']} {p['nama_pemain']} ({p['kewarganegaraan']})" for p in pemain_list)
        ) if pemain_list else f"Tidak ada data pemain untuk posisi '{posisi}'."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_pemain}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "info_pemain_status":
        status      = extract_status_pemain(query)
        pemain_list = get_pemain_by_status(status) if status else []

        data_pemain = (
            f"Daftar pemain dengan status {status}:\n" +
            "\n".join(f"- #{p['nomor_punggung']} {p['nama_pemain']} ({p['posisi']})" for p in pemain_list)
        ) if pemain_list else f"Tidak ada pemain dengan status '{status}'."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
{LANGUAGE_INSTRUCTION}
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.

{data_pemain}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
    
    elif intent in {
        "info_sejarah",
        "info_sejarah_awal",
        "info_sejarah_era_perserikatan",
        "info_sejarah_era_liga_indonesia",
        "info_sejarah_era_liga_super",
        "info_sejarah_era_liga1",
        "info_prestasi_juara",
        "info_pemain_legenda"
    }:
        intent_query_map = {
            "info_sejarah":                    "sejarah umum Persib Bandung asal-usul berdiri",
            "info_sejarah_awal":               "BIVB asal-usul berdiri Persib 1919 1933 pendiri ketua",
            "info_sejarah_era_perserikatan":   "Persib era Perserikatan juara 1937 1961 1986 1994 pemain pelatih",
            "info_sejarah_era_liga_indonesia": "Persib Liga Indonesia 1994 1995 juara Piala Champions Asia",
            "info_sejarah_era_liga_super":     "Persib Liga Super Indonesia LSI 2014 juara final Persipura",
            "info_sejarah_era_liga1":          "Persib Liga 1 juara 2023 2024 2025 Bojan Hodak David da Silva",
            "info_prestasi_juara":             "gelar juara Persib trofi prestasi kompetisi liga piala",
            "info_pemain_legenda":             "pemain legenda bersejarah Persib Robby Darwis Adjat Sudradjat Djadjang",
        }
        enriched_query = intent_query_map.get(intent, query)
        search_results = semantic_search_api(enriched_query, top_k=6)
        context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results) if search_results else "Tidak ada informasi yang relevan ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah dan helpful.
{LANGUAGE_INSTRUCTION}
Gunakan HANYA informasi dari konteks berikut untuk menjawab.
Jika informasi tidak ada di konteks, katakan dengan jujur bahwa kamu tidak tahu.
Sampaikan dengan gaya bercerita yang menarik, tidak sekadar menyebutkan fakta kering.

Konteks:
{context}

Riwayat percakapan sebelumnya:
{history_text}
 
Pertanyaan: {query}
Jawaban:"""
        
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
        intent_query_map = {
            "info_membersib":           "MemberSIB program keanggotaan digital Persib",
            "info_passport_persib":     "Passport Persib program keanggotaan premium",
            "benefit_membersib":        "manfaat keuntungan benefit MemberSIB",
            "benefit_passport_persib":  "manfaat keuntungan benefit Passport Persib",
            "harga_keanggotaan":        "harga biaya keanggotaan MemberSIB Passport Persib",
            "cara_daftar_membersib":    "cara daftar pendaftaran MemberSIB",
            "cara_daftar_passport":     "cara daftar pendaftaran Passport Persib",
            "perbandingan_keanggotaan": "perbedaan MemberSIB Passport Persib perbandingan"
        }
        enriched_query = intent_query_map.get(intent, query)
        search_results = semantic_search_api(enriched_query, top_k=5)
        context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results) if search_results else "Tidak ada informasi yang relevan ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah dan helpful.
{LANGUAGE_INSTRUCTION}
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
            "info_stadion_gbla":           "informasi umum stadion Gelora Bandung Lautan Api kapasitas",
            "peraturan_penonton_boleh":    "barang yang boleh dibawa penonton ke stadion diizinkan",
            "peraturan_penonton_dilarang": "barang yang dilarang dibawa penonton larangan stadion",
            "sanksi_pelanggaran":          "denda sanksi pelanggaran stadion GBLA",
            "fasilitas_stadion":           "fasilitas stadion GBLA toilet musholla medis disabilitas",
            "info_parkir_stadion":         "area parkir stadion GBLA kapasitas motor mobil bus",
            "info_tiket_stadion":          "aturan tiket masuk stadion penonton anak-anak kategori",
            "info_media_stadion":          "aturan media wartawan fotografer akreditasi drone stadion"
        }
        enriched_query = intent_query_map.get(intent, query)
        search_results = semantic_search_api(enriched_query, top_k=7)
        context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results) if search_results else "Tidak ada informasi yang relevan ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah dan helpful.
{LANGUAGE_INSTRUCTION}
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

    elif intent == "greeting":
        if is_first_message(id_account):
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
Ini adalah pertama kali user menyapa. Sapa user dengan menyebut namanya: {account['nama_lengkap']}.
Perkenalkan dirimu dengan hangat dan sebutkan bahwa kamu bisa membantu informasi seputar
Persib Bandung seperti jadwal pertandingan, data pemain, stok merchandise, keanggotaan,
dan informasi stadion GBLA.

Pertanyaan user: '{query}'"""
        else:
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User menyapa kembali. Balas sapaannya dengan menyebut namanya: {account['nama_lengkap']}.
Tanyakan apa yang bisa kamu bantu.

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "farewell":
        prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
Balas perpisahan dari {account['nama_lengkap']} dengan hangat dan sopan.
Sampaikan bahwa kamu siap membantu kapan saja jika butuh informasi tentang Persib lagi.

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
    
    elif intent == "tentang_chatbot":
        prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
{'Perkenalkan dirimu dan jelaskan' if is_first_message(id_account) else 'Jelaskan'} hal-hal yang bisa kamu bantu:
- Informasi jadwal pertandingan Persib
- Data dan profil pemain Persib
- Stok merchandise resmi Persib
- Informasi keanggotaan MemberSIB dan Passport Persib
- Peraturan dan fasilitas Stadion GBLA
- Sejarah dan informasi umum Persib Bandung

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
    
    elif intent == "bantuan":
        prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
{'Perkenalkan dirimu singkat lalu jelaskan' if is_first_message(id_account) else 'Jelaskan'} cara menggunakan chatbot ini.
Berikan contoh pertanyaan seperti:
- "Kapan Persib main lagi?"
- "Stok jersey Persib masih ada?"
- "Siapa saja striker Persib?"
- "Apa benefit MemberSIB?"
- "Boleh bawa flare ke stadion?"

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()
    
    elif intent == "thanks":
        prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME} yang ramah.
{LANGUAGE_INSTRUCTION}
Balas ucapan terima kasih dari {account['nama_lengkap']} dengan hangat dan sopan.

Pertanyaan user: '{query}'"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "konfirmasi_positif":
        prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User memberikan konfirmasi positif. Respons singkat dan tanyakan apakah ada hal lain yang bisa dibantu.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    elif intent == "konfirmasi_negatif":
        prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User menyatakan informasi kurang tepat. Minta maaf singkat dan tawarkan untuk mencoba lagi.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

    else:
        search_results = semantic_search_api(query, top_k=3)
        context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results) if search_results else "Tidak ada informasi yang relevan ditemukan."

        prompt = f"""Kamu adalah asisten Persib Bandung yang ramah dan helpful.
{LANGUAGE_INSTRUCTION}
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

    save_context(id_account, query, answer)

    return {
        "intent":   intent,
        "score":    score,
        "response": answer
    }


# ─────────────────────────────────────────
# DELETE HISTORY — hanya milik sendiri
# ─────────────────────────────────────────

@router.delete("/chat/history/me")
def delete_my_history(account: dict = Depends(get_current_account)):
    """Hapus seluruh riwayat chat milik user yang sedang login."""
    clear_history(account["id_account"])
    return {"message": "Riwayat chat berhasil dihapus."}