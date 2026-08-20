from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
from datetime import datetime

from core.db import engine
from core.dependencies import get_current_account

router = APIRouter(prefix="/eskalasi", tags=["eskalasi"])

# SCHEMA
class JawabanCSRequest(BaseModel):
    jawaban: str

# HELPER
def _format_eskalasi(row: dict) -> dict:
    return {
        "id_fallback":      row["id_fallback"],
        "id_account":       row["id_account"],
        "nama_lengkap":     row.get("nama_lengkap"),
        "email":            row.get("email"),
        "id_history":       row["id_history"],
        "pertanyaan":       row.get("content"),           # dari JOIN ke chat_history
        "jawaban":          row["jawaban"],
        "status":           row["status"],
        "created_at":       str(row["created_at"]) if row.get("created_at") else None,
        "answered_at":      str(row["answered_at"]) if row.get("answered_at") else None,
    }

# GET — semua eskalasi (untuk CS / admin)
@router.get("")
def get_all_eskalasi(
    status: Optional[str] = Query(
        None,
        description="Filter: 'pending', 'answered'"
    )
):
    """
    Ambil semua pertanyaan yang dieskalasi.
    Gunakan ?status=pending untuk yang belum dijawab,
    ?status=answered untuk yang sudah dijawab.
    """
    base_query = """
        SELECT
            e.id_fallback,
            ch.session_id AS id_account,
            a.nama_lengkap,
            a.email,
            e.id_history,
            ch.content,
            e.jawaban,
            e.status,
            e.created_at,
            e.answered_at
        FROM eskalasi e
        JOIN chat_history  ch ON ch.id          = e.id_history
        JOIN accounts      a  ON a.id_account   = ch.session_id
    """
    params = {}
    if status:
        base_query += " WHERE e.status = :status"
        params["status"] = status

    base_query += " ORDER BY e.created_at DESC"

    with engine.connect() as conn:
        rows = conn.execute(text(base_query), params).mappings().all()

    return {
        "total": len(rows),
        "data":  [_format_eskalasi(dict(r)) for r in rows]
    }


# GET — 1 eskalasi by id
@router.get("/{id_fallback}")
def get_eskalasi_by_id(id_fallback: int):
    """Ambil detail satu tiket eskalasi."""
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT
                    e.id_fallback,
                    ch.session_id AS id_account,
                    a.nama_lengkap,
                    a.email,
                    e.id_history,
                    ch.content,
                    e.jawaban,
                    e.status,
                    e.created_at,
                    e.answered_at
                FROM eskalasi e
                JOIN chat_history  ch ON ch.id          = e.id_history
                JOIN accounts      a  ON a.id_account   = ch.session_id
                WHERE e.id_fallback = :id_fallback
            """),
            {"id_fallback": id_fallback}
        ).mappings().fetchone()

    if not row:
        return {"error": f"Eskalasi dengan id {id_fallback} tidak ditemukan"}

    return _format_eskalasi(dict(row))

# GET — eskalasi milik user yg login
@router.get("/me/history")
def get_my_eskalasi(account: dict = Depends(get_current_account)):
    """
    Ambil seluruh tiket eskalasi milik user yang sedang login,
    termasuk jawaban dari CS jika sudah ada.
    """
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    e.id_fallback,
                    ch.session_id AS id_account,
                    e.id_history,
                    ch.content,
                    e.jawaban,
                    e.status,
                    e.created_at,
                    e.answered_at
                FROM eskalasi e
                JOIN chat_history ch ON ch.id = e.id_history
                WHERE ch.session_id = :id_account
                ORDER BY e.created_at DESC
            """),
            {"id_account": account["id_account"]}
        ).mappings().all()

    return {
        "total": len(rows),
        "data": [
            {
                "id_fallback":  r["id_fallback"],
                "id_history":   r["id_history"],
                "pertanyaan":   r["content"],
                "jawaban":      r["jawaban"],
                "status":       r["status"],
                "created_at":   str(r["created_at"]) if r["created_at"] else None,
                "answered_at":  str(r["answered_at"]) if r["answered_at"] else None,
            }
            for r in rows
        ]
    }

# POST — CS menjawab satu tiket eskalasi
@router.post("/{id_fallback}/jawab")
def jawab_eskalasi(id_fallback: int, data: JawabanCSRequest):
    """
    Tim Customer Service mengisi jawaban untuk satu tiket eskalasi.
    Status otomatis berubah menjadi 'answered'.
    """
    with engine.connect() as conn:
        existing = conn.execute(
            text("SELECT id_fallback, status FROM eskalasi WHERE id_fallback = :id"),
            {"id": id_fallback}
        ).mappings().fetchone()

        if not existing:
            return {"error": f"Eskalasi dengan id {id_fallback} tidak ditemukan"}

        if existing["status"] == "answered":
            return {"error": "Tiket ini sudah dijawab sebelumnya"}

        conn.execute(
            text("""
                UPDATE eskalasi
                SET jawaban     = :jawaban,
                    status      = 'answered',
                    answered_at = NOW()
                WHERE id_fallback = :id_fallback
            """),
            {"jawaban": data.jawaban, "id_fallback": id_fallback}
        )
        conn.commit()

    return {
        "message":     f"Jawaban untuk tiket eskalasi id {id_fallback} berhasil disimpan",
        "id_fallback": id_fallback,
        "status":      "answered"
    }

# DELETE — hapus tiket eskalasi
@router.delete("/{id_fallback}")
def delete_eskalasi(id_fallback: int):
    """Hapus satu tiket eskalasi (misalnya duplikat / spam)."""
    with engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM eskalasi WHERE id_fallback = :id"),
            {"id": id_fallback}
        )
        conn.commit()

        if result.rowcount == 0:
            return {"error": f"Eskalasi dengan id {id_fallback} tidak ditemukan"}

    return {"message": f"Tiket eskalasi id {id_fallback} berhasil dihapus"}