from fastapi import APIRouter, Query
from pydantic import BaseModel
from datetime import date
from typing import Optional
from core.db import engine
from sqlalchemy import text

router = APIRouter()

# ─────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────

class PemainCreate(BaseModel):
    nama_pemain: str
    nomor_punggung: Optional[int] = None
    posisi: Optional[str] = None
    kewarganegaraan: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    status: Optional[str] = "Aktif"

class PemainUpdate(BaseModel):
    nama_pemain: Optional[str] = None
    nomor_punggung: Optional[int] = None
    posisi: Optional[str] = None
    kewarganegaraan: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    status: Optional[str] = None

# ─────────────────────────────────────────
# VALIDASI
# ─────────────────────────────────────────

VALID_POSISI = {"Kiper", "Bek", "Gelandang", "Penyerang"}
VALID_STATUS = {"Aktif", "Cedera", "Dipinjam"}

def validate_nomor_punggung(nomor: int):
    if not (1 <= nomor <= 99):
        return "Nomor punggung harus antara 1 sampai 99"
    return None

def validate_posisi(posisi: str):
    if posisi not in VALID_POSISI:
        return f"Posisi harus salah satu dari: {VALID_POSISI}"
    return None

def validate_status(status: str):
    if status not in VALID_STATUS:
        return f"Status harus salah satu dari: {VALID_STATUS}"
    return None

# ─────────────────────────────────────────
# GET
# ─────────────────────────────────────────

@router.get("/pemain")
def get_all_pemain(
    posisi: Optional[str] = Query(None, description="Filter: Kiper, Bek, Gelandang, Penyerang"),
    status: Optional[str] = Query(None, description="Filter: Aktif, Cedera, Dipinjam")
):
    query = "SELECT * FROM pemain WHERE 1=1"
    params = {}

    if posisi:
        query += " AND LOWER(posisi) = LOWER(:posisi)"
        params["posisi"] = posisi
    if status:
        query += " AND LOWER(status) = LOWER(:status)"
        params["status"] = status

    query += " ORDER BY nomor_punggung ASC"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    return {
        "total": len(rows),
        "pemain": [
            {
                "id_pemain": row["id_pemain"],
                "nama_pemain": row["nama_pemain"],
                "nomor_punggung": row["nomor_punggung"],
                "posisi": row["posisi"],
                "kewarganegaraan": row["kewarganegaraan"],
                "tanggal_lahir": row["tanggal_lahir"].strftime("%d %B %Y") if row["tanggal_lahir"] else None,
                "status": row["status"]
            }
            for row in rows
        ]
    }

@router.get("/pemain/{id_pemain}")
def get_pemain(id_pemain: int):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM pemain WHERE id_pemain = :id_pemain"),
            {"id_pemain": id_pemain}
        ).mappings().fetchone()

    if not row:
        return {"error": f"Pemain dengan id {id_pemain} tidak ditemukan"}

    return {
        "id_pemain": row["id_pemain"],
        "nama_pemain": row["nama_pemain"],
        "nomor_punggung": row["nomor_punggung"],
        "posisi": row["posisi"],
        "kewarganegaraan": row["kewarganegaraan"],
        "tanggal_lahir": row["tanggal_lahir"].strftime("%d %B %Y") if row["tanggal_lahir"] else None,
        "status": row["status"]
    }

# ─────────────────────────────────────────
# POST
# ─────────────────────────────────────────

