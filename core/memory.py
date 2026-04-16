from sqlalchemy import text
from langchain_classic.schema import HumanMessage, AIMessage
from core.db import engine

def save_message(session_id: str, role: str, content: str):
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO chat_history (session_id, role, content)
                VALUES (:session_id, :role, :content)
            """),
            {"session_id": session_id, "role": role, "content": content}
        )
        conn.commit()

def load_history(session_id: str, limit: int = 5):
    """Ambil N percakapan terakhir per session"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT role, content FROM (
                    SELECT role, content, created_at
                    FROM chat_history
                    WHERE session_id = :session_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                ) sub
                ORDER BY created_at ASC
            """),
            {"session_id": session_id, "limit": limit * 2}  # *2 karena 1 giliran = human + ai
        ).mappings().all()

    messages = []
    for row in rows:
        if row["role"] == "human":
            messages.append(HumanMessage(content=row["content"]))
        else:
            messages.append(AIMessage(content=row["content"]))
    return messages

def save_context(session_id: str, human_input: str, ai_output: str):
    """Simpan 1 giliran percakapan (human + ai)"""
    save_message(session_id, "human", human_input)
    save_message(session_id, "ai", ai_output)

def clear_history(session_id: str):
    """Hapus semua history untuk session tertentu"""
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM chat_history WHERE session_id = :session_id"),
            {"session_id": session_id}
        )
        conn.commit()