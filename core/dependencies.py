from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy import text

from core.security import decode_access_token
from core.db import engine

# Skema Bearer token — otomatis baca header "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Dependency yang memvalidasi JWT dan mengembalikan data account dari DB.

    Cara pakai di route:
        @router.get("/protected")
        def protected_route(account: dict = Depends(get_current_account)):
            return {"user": account["email"]}

    Raises:
        401 jika token tidak valid / kadaluarsa.
        401 jika account tidak ditemukan di DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        id_account: str = payload.get("sub")
        if id_account is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ambil data account dari DB (exclude password)
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id_account, nama_lengkap, nik, email, nomor_telepon,
                       tanggal_lahir, jenis_kelamin, kota, membership, role, created_at
                FROM accounts
                WHERE id_account = :id_account
            """),
            {"id_account": int(id_account)},
        ).mappings().fetchone()

    if row is None:
        raise credentials_exception

    return dict(row)