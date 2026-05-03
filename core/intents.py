import json
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

with open("intents.json", "r", encoding="utf-8") as f:
    intents_data = json.load(f)

emb_model = SentenceTransformer("all-MiniLM-L6-v2")
intent_embeddings = {}

for intent in intents_data:
    ex_embeddings = [emb_model.encode(ex) for ex in intent["examples"]]
    intent_embeddings[intent["intent"]] = ex_embeddings

def detect_intent(user_query, threshold=0.55):
    query_emb = emb_model.encode(user_query)
    best_intent = None
    best_score = -1
    for intent, ex_emb_list in intent_embeddings.items():
        for ex_emb in ex_emb_list:
            score = float(cosine_similarity([query_emb], [ex_emb])[0][0])
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score < threshold:
        return "general", best_score

    return best_intent, best_score

def extract_lawan(query: str) -> str | None:
    """Ekstrak nama klub lawan dari query user"""
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower())

    stopwords = [
        # Kata dasar bawaan
        "pertandingan", "jadwal", "lawan", "kapan", "persib",
        "main", "vs", "melawan", "ketemu", "bertanding", "tanding",
        "bermain", "maen", "ari", "kalo", "kalau", "dengan", "sama",
        "tanggal", "berapa", "info", "el clasico", "dong", "min",
        "tandang", "ke", "markas", "laga", "home", "jam", "kickoff",
        "pangeran biru", "maung bandung", "menjamu", "away", "lengkap",
        "putaran", "kedua", "mana", "mau", "tau", "hari", "apa", "ya"
    ]

    for word in stopwords:
        query_clean = re.sub(rf'\b{word}\b', ' ', query_clean)

    result = re.sub(r'\s+', ' ', query_clean).strip()
    return result.title() if result else None

def extract_nama_pemain(query: str) -> str | None:
    """Ekstrak nama pemain dari query user"""
    stopwords = [
        "informasi", "tentang", "siapa", "itu", "profil", "pemain",
        "persib", "data", "bernama", "ceritakan", "nomor", "punggung"
    ]
    query_clean = query.lower()
    for word in stopwords:
        query_clean = query_clean.replace(word, "")

    result = re.sub(r'\s+', ' ', query_clean).strip()
    return result if result else None

def extract_posisi(query: str) -> str | None:
    """Ekstrak posisi dari query user"""
    posisi_map = {
        "kiper": "Kiper",
        "bek": "Bek",
        "gelandang": "Gelandang",
        "striker": "Penyerang",
        "penyerang": "Penyerang",
    }
    query_lower = query.lower()
    for keyword, posisi in posisi_map.items():
        if keyword in query_lower:
            return posisi
    return None

def extract_status_pemain(query: str) -> str | None:
    """Ekstrak status pemain dari query user"""
    status_map = {
        "cedera": "Cedera",
        "dipinjam": "Dipinjam",
        "pinjam": "Dipinjam",
        "aktif": "Aktif",
    }
    query_lower = query.lower()
    for keyword, status in status_map.items():
        if keyword in query_lower:
            return status
    return None