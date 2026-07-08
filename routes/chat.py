from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator, Field
from langchain_core.messages import HumanMessage
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
from core.db import create_eskalasi, get_last_human_history_id

router = APIRouter()

item_map = {
    "stok_jersey": "Jersey Persib 2025",
    "stok_scarf":  "Scarf Maung Bandung",
    "stok_topi":   "Topi Persib"
}

# Pesan fallback standar yang ditampilkan ke user
FALLBACK_MESSAGE = (
    """Maaf, saya belum dapat menemukan informasi yang tepat untuk pertanyaan Anda.
Pertanyaan Anda telah kami catat dan akan segera ditindaklanjuti oleh tim
Customer Service Persib Bandung. Anda juga dapat menghubungi CS kami secara
langsung melalui jalur resmi yang tersedia. Terima kasih atas kesabaran Anda!"""
)

SIMILARITY_THRESHOLD = 0.70
RAG_TOP_K = 5

class QueryRequest(BaseModel):
    query: str = Field(
        ..., 
        max_length=500, 
        min_length=1, 
        description="Input pertanyaan dari user, maksimal 500 karakter."
    )

    @field_validator("query")
    @classmethod
    def validate_spaces(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Pertanyaan tidak boleh kosong atau hanya spasi.")
        return v.strip()

def is_first_message(id_account: int) -> bool:
    history = load_history(id_account, limit=1)
    return len(history) == 0

def _escalate(id_account: int, query: str) -> None:
    """Simpan pertanyaan user ke tabel eskalasi."""
    try:
        id_history = get_last_human_history_id(id_account)
        if id_history:
            create_eskalasi(id_account=id_account, id_history=id_history)
    except Exception as exc:
        print(f"[ESKALASI ERROR] id_account={id_account} | {exc}")

def _safe_llm_invoke(messages) -> tuple[str, bool]:
    try:
        response = llm.invoke(messages)
        return response.content.strip(), False
    except Exception as e:
        print(f"[LLM ERROR] HuggingFace API gagal: {type(e).__name__}: {e}")
        return "", True


@router.post("/chat")
def chat(
    req: QueryRequest,
    account: dict = Depends(get_current_account)
):
    """Chat endpoint utama MaungBot."""
    # Shadow LANGUAGE_INSTRUCTION dynamically based on user's referensi_generate setting
    ref_generate = account.get("referensi_generate", 1)
    if ref_generate == 2:
        LANGUAGE_INSTRUCTION = "Always answer in natural, friendly, and helpful English. Keep the tone warm and easy to understand."
    else:
        LANGUAGE_INSTRUCTION = globals()["LANGUAGE_INSTRUCTION"]

    try:
        query      = req.query
        id_account = account["id_account"]

        fallback = False

        # Muat riwayat percakapan
        history = load_history(id_account, limit=5)
        if history:
            history_text = "\n".join(
                f"{'User' if getattr(m, 'type', '') == 'human' or isinstance(m, HumanMessage) else 'Asisten'}: {getattr(m, 'content', '')}"
                for m in history
            )
        else:
            history_text = "Belum ada percakapan sebelumnya."

        # Deteksi Intent
        try:
            intent, score = detect_intent(query)
        except Exception as e:
            print(f"[Intent Detection Error] {e}")
            intent = "general"
            score = 0.0


        # INTENT: Cek Merchandise (DB)
        if intent in item_map:
            item_name = item_map[intent]
            stock = get_merch_stock(item_name)

            if stock is not None:
                prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
Gunakan hanya informasi berikut untuk menjawab pertanyaan user.
Data: Merchandise {item_name}, Stok saat ini: {stock} pcs.
Jawaban harus ramah dan langsung memberikan jumlah stok.
{LANGUAGE_INSTRUCTION}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""
            else:
                prompt = f"""Kamu adalah asisten Persib Bandung bernama {CHATBOT_NAME} yang ramah, singkat, dan natural.
Data: Merchandise {item_name} tidak tersedia.
Jawaban harus ramah dan beri tahu user bahwa merchandise tidak ditemukan.
{LANGUAGE_INSTRUCTION}

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Stok tiket terdekat (DB)
        elif intent == "stok_tiket":
            nama_tribun = extract_tribun(query)
            data = get_stok_tiket_terdekat()

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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Stok tiket by lawan (DB)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Jadwal terdekat (DB)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Jadwal by lawan (DB)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Info pemain by nama (DB)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Pemain by posisi (DB)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Pemain by status (DB)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # ROUTING: CONVERSATIONAL (LLM only, no DB, no RAG)
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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        elif intent == "farewell":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
Balas perpisahan dari {account['nama_lengkap']} dengan hangat dan sopan.
Sampaikan bahwa kamu siap membantu kapan saja jika butuh informasi tentang Persib lagi.

Pertanyaan user: '{query}'"""

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        elif intent == "thanks":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME} yang ramah.
{LANGUAGE_INSTRUCTION}
Balas ucapan terima kasih dari {account['nama_lengkap']} dengan hangat dan sopan.

Pertanyaan user: '{query}'"""

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

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

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        elif intent == "konfirmasi_positif":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User memberikan konfirmasi positif. Respons singkat dan tanyakan apakah ada hal lain yang bisa dibantu.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        elif intent == "konfirmasi_negatif":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User menyatakan informasi kurang tepat. Minta maaf singkat dan tawarkan untuk mencoba lagi.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

            answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
            if llm_failed:
                fallback = True

        # INTENT: Eskalasi eksplisit — user sendiri yang minta dihubungkan ke CS
        elif intent == "fallback_eskalasi":
            fallback = True
            answer = ""

        else:
            search_results = semantic_search_api(query, top_k=RAG_TOP_K, min_similarity=SIMILARITY_THRESHOLD)

            if not search_results:
                fallback = True
                answer = ""
            else:
                context = "\n\n".join(
                    f"[Sumber: {r['source']}]\n{r['content']}"
                    for r in search_results
                )
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
                answer, llm_failed = _safe_llm_invoke([HumanMessage(content=prompt)])
                if llm_failed:
                    fallback = True

        # ==========================================
        # PENYELESAIAN & PENYIMPANAN
        # ==========================================
        final_answer = FALLBACK_MESSAGE if fallback else answer
        save_context(id_account, query, final_answer)

        if fallback:
            _escalate(id_account, query)

        return {
            "intent":    intent,
            "score":     score,
            "response":  final_answer,
            "escalated": fallback
        }

    except Exception as e:
        print(f"[Chat Error Fatal] {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "intent": "error",
            "score": 0.0,
            "response": "Maaf, ada kesalahan internal saat memproses pertanyaan Anda. Silakan coba lagi.",
            "escalated": False,
            "error": str(e)
        }


# DELETE HISTORY — hanya milik sendiri
@router.delete("/chat/history/me")
def delete_my_history(account: dict = Depends(get_current_account)):
    """Hapus seluruh riwayat chat milik user yang sedang login."""
    clear_history(account["id_account"])
    return {"message": "Riwayat chat berhasil dihapus."}