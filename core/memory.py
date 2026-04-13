from langchain_classic.memory import ConversationBufferWindowMemory

# Simpan memory per session_id
memory_store = {}

def get_memory(session_id: str) -> ConversationBufferWindowMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferWindowMemory(
            k=5,  # ingat 5 percakapan terakhir
            memory_key="chat_history",
            return_messages=True
        )
    return memory_store[session_id]