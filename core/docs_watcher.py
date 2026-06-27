import os
import threading
import time
from sqlalchemy import text
from core.db import engine

POLL_INTERVAL = int(os.getenv("GCS_POLL_INTERVAL", "30"))  # detik


def _remove_embeddings_from_db(file_name: str):
    from core.embeddings import remove_tracker
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM document_embeddings WHERE source_file = :n"),
            {"n": file_name}
        )
    remove_tracker(file_name)
    print(f"[WATCHER] Embeddings dihapus untuk: {file_name}")


def start_docs_watcher():
    def poll():
        from core.storage import get_all_doc_hashes, download_doc_bytes
        from core.embeddings import embed_single_file_from_bytes, compute_md5

        known_hashes: dict[str, str] = {}
        print(f"[WATCHER] Memulai polling GCS setiap {POLL_INTERVAL}s...")

        # Inisialisasi state awal tanpa re-embed (sudah di-embed saat startup)
        try:
            known_hashes = get_all_doc_hashes()
        except Exception as e:
            print(f"[WATCHER] Gagal inisialisasi state awal: {e}")

        while True:
            time.sleep(POLL_INTERVAL)
            try:
                current_hashes = get_all_doc_hashes()
                current_names = set(current_hashes.keys())
                known_names = set(known_hashes.keys())

                # File baru atau berubah
                for name in current_names:
                    old_hash = known_hashes.get(name)
                    new_hash = current_hashes[name]
                    if old_hash != new_hash:
                        action = "baru" if old_hash is None else "berubah"
                        print(f"[WATCHER] File {action}: {name}")
                        try:
                            file_bytes = download_doc_bytes(name)
                            embed_single_file_from_bytes(name, file_bytes)
                        except Exception as e:
                            print(f"[WATCHER ERROR] {name}: {e}")

                # File dihapus dari GCS
                for name in known_names - current_names:
                    print(f"[WATCHER] File dihapus dari GCS: {name}")
                    try:
                        _remove_embeddings_from_db(name)
                    except Exception as e:
                        print(f"[WATCHER ERROR] hapus embedding {name}: {e}")

                known_hashes = current_hashes

            except Exception as e:
                print(f"[WATCHER POLL ERROR] {e}")

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()
    print("[WATCHER] Thread polling GCS dimulai")
    return thread