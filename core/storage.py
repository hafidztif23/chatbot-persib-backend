import os
import io
import hashlib
from typing import Optional
from google.cloud import storage

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "maungbot-docs")
SUPPORTED_EXT = {".txt", ".pdf", ".docx"}


def _get_client() -> storage.Client:
    return storage.Client()


def list_docs() -> list[dict]:
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    result = []
    for blob in bucket.list_blobs():
        ext = os.path.splitext(blob.name)[1].lower()
        if ext not in SUPPORTED_EXT:
            continue
        result.append({
            "name": blob.name,
            "size_bytes": blob.size,
            "updated": blob.updated.isoformat() if blob.updated else None,
            "md5_hash": blob.md5_hash,
            "content_type": blob.content_type,
        })
    return result


def upload_doc(file_name: str, file_bytes: bytes, content_type: str = "application/octet-stream") -> dict:
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_bytes, content_type=content_type)
    blob.reload()
    return {
        "name": blob.name,
        "size_bytes": len(file_bytes),
        "content_type": content_type,
        "md5_hash": blob.md5_hash,
    }


def download_doc_bytes(file_name: str) -> bytes:
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    if not blob.exists():
        raise FileNotFoundError(f"File '{file_name}' tidak ditemukan di GCS")
    return blob.download_as_bytes()


def delete_doc_gcs(file_name: str) -> bool:
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    if not blob.exists():
        return False
    blob.delete()
    return True


def get_all_doc_hashes() -> dict[str, str]:
    """Return {blob_name: md5_hash} untuk semua file yang didukung di bucket."""
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    result = {}
    for blob in bucket.list_blobs():
        ext = os.path.splitext(blob.name)[1].lower()
        if ext in SUPPORTED_EXT:
            result[blob.name] = blob.md5_hash or ""
    return result


def compute_md5(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()