@router.post("/pemain", status_code=201)
def insert_pemain(data: PemainCreate):
    if data.nomor_punggung:
        err = validate_nomor_punggung(data.nomor_punggung)
        if err:
            return {"error": err}

    if data.posisi:
        err = validate_posisi(data.posisi)
        if err:
            return {"error": err}

    if data.status:
        err = validate_status(data.status)
        if err:
            return {"error": err}

    with engine.connect() as conn:
        # Cek nomor punggung duplikat
        if data.nomor_punggung:
            existing = conn.execute(
                text("SELECT id_pemain FROM pemain WHERE nomor_punggung = :nomor"),
                {"nomor": data.nomor_punggung}
            ).fetchone()
            if existing:
                return {"error": f"Nomor punggung {data.nomor_punggung} sudah dipakai pemain lain"}

        result = conn.execute(
            text("""
                INSERT INTO pemain (nama_pemain, nomor_punggung, posisi, kewarganegaraan, tanggal_lahir, status)
                VALUES (:nama_pemain, :nomor_punggung, :posisi, :kewarganegaraan, :tanggal_lahir, :status)
                RETURNING id_pemain
            """),
            {
                "nama_pemain": data.nama_pemain,
                "nomor_punggung": data.nomor_punggung,
                "posisi": data.posisi,
                "kewarganegaraan": data.kewarganegaraan,
                "tanggal_lahir": data.tanggal_lahir,
                "status": data.status
            }
        )
        conn.commit()
        new_id = result.fetchone()[0]

    return {
        "message": "Pemain berhasil ditambahkan",
        "id_pemain": new_id,
        "data": {
            "nama_pemain": data.nama_pemain,
            "nomor_punggung": data.nomor_punggung,
            "posisi": data.posisi,
            "kewarganegaraan": data.kewarganegaraan,
            "tanggal_lahir": str(data.tanggal_lahir) if data.tanggal_lahir else None,
            "status": data.status
        }
    }

# ─────────────────────────────────────────
# PUT
# ─────────────────────────────────────────

@router.put("/pemain/{id_pemain}")
def update_pemain(id_pemain: int, data: PemainUpdate):
    fields = {}

    if data.nama_pemain is not None:
        fields["nama_pemain"] = data.nama_pemain
    if data.nomor_punggung is not None:
        err = validate_nomor_punggung(data.nomor_punggung)
        if err:
            return {"error": err}
        fields["nomor_punggung"] = data.nomor_punggung
    if data.posisi is not None:
        err = validate_posisi(data.posisi)
        if err:
            return {"error": err}
        fields["posisi"] = data.posisi
    if data.kewarganegaraan is not None:
        fields["kewarganegaraan"] = data.kewarganegaraan
    if data.tanggal_lahir is not None:
        fields["tanggal_lahir"] = data.tanggal_lahir
    if data.status is not None:
        err = validate_status(data.status)
        if err:
            return {"error": err}
        fields["status"] = data.status

    if not fields:
        return {"error": "Tidak ada field yang diupdate"}

    with engine.connect() as conn:
        # Cek pemain exists
        existing = conn.execute(
            text("SELECT id_pemain FROM pemain WHERE id_pemain = :id_pemain"),
            {"id_pemain": id_pemain}
        ).fetchone()
        if not existing:
            return {"error": f"Pemain dengan id {id_pemain} tidak ditemukan"}

        # Cek duplikat nomor punggung kalau diupdate
        if "nomor_punggung" in fields:
            duplicate = conn.execute(
                text("SELECT id_pemain FROM pemain WHERE nomor_punggung = :nomor AND id_pemain != :id"),
                {"nomor": fields["nomor_punggung"], "id": id_pemain}
            ).fetchone()
            if duplicate:
                return {"error": f"Nomor punggung {fields['nomor_punggung']} sudah dipakai pemain lain"}

        set_clause = ", ".join(f"{k} = :{k}" for k in fields)
        fields["id_pemain"] = id_pemain

        conn.execute(
            text(f"UPDATE pemain SET {set_clause} WHERE id_pemain = :id_pemain"),
            fields
        )
        conn.commit()

    return {"message": f"Pemain id {id_pemain} berhasil diupdate"}

# ─────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────

@router.delete("/pemain/{id_pemain}")
def delete_pemain(id_pemain: int):
    with engine.connect() as conn:
        existing = conn.execute(
            text("SELECT id_pemain, nama_pemain FROM pemain WHERE id_pemain = :id_pemain"),
            {"id_pemain": id_pemain}
        ).mappings().fetchone()

        if not existing:
            return {"error": f"Pemain dengan id {id_pemain} tidak ditemukan"}

        nama = existing["nama_pemain"]
        conn.execute(
            text("DELETE FROM pemain WHERE id_pemain = :id_pemain"),
            {"id_pemain": id_pemain}
        )
        conn.commit()

    return {"message": f"Pemain '{nama}' berhasil dihapus"}