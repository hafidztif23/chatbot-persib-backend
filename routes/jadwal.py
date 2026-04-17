from fastapi import APIRouter, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.db import get_jadwal_pertandingan, get_jadwal_terdekat, engine
from sqlalchemy import text

router = APIRouter()

# ─────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────

class JadwalCreate(BaseModel):
    lawan: str
    tanggal_jam: datetime
    lokasi: Optional[str] = "Stadion Bandung Lautan Api"
    kompetisi: Optional[str] = "BRI Super League"
    status_pertandingan: Optional[str] = "Akan Datang"

class JadwalUpdate(BaseModel):
    lawan: Optional[str] = None
    tanggal_jam: Optional[datetime] = None
    lokasi: Optional[str] = None
    kompetisi: Optional[str] = None
    status_pertandingan: Optional[str] = None

# ─────────────────────────────────────────
# GET
# ─────────────────────────────────────────

@router.get("/jadwal")
def get_jadwal(status: str = Query(None, description="Filter: 'Akan Datang', 'Selesai', 'Ditunda'")):
    jadwal = get_jadwal_pertandingan(status=status)
    return {"jadwal": jadwal}

@router.get("/jadwal/terdekat")
def jadwal_terdekat():
    jadwal = get_jadwal_terdekat()
    if not jadwal:
        return {"message": "Tidak ada pertandingan yang akan datang"}
    return {"jadwal": jadwal}

# ─────────────────────────────────────────
# POST
# ─────────────────────────────────────────

@router.post("/jadwal", status_code=201)
def insert_jadwal(data: JadwalCreate):
    valid_status = {"Akan Datang", "Selesai", "Ditunda"}
    if data.status_pertandingan not in valid_status:
        return {"error": f"status_pertandingan harus salah satu dari: {valid_status}"}

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                INSERT INTO jadwal_pertandingan (lawan, tanggal_jam, lokasi, kompetisi, status_pertandingan)
                VALUES (:lawan, :tanggal_jam, :lokasi, :kompetisi, :status_pertandingan)
                RETURNING id_jadwal
            """),
            {
                "lawan": data.lawan,
                "tanggal_jam": data.tanggal_jam,
                "lokasi": data.lokasi,
                "kompetisi": data.kompetisi,
                "status_pertandingan": data.status_pertandingan
            }
        )
        conn.commit()
        new_id = result.fetchone()[0]

    return {
        "message": "Jadwal berhasil ditambahkan",
        "id_jadwal": new_id,
        "data": {
            "lawan": data.lawan,
            "tanggal_jam": data.tanggal_jam.strftime("%d %B %Y, %H:%M WIB"),
            "lokasi": data.lokasi,
            "kompetisi": data.kompetisi,
            "status_pertandingan": data.status_pertandingan
        }
    }

# ─────────────────────────────────────────
# PUT
# ─────────────────────────────────────────

@router.put("/jadwal/{id_jadwal}")
def update_jadwal(id_jadwal: int, data: JadwalUpdate):
    # Bangun query dinamis, hanya update field yang dikirim
    fields = {}
    if data.lawan is not None:
        fields["lawan"] = data.lawan
    if data.tanggal_jam is not None:
        fields["tanggal_jam"] = data.tanggal_jam
    if data.lokasi is not None:
        fields["lokasi"] = data.lokasi
    if data.kompetisi is not None:
        fields["kompetisi"] = data.kompetisi
    if data.status_pertandingan is not None:
        valid_status = {"Akan Datang", "Selesai", "Ditunda"}
        if data.status_pertandingan not in valid_status:
            return {"error": f"status_pertandingan harus salah satu dari: {valid_status}"}
        fields["status_pertandingan"] = data.status_pertandingan

    if not fields:
        return {"error": "Tidak ada field yang diupdate"}

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    fields["id_jadwal"] = id_jadwal

    with engine.connect() as conn:
        result = conn.execute(
            text(f"UPDATE jadwal_pertandingan SET {set_clause} WHERE id_jadwal = :id_jadwal"),
            fields
        )
        conn.commit()

        if result.rowcount == 0:
            return {"error": f"Jadwal dengan id_jadwal {id_jadwal} tidak ditemukan"}

    return {"message": f"Jadwal id {id_jadwal} berhasil diupdate"}

# ─────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────

@router.delete("/jadwal/{id_jadwal}")
def delete_jadwal(id_jadwal: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM jadwal_pertandingan WHERE id_jadwal = :id_jadwal"),
            {"id_jadwal": id_jadwal}
        )
        conn.commit()

        if result.rowcount == 0:
            return {"error": f"Jadwal dengan id_jadwal {id_jadwal} tidak ditemukan"}

    return {"message": f"Jadwal id {id_jadwal} berhasil dihapus"}