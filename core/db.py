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