from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from core.db import engine
from pypdf import PdfReader
import openpyxl
from docx import Document as DocxDocument
import os
import hashlib

emb_model = SentenceTransformer("all-MiniLM-L6-v2")

FILE_CHUNK_CONFIG = {
    # Dokumen pendek / ringkas → chunk kecil
    "sejarah.txt":              {"chunk_size": 500,  "overlap": 50},
    "harga_keanggotaan.txt":    {"chunk_size": 500,  "overlap": 50},
    "membersib.pdf":            {"chunk_size": 600,  "overlap": 75},
    "passport_persib.pdf":      {"chunk_size": 600,  "overlap": 75},

    "regulasi_stadion_gbla_2025.pdf": {"chunk_size": 900, "overlap": 120},
}

DEFAULT_CHUNK_CONFIG = {"chunk_size": 600, "overlap": 75}

def get_file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def is_already_embedded(file_name: str, file_hash: str) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT file_hash FROM docs_embedding_tracker WHERE file_name = :file_name"),
            {"file_name": file_name}
        ).fetchone()

    if not row:
        return False

    return row[0] == file_hash

def update_tracker(file_name: str, file_hash: str):
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO docs_embedding_tracker (file_name, file_hash, last_embedded)
                VALUES (:file_name, :file_hash, NOW())
                ON CONFLICT (file_name) DO UPDATE
                SET file_hash = :file_hash, last_embedded = NOW()
            """),
            {"file_name": file_name, "file_hash": file_hash}
        )
        conn.commit()

def remove_tracker(file_name: str):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM docs_embedding_tracker WHERE file_name = :file_name"),
            {"file_name": file_name}
        )
        conn.commit()

def embed_text(text: str) -> list:
    return emb_model.encode(text).tolist()

def load_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    return "\n".join(
        page.extract_text() for page in reader.pages if page.extract_text()
    )

def load_excel(filepath: str) -> str:
    wb = openpyxl.load_workbook(filepath, data_only=True)
    result = []
    for sheet in wb.worksheets:
        result.append(f"[Sheet: {sheet.title}]")
        for row in sheet.iter_rows(values_only=True):
            row_text = " | ".join(str(cell) for cell in row if cell is not None)
            if row_text.strip():
                result.append(row_text)
    return "\n".join(result)

def load_docx(filepath: str) -> str:
    doc = DocxDocument(filepath)
    return "\n".join(
        para.text for para in doc.paragraphs if para.text.strip()
    )

def load_file(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    loaders = {
        ".txt":  load_txt,
        ".pdf":  load_pdf,
        ".xlsx": load_excel,
        ".xls":  load_excel,
        ".docx": load_docx,
    }
    if ext not in loaders:
        raise ValueError(f"Format file '{ext}' tidak didukung")
    return loaders[ext](filepath)

def chunk_text(content: str, chunk_size: int = 600, overlap: int = 75) -> list:
    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunks.append(content[start:end])
        start += chunk_size - overlap
    return chunks

def embed_single_file(filepath: str, force: bool = False):
    file_name = os.path.basename(filepath)
    file_hash = get_file_hash(filepath)

    if not force and is_already_embedded(file_name, file_hash):
        print(f"[SKIP] {file_name} tidak ada perubahan")
        return

    print(f"[PROSES] {file_name}")

    try:
        content = load_file(filepath)
    except Exception as e:
        print(f"[ERROR] {file_name} gagal dibaca: {e}")
        return

    config = FILE_CHUNK_CONFIG.get(file_name, DEFAULT_CHUNK_CONFIG)
    chunks = chunk_text(content, chunk_size=config["chunk_size"], overlap=config["overlap"])

    print(f"  → chunk_size={config['chunk_size']}, overlap={config['overlap']}, total={len(chunks)} chunks")

    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM document_embeddings WHERE source_file = :source_file"),
            {"source_file": file_name}
        )
        for idx, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            conn.execute(
                text("""
                    INSERT INTO document_embeddings (source_file, chunk_index, content, embedding)
                    VALUES (:source_file, :chunk_index, :content, :embedding)
                """),
                {
                    "source_file": file_name,
                    "chunk_index": idx,
                    "content": chunk,
                    "embedding": str(embedding)
                }
            )
        conn.commit()

    update_tracker(file_name, file_hash)
    print(f"[OK] {file_name} → {len(chunks)} chunks disimpan")

def store_embeddings_from_docs(docs_folder: str = "docs", force: bool = False):
    supported_ext = {".txt", ".pdf", ".xlsx", ".xls", ".docx"}

    for file_name in os.listdir(docs_folder):
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in supported_ext:
            continue

        filepath = os.path.join(docs_folder, file_name)
        embed_single_file(filepath, force=force)

def semantic_search(query: str, top_k: int = 3) -> list:
    query_embedding = embed_text(query)
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT source_file, content,
                       1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM document_embeddings
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {"embedding": str(query_embedding), "top_k": top_k}
        ).mappings().all()

    return [
        {
            "source": row["source_file"],
            "content": row["content"],
            "similarity": round(float(row["similarity"]), 4)
        }
        for row in rows
    ]