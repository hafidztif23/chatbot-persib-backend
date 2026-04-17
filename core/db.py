import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def check_merch_stock(item_name: str):
    item_name = item_name.strip().title()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT stock FROM merchandise WHERE name = :name"),
            {"name": item_name}
        ).mappings().fetchone()
        if row:
            return row['stock']
        return None
    
def get_jadwal_pertandingan(status: str = None):
    """Ambil semua jadwal, bisa difilter by status"""
    with engine.connect() as conn:
        if status:
            rows = conn.execute(
                text("""
                    SELECT id_jadwal, lawan, tanggal_jam, lokasi, kompetisi, status_pertandingan
                    FROM jadwal_pertandingan
                    WHERE status_pertandingan = :status
                    ORDER BY tanggal_jam ASC
                """),
                {"status": status}
            ).mappings().all()
        else:
            rows = conn.execute(
                text("""
                    SELECT id_jadwal, lawan, tanggal_jam, lokasi, kompetisi, status_pertandingan
                    FROM jadwal_pertandingan
                    ORDER BY tanggal_jam ASC
                """)
            ).mappings().all()

    return [
        {
            "id_jadwal": row["id_jadwal"],
            "lawan": row["lawan"],
            "tanggal_jam": row["tanggal_jam"].strftime("%d %B %Y, %H:%M WIB"),
            "lokasi": row["lokasi"],
            "kompetisi": row["kompetisi"],
            "status_pertandingan": row["status_pertandingan"]
        }
        for row in rows
    ]

def get_jadwal_terdekat():
    """Ambil 1 pertandingan terdekat yang akan datang"""
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id_jadwal, lawan, tanggal_jam, lokasi, kompetisi, status_pertandingan
                FROM jadwal_pertandingan
                WHERE status_pertandingan = 'Akan Datang'
                ORDER BY tanggal_jam ASC
                LIMIT 1
            """)
        ).mappings().fetchone()

    if not row:
        return None

    return {
        "id_jadwal": row["id_jadwal"],
        "lawan": row["lawan"],
        "tanggal_jam": row["tanggal_jam"].strftime("%d %B %Y, %H:%M WIB"),
        "lokasi": row["lokasi"],
        "kompetisi": row["kompetisi"],
        "status_pertandingan": row["status_pertandingan"]
    }