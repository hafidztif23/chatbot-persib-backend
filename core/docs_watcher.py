import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.embeddings import embed_single_file, remove_tracker

SUPPORTED_EXT = {".txt", ".pdf", ".xlsx", ".xls", ".docx"}

class DocsEventHandler(FileSystemEventHandler):

    def _is_supported(self, filepath: str) -> bool:
        ext = os.path.splitext(filepath)[1].lower()
        return ext in SUPPORTED_EXT

    def on_created(self, event):
        if event.is_directory or not self._is_supported(event.src_path):
            return
        file_name = os.path.basename(event.src_path)
        print(f"[WATCHER] File baru terdeteksi: {file_name}")
        # Delay singkat agar file selesai ditulis sebelum dibaca
        time.sleep(1)
        embed_single_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not self._is_supported(event.src_path):
            return
        file_name = os.path.basename(event.src_path)
        print(f"[WATCHER] Perubahan terdeteksi: {file_name}")
        time.sleep(1)
        embed_single_file(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or not self._is_supported(event.src_path):
            return
        file_name = os.path.basename(event.src_path)
        print(f"[WATCHER] File dihapus: {file_name}")
        remove_tracker(file_name)

def start_docs_watcher(docs_folder: str = "docs"):
    event_handler = DocsEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=docs_folder, recursive=False)

    thread = threading.Thread(target=observer.start, daemon=True)
    thread.start()

    print(f"[WATCHER] Memantau folder '{docs_folder}' untuk perubahan...")
    return observer