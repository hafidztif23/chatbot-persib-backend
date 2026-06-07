from fastapi import APIRouter, Depends
from pydantic import BaseModel
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

# Threshold similarity untuk fallback
SIMILARITY_THRESHOLD = 0.60   # skor di bawah ini dianggap tidak relevan

class QueryRequest(BaseModel):
    query: str

def is_first_message(id_account: int) -> bool:
    history = load_history(id_account, limit=1)
    return len(history) == 0

def _is_context_relevant(search_results: list) -> bool:
    """
    Kembalikan True jika setidaknya satu hasil pencarian
    memiliki similarity di atas threshold.
    """
    if not search_results:
        return False
    return any(r.get("similarity", 0) >= SIMILARITY_THRESHOLD for r in search_results)

def _escalate(id_account: int, query: str) -> None:
    """
    Simpan pertanyaan user ke tabel eskalasi setelah pesan 'human'
    sudah tersimpan di chat_history.
    """
    try:
        id_history = get_last_human_history_id(id_account)
        if id_history:
            create_eskalasi(id_account=id_account, id_history=id_history)
    except Exception as exc:
        # Eskalasi gagal tidak boleh menghentikan respons ke user
        print(f"[ESKALASI ERROR] id_account={id_account} | {exc}")

@router.post("/chat")
def chat(
    req: QueryRequest,
    account: dict = Depends(get_current_account)
):
    """Chat endpoint utama MaungBot."""
    try:
        query      = req.query
        id_account = account["id_account"]
        
        # 1. Inisialisasi variabel wajib
        fallback = False
        
        # 2. Muat riwayat percakapan (MENGGUNAKAN LOGIKA LAMA YANG BENAR)
        history = load_history(id_account, limit=5)
        if history:
            history_text = "\n".join(
                f"{'User' if getattr(m, 'type', '') == 'human' or isinstance(m, HumanMessage) else 'Asisten'}: {getattr(m, 'content', '')}"
                for m in history
            )
        else:
            history_text = "Belum ada percakapan sebelumnya."

        # 3. Deteksi Intent
        try:
            intent, score = detect_intent(query)
        except Exception as e:
            print(f"[Intent Detection Error] {e}")
            intent = "general"
            score = 0.0

        # ==========================================
        # MULAI RANTAI ROUTING INTENT
        # ==========================================

        # INTENT: Cek Merchandise
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
            
            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip()

        # INTENT: stok tiket (terdekat)
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

        # INTENT: stok tiket by lawan
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

        # INTENT: kebijakan tiket
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

            context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results)
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

        # INTENT: jadwal terdekat
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

        # INTENT: jadwal by lawan
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

        # INTENT: info pemain
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

        # INTENT: pemain by posisi
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

        # INTENT: pemain by status
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

        # INTENT: sejarah & prestasi (RAG)
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

            context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results)
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

        # INTENT: keanggotaan MemberSIB / Passport (RAG)
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

            context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results)
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

        # INTENT: stadion GBLA (RAG)
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

            context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results)
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

        # INTENT: greeting
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

        # INTENT: farewell
        elif intent == "farewell":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
Balas perpisahan dari {account['nama_lengkap']} dengan hangat dan sopan.
Sampaikan bahwa kamu siap membantu kapan saja jika butuh informasi tentang Persib lagi.

Pertanyaan user: '{query}'"""

            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip()

        # INTENT: tentang chatbot
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

        # INTENT: bantuan
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

        # INTENT: thanks
        elif intent == "thanks":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME} yang ramah.
{LANGUAGE_INSTRUCTION}
Balas ucapan terima kasih dari {account['nama_lengkap']} dengan hangat dan sopan.

Pertanyaan user: '{query}'"""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip()

        # INTENT: konfirmasi positif
        elif intent == "konfirmasi_positif":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User memberikan konfirmasi positif. Respons singkat dan tanyakan apakah ada hal lain yang bisa dibantu.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip()

        # INTENT: konfirmasi negatif
        elif intent == "konfirmasi_negatif":
            prompt = f"""Kamu adalah asisten virtual Persib Bandung bernama {CHATBOT_NAME}.
{LANGUAGE_INSTRUCTION}
User menyatakan informasi kurang tepat. Minta maaf singkat dan tawarkan untuk mencoba lagi.

Riwayat percakapan sebelumnya:
{history_text}

Pertanyaan user: '{query}'"""

            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip()
        
        elif intent == "fallback_eskalasi":
            fallback = True
            answer = ""

        # FALLBACK AKHIR — intent "general" atau tidak dikenali
        else:
            search_results = semantic_search_api(query, top_k=3)

            if not _is_context_relevant(search_results):
                # Tidak ada konteks yang relevan → langsung eskalasi
                fallback = True
            else:
                context = "\n\n".join(f"[Sumber: {r['source']}]\n{r['content']}" for r in search_results)
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