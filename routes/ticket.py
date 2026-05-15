from fastapi import APIRouter
from core.db import get_stok_tiket, get_stok_tiket_terdekat, get_stok_tiket_by_lawan, engine
from sqlalchemy import text

router = APIRouter()

@router.get("/ticket/stok/terdekat")
def stok_tiket_terdekat():
    data = get_stok_tiket_terdekat()
    if not data:
        return {"message": "Tidak ada pertandingan yang akan datang"}
    return data

@router.get("/ticket/stok/lawan/{nama_lawan}")
def stok_tiket_by_lawan(nama_lawan: str):
    data = get_stok_tiket_by_lawan(nama_lawan)
    if not data:
        return {"error": f"Data tiket untuk lawan '{nama_lawan}' tidak ditemukan"}
    return data

@router.get("/ticket/stok/{id_jadwal}")
def stok_tiket_by_jadwal(id_jadwal: int):
    data = get_stok_tiket(id_jadwal)
    if not data:
        return {"error": f"Data tiket untuk id_jadwal {id_jadwal} tidak ditemukan"}
    return data

@router.put("/ticket/stok/{id_jadwal}/{nama_tribun}")
def update_stok(id_jadwal: int, nama_tribun: str, jumlah: int):
    """Kurangi stok tiket (misalnya setelah penjualan)"""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                UPDATE ticket SET stok = stok - :jumlah, updated_at = NOW()
                WHERE id_jadwal = :id_jadwal AND nama_tribun = :nama_tribun
                AND stok >= :jumlah
            """),
            {"id_jadwal": id_jadwal, "nama_tribun": nama_tribun, "jumlah": jumlah}
        )
        conn.commit()
        if result.rowcount == 0:
            return {"error": "Stok tidak cukup atau data tidak ditemukan"}
    return {"message": "Stok berhasil diupdate"}