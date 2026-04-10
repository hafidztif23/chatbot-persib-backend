from fastapi import APIRouter
from sqlalchemy import text
from core.db import engine

router = APIRouter()

@router.get("/status")
def status():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
        db_status = "OK" if result else "FAIL"
    except Exception:
        db_status = "FAIL"
    return {"status": "running", "database": db_status}