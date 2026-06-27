import os
from google.cloud import storage

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "maungbot-docs")
DOCS_FOLDER = "docs"

def sync_docs_from_gcs():
    """Download semua PDF dari GCS bucket ke folder docs lokal"""
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs()

        os.makedirs(DOCS_FOLDER, exist_ok=True)

        downloaded = 0
        for blob in blobs:
            local_path = os.path.join(DOCS_FOLDER, blob.name)
            if not os.path.exists(local_path):
                blob.download_to_filename(local_path)
                print(f"[GCS] Downloaded: {blob.name}")
                downloaded += 1

        print(f"[GCS] Sync selesai. {downloaded} file baru diunduh.")
    except Exception as e:
        print(f"[GCS] Sync gagal: {e}")