import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()

INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "maungbot")
DATABASE_URL = os.getenv("DATABASE_URL")

if INSTANCE_CONNECTION_NAME and DB_PASSWORD:
    # Production: pakai Cloud SQL Python Connecto

    connector = Connector()

    def getconn():
        return connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
        )

    engine = create_engine("postgresql+pg8000://", creator=getconn)
    print("Connected to Cloud SQL via Python Connector")

elif DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    print("Connected via DATABASE_URL")

else:
    # Fallback lokal: SQLite
    engine = create_engine(
        "sqlite:///./chatbot.db",
        connect_args={"check_same_thread": False}
    )
    print("⚠ Menggunakan SQLite (development)")

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

def get_jadwal_by_lawan(nama_lawan: str):
    """Cari jadwal pertandingan berdasarkan nama lawan (partial match)"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id_jadwal, lawan, tanggal_jam, lokasi, kompetisi, status_pertandingan
                FROM jadwal_pertandingan
                WHERE LOWER(lawan) LIKE LOWER(:nama_lawan)
                ORDER BY tanggal_jam ASC
            """),
            {"nama_lawan": f"%{nama_lawan}%"}
        ).mappings().all()

    if not rows:
        return None

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

def get_pemain_by_nama(nama: str):
    """Cari pemain berdasarkan nama (partial match)"""
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id_pemain, nama_pemain, nomor_punggung, posisi,
                       kewarganegaraan, tanggal_lahir, status
                FROM pemain
                WHERE LOWER(nama_pemain) LIKE LOWER(:nama)
                LIMIT 1
            """),
            {"nama": f"%{nama}%"}
        ).mappings().fetchone()

    if not row:
        return None

    return {
        "id_pemain": row["id_pemain"],
        "nama_pemain": row["nama_pemain"],
        "nomor_punggung": row["nomor_punggung"],
        "posisi": row["posisi"],
        "kewarganegaraan": row["kewarganegaraan"],
        "tanggal_lahir": row["tanggal_lahir"].strftime("%d %B %Y") if row["tanggal_lahir"] else None,
        "status": row["status"]
    }

def get_pemain_by_posisi(posisi: str):
    """Ambil semua pemain berdasarkan posisi"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id_pemain, nama_pemain, nomor_punggung, posisi,
                       kewarganegaraan, tanggal_lahir, status
                FROM pemain
                WHERE LOWER(posisi) = LOWER(:posisi)
                AND status = 'Aktif'
                ORDER BY nomor_punggung ASC
            """),
            {"posisi": posisi}
        ).mappings().all()

    return [
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

def get_pemain_by_status(status: str):
    """Ambil semua pemain berdasarkan status"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id_pemain, nama_pemain, nomor_punggung, posisi,
                       kewarganegaraan, status
                FROM pemain
                WHERE LOWER(status) = LOWER(:status)
                ORDER BY nomor_punggung ASC
            """),
            {"status": status}
        ).mappings().all()

    return [
        {
            "id_pemain": row["id_pemain"],
            "nama_pemain": row["nama_pemain"],
            "nomor_punggung": row["nomor_punggung"],
            "posisi": row["posisi"],
            "kewarganegaraan": row["kewarganegaraan"],
            "status": row["status"]
        }
        for row in rows
    ]

def get_stok_tiket(id_jadwal: int):
    """Ambil stok tiket per tribun untuk pertandingan tertentu"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT t.nama_tribun, t.stok, t.harga_tiket, j.lawan, j.tanggal_jam, j.status_pertandingan
                FROM ticket t
                JOIN jadwal_pertandingan j ON t.id_jadwal = j.id_jadwal
                WHERE t.id_jadwal = :id_jadwal
                ORDER BY t.nama_tribun
            """),
            {"id_jadwal": id_jadwal}
        ).mappings().all()

    if not rows:
        return None

    first = rows[0]
    return {
        "id_jadwal": id_jadwal,
        "lawan": first["lawan"],
        "tanggal_jam": first["tanggal_jam"].strftime("%d %B %Y, %H:%M WIB"),
        "status_pertandingan": first["status_pertandingan"],
        "tribun": [
            {
                "nama_tribun": r["nama_tribun"], 
                "stok": r["stok"], 
                "harga_tiket": r.get("harga_tiket") or 0
            }
            for r in rows
        ],
        "total_stok": sum(r["stok"] for r in rows)
    }

def get_stok_tiket_terdekat():
    """Ambil stok tiket untuk pertandingan terdekat yang akan datang"""
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id_jadwal FROM jadwal_pertandingan
                WHERE status_pertandingan = 'Akan Datang'
                ORDER BY tanggal_jam ASC
                LIMIT 1
            """)
        ).mappings().fetchone()

    if not row:
        return None

    return get_stok_tiket(row["id_jadwal"])

def get_stok_tiket_by_lawan(nama_lawan: str):
    """Ambil stok tiket berdasarkan nama lawan (partial match), prioritas yang akan datang"""
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id_jadwal FROM jadwal_pertandingan
                WHERE LOWER(lawan) LIKE LOWER(:nama_lawan)
                ORDER BY
                    CASE WHEN status_pertandingan = 'Akan Datang' THEN 0 ELSE 1 END,
                    tanggal_jam ASC
                LIMIT 1
            """),
            {"nama_lawan": f"%{nama_lawan}%"}
        ).mappings().fetchone()

    if not row:
        return None

    return get_stok_tiket(row["id_jadwal"])

def create_eskalasi(id_account: int, id_history: int) -> int:
    """
    Simpan satu tiket eskalasi ke tabel eskalasi.
    Mengembalikan id_fallback yang baru dibuat.
    """
    # Gunakan engine.begin()
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO eskalasi (id_account, id_history)
                VALUES (:id_account, :id_history)
                RETURNING id_fallback
            """),
            {"id_account": id_account, "id_history": id_history}
        )
        return result.fetchone()[0]
 
 
def get_last_human_history_id(id_account: int) -> int | None:
    """
    Ambil id terbaru dari chat_history milik id_account dengan role = 'human'.
    Digunakan setelah save_message() untuk mendapatkan id_history bagi eskalasi.
    """
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id FROM chat_history
                WHERE session_id = :id_account AND role = 'human'
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"id_account": id_account}
        ).fetchone()
    return row[0] if row else None