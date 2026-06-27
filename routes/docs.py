import io
import os
import mimetypes
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/documents", tags=["documents"])

SUPPORTED_EXT = {".txt", ".pdf", ".xlsx", ".xls", ".docx"}


@router.get("")
def list_docs():
    """Ambil daftar semua dokumen di GCS bucket."""
    from core.storage import list_docs as gcs_list
    try:
        files = gcs_list()
        return {"total": len(files), "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar dokumen: {e}")


@router.post("", status_code=201)
async def upload_doc(file: UploadFile = File(...)):
    """Upload dokumen ke GCS dan langsung embed."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Format '{ext}' tidak didukung. Gunakan: {', '.join(SUPPORTED_EXT)}"
        )

    from core.storage import upload_doc as gcs_upload
    from core.embeddings import embed_single_file_from_bytes

    try:
        file_bytes = await file.read()
        content_type = file.content_type or "application/octet-stream"

        # Upload ke GCS
        gcs_result = gcs_upload(file.filename, file_bytes, content_type)

        # Langsung embed
        embed_single_file_from_bytes(file.filename, file_bytes)

        return {
            "message": f"File '{file.filename}' berhasil diupload ke GCS dan di-embed",
            "file": gcs_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal upload: {e}")


@router.get("/download/{file_name:path}")
def download_doc(file_name: str):
    """
    Download dokumen dari GCS langsung ke browser/client.
    Response berupa binary file dengan header Content-Disposition: attachment.
    """
    from core.storage import download_doc_bytes

    try:
        file_bytes = download_doc_bytes(file_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file_name}' tidak ditemukan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal download: {e}")

    content_type, _ = mimetypes.guess_type(file_name)
    content_type = content_type or "application/octet-stream"

    # Encode nama file untuk header agar aman dari karakter aneh
    safe_name = file_name.replace('"', '\\"')

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Content-Length": str(len(file_bytes)),
        }
    )


@router.delete("/{file_name:path}")
def delete_doc(file_name: str):
    """Hapus dokumen dari GCS dan hapus embedding-nya dari DB."""
    from core.storage import delete_doc_gcs
    from core.embeddings import remove_tracker
    from core.db import engine
    from sqlalchemy import text

    deleted = delete_doc_gcs(file_name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"File '{file_name}' tidak ditemukan di GCS")

    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM document_embeddings WHERE source_file = :n"),
                {"n": file_name}
            )
        remove_tracker(file_name)
    except Exception as e:
        # File sudah terhapus dari GCS, tapi gagal hapus embedding — log saja
        print(f"[DOCS DELETE] Warning: gagal hapus embedding {file_name}: {e}")

    return {
        "message": f"File '{file_name}' berhasil dihapus dari GCS beserta embedding-nya"
    }