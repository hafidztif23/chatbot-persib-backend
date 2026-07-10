import io
import os
import hashlib
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from core.db import engine

emb_model = SentenceTransformer("all-MiniLM-L6-v2")

SUPPORTED_EXT = {".txt", ".pdf", ".docx"}

FILE_CHUNK_CONFIG = {
    "sejarah.txt":                    {"chunk_size": 500,  "overlap": 50},
    "harga_keanggotaan.txt":          {"chunk_size": 500,  "overlap": 50},
    "membersib.pdf":                  {"chunk_size": 600,  "overlap": 75},
    "passport_persib.pdf":            {"chunk_size": 600,  "overlap": 75},
    "sejarah.pdf":                    {"chunk_size": 800,  "overlap": 100},
    "regulasi_stadion_gbla_2025.pdf": {"chunk_size": 900,  "overlap": 120},
}

DEFAULT_CHUNK_CONFIG = {"chunk_size": 600, "overlap": 75}
SIMILARITY_THRESHOLD = 0.40

# ──────────────────────────────────────────────
# HASH / TRACKER
# ──────────────────────────────────────────────

def compute_md5(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()


def is_already_embedded(file_name: str, file_hash: str) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT file_hash FROM docs_embedding_tracker WHERE file_name = :n"),
            {"n": file_name}
        ).fetchone()
    return bool(row and row[0] == file_hash)


def update_tracker(file_name: str, file_hash: str) -> int:
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                INSERT INTO docs_embedding_tracker (file_name, file_hash, last_embedded)
                VALUES (:n, :h, NOW())
                ON CONFLICT (file_name) DO UPDATE
                SET file_hash = :h, last_embedded = NOW()
                RETURNING id_docs_tracker
            """),
            {"n": file_name, "h": file_hash}
        ).fetchone()
        return row[0]


def remove_tracker(file_name: str):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM docs_embedding_tracker WHERE file_name = :n"),
            {"n": file_name}
        )


# ──────────────────────────────────────────────
# LOADERS (bytes-based)
# ──────────────────────────────────────────────

def _load_txt_bytes(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def _load_pdf_bytes(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return "\n".join(
        page.extract_text() for page in reader.pages if page.extract_text()
    )


def _load_docx_bytes(data: bytes) -> str:
    from docx import Document as DocxDocument
    doc = DocxDocument(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_file_from_bytes(file_name: str, data: bytes) -> str:
    ext = os.path.splitext(file_name)[1].lower()
    loaders = {
        ".txt":  _load_txt_bytes,
        ".pdf":  _load_pdf_bytes,
        ".docx": _load_docx_bytes,
    }
    if ext not in loaders:
        raise ValueError(f"Format file '{ext}' tidak didukung")
    return loaders[ext](data)


# ──────────────────────────────────────────────
# CHUNKING & EMBEDDING
# ──────────────────────────────────────────────

def chunk_text(content: str, chunk_size: int = 600, overlap: int = 75) -> list[str]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(content)


def embed_text(text: str) -> list:
    return emb_model.encode(text).tolist()


# ──────────────────────────────────────────────
# EMBED SINGLE FILE (dari bytes — dipakai watcher & upload endpoint)
# ──────────────────────────────────────────────

def embed_single_file_from_bytes(file_name: str, file_bytes: bytes, force: bool = False):
    file_hash = compute_md5(file_bytes)

    if not force and is_already_embedded(file_name, file_hash):
        print(f"[SKIP] {file_name} tidak ada perubahan")
        return

    print(f"[PROSES] {file_name}")

    try:
        content = load_file_from_bytes(file_name, file_bytes)
    except Exception as e:
        print(f"[ERROR] {file_name} gagal dibaca: {e}")
        return

    config = FILE_CHUNK_CONFIG.get(file_name, DEFAULT_CHUNK_CONFIG)
    chunks = chunk_text(content, chunk_size=config["chunk_size"], overlap=config["overlap"])
    print(f"  → chunk_size={config['chunk_size']}, overlap={config['overlap']}, total={len(chunks)} chunks")

    id_docs_tracker = update_tracker(file_name, file_hash)

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM document_embeddings WHERE source_file = :s"),
            {"s": file_name}
        )
        for idx, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            conn.execute(
                text("""
                    INSERT INTO document_embeddings (source_file, chunk_index, content, embedding, id_docs_tracker)
                    VALUES (:s, :i, :c, :e, :id_tracker)
                """),
                {
                    "s": file_name,
                    "i": idx,
                    "c": chunk,
                    "e": str(embedding),
                    "id_tracker": id_docs_tracker
                }
            )

    print(f"[OK] {file_name} → {len(chunks)} chunks disimpan")


# ──────────────────────────────────────────────
# STORE ALL (baca langsung dari GCS, bukan disk)
# ──────────────────────────────────────────────

def store_embeddings_from_docs(force: bool = False):
    from core.storage import list_docs, download_doc_bytes
    docs = list_docs()
    if not docs:
        print("[EMBED] Tidak ada dokumen di GCS bucket")
        return
    for doc in docs:
        file_name = doc["name"]
        try:
            file_bytes = download_doc_bytes(file_name)
            embed_single_file_from_bytes(file_name, file_bytes, force=force)
        except Exception as e:
            print(f"[EMBED ERROR] {file_name}: {e}")


# ──────────────────────────────────────────────
# SEMANTIC SEARCH
# ──────────────────────────────────────────────

def semantic_search(query: str, top_k: int = 5, min_similarity: float = SIMILARITY_THRESHOLD) -> list:
    query_embedding = embed_text(query)
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT source_file, content,
                       1 - (embedding <=> CAST(:e AS vector)) AS similarity
                FROM document_embeddings
                WHERE 1 - (embedding <=> CAST(:e AS vector)) >= :threshold
                ORDER BY embedding <=> CAST(:e AS vector)
                LIMIT :k
            """),
            {"e": str(query_embedding), "k": top_k, "threshold": min_similarity}
        ).mappings().all()

    return [
        {
            "source": row["source_file"],
            "content": row["content"],
            "similarity": round(float(row["similarity"]), 4)
        }
        for row in rows
    ]