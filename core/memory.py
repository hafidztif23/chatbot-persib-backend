from sqlalchemy import text
from langchain_classic.schema import HumanMessage, AIMessage
from core.db import engine

def save_message(id_account: int, role: str, content: str):
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO chat_history (session_id, role, content)
                VALUES (:id_account, :role, :content)
            """),
            {"id_account": id_account, "role": role, "content": content}
        )
        conn.commit()

def load_history(id_account: int, limit: int = 5):
    """Ambil N percakapan terakhir per account"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT role, content FROM (
                    SELECT role, content, created_at
                    FROM chat_history
                    WHERE session_id = :id_account
                    ORDER BY created_at DESC
                    LIMIT :limit
                ) sub
                ORDER BY created_at ASC
            """),
            {"id_account": id_account, "limit": limit * 2}
        ).mappings().all()
 
    messages = []
    for row in rows:
        if row["role"] == "human":
            messages.append(HumanMessage(content=row["content"]))
        else:
            messages.append(AIMessage(content=row["content"]))
    return messages

def save_context(id_account: int, human_input: str, ai_output: str):
    """Simpan 1 giliran percakapan (human + ai)"""
    save_message(id_account, "human", human_input)
    save_message(id_account, "ai", ai_output)

def clear_history(id_account: int):
    """Hapus semua history untuk account tertentu"""
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM chat_history WHERE session_id = :id_account"),
            {"id_account": id_account}
        )
        conn.commit()