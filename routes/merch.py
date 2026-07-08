from fastapi import APIRouter
from sqlalchemy import text
from core.db import engine

router = APIRouter()

@router.get("/merchandise")
def get_merchandise():
    items = []
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT name, stock, harga_merchandise FROM merchandise")).mappings().all()
        for row in rows:
            items.append({
                "name": row["name"], 
                "stock": row["stock"],
                "harga_merchandise": row.get("harga_merchandise") or 0
            })
    return {"merchandise": items}