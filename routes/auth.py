from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date
from sqlalchemy import text

from core.db import engine
from core.security import hash_password, verify_password, create_access_token
from core.dependencies import get_current_account

router = APIRouter(prefix="/auth", tags=["auth"])

# SCHEMA
class RegisterRequest(BaseModel):
    nama_lengkap:  str
    nik:           str
    email:         EmailStr
    nomor_telepon: str
    tanggal_lahir: date
    jenis_kelamin: str
    kota:          Optional[str] = None
    password:      str

    @field_validator("nik")
    @classmethod
    def nik_harus_16_digit(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 16:
            raise ValueError("NIK harus 16 digit angka")
        return v

    @field_validator("nomor_telepon")
    @classmethod
    def telepon_valid(cls, v: str) -> str:
        digits = v.replace("+", "").replace("-", "")
        if not digits.isdigit() or not (8 <= len(v) <= 13):
            raise ValueError("Nomor telepon tidak valid (maks 13 karakter)")
        return v

    @field_validator("jenis_kelamin")
    @classmethod
    def jenis_kelamin_valid(cls, v: str) -> str:
        if v not in {"Pria", "Wanita"}:
            raise ValueError("jenis_kelamin harus 'Pria' atau 'Wanita'")
        return v

    @field_validator("password")
    @classmethod
    def password_cukup_kuat(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    nama_lengkap:  Optional[str]  = None
    nomor_telepon: Optional[str]  = None
    tanggal_lahir: Optional[date] = None
    kota:          Optional[str]  = None

    @field_validator("nomor_telepon")
    @classmethod
    def telepon_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = v.replace("+", "").replace("-", "")
        if not digits.isdigit() or not (8 <= len(v) <= 13):
            raise ValueError("Nomor telepon tidak valid")
        return v

# HELPER
def _format_account(row: dict) -> dict:
    """Serialisasi row DB ke response dict (exclude password)."""
    return {
        "id_account":    row["id_account"],
        "nama_lengkap":  row["nama_lengkap"],
        "nik":           row["nik"],
        "email":         row["email"],
        "nomor_telepon": row["nomor_telepon"],
        "tanggal_lahir": str(row["tanggal_lahir"]) if row.get("tanggal_lahir") else None,
        "jenis_kelamin": row["jenis_kelamin"],
        "kota":          row["kota"],
        "membership":    row["membership"],
        "role":          row.get("role"),
        "created_at":    str(row["created_at"]) if row.get("created_at") else None,
    }

# REGISTER
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    """Daftarkan akun baru. Membership default = 'reguler'."""

    with engine.begin() as conn:
        # Cek duplikat email
        if conn.execute(
            text("SELECT 1 FROM accounts WHERE email = :email"),
            {"email": data.email},
        ).fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email sudah terdaftar.",
            )

        # Cek duplikat NIK
        if conn.execute(
            text("SELECT 1 FROM accounts WHERE nik = :nik"),
            {"nik": data.nik},
        ).fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="NIK sudah terdaftar.",
            )

        hashed = hash_password(data.password)

        result = conn.execute(
            text("""
                INSERT INTO accounts
                    (nama_lengkap, nik, email, nomor_telepon,
                     tanggal_lahir, jenis_kelamin, kota, password)
                VALUES
                    (:nama_lengkap, :nik, :email, :nomor_telepon,
                     :tanggal_lahir, :jenis_kelamin, :kota, :password)
                RETURNING id_account
            """),
            {
                "nama_lengkap":  data.nama_lengkap,
                "nik":           data.nik,
                "email":         data.email,
                "nomor_telepon": data.nomor_telepon,
                "tanggal_lahir": data.tanggal_lahir,
                "jenis_kelamin": data.jenis_kelamin,
                "kota":          data.kota,
                "password":      hashed,
            },
        )
        new_id = result.fetchone()[0]

    return {
        "message":    "Registrasi berhasil.",
        "id_account": new_id,
    }

# LOGIN
@router.post("/login")
def login(data: LoginRequest):
    """Login dengan email + password. Mengembalikan JWT access token."""

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM accounts WHERE email = :email"),
            {"email": data.email},
        ).mappings().fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
        )

    if not verify_password(data.password, row["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
        )

    token = create_access_token({"sub": str(row["id_account"])})

    return {
        "access_token": token,
        "token_type":   "bearer",
        "account":      _format_account(dict(row)),
    }

# PROFILE (protected)
@router.get("/me")
def get_profile(account: dict = Depends(get_current_account)):
    """Ambil profil account yang sedang login."""
    return {"account": _format_account(account)}


@router.put("/me")
def update_profile(
    data: UpdateProfileRequest,
    account: dict = Depends(get_current_account),
):
    """Update sebagian field profil (nama, telepon, tanggal lahir, kota)."""

    fields: dict = {}
    if data.nama_lengkap  is not None: fields["nama_lengkap"]  = data.nama_lengkap
    if data.nomor_telepon is not None: fields["nomor_telepon"] = data.nomor_telepon
    if data.tanggal_lahir is not None: fields["tanggal_lahir"] = data.tanggal_lahir
    if data.kota          is not None: fields["kota"]          = data.kota

    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak ada field yang diupdate.",
        )

    fields["id_account"] = account["id_account"]
    set_clause = ", ".join(f"{k} = :{k}" for k in fields if k != "id_account")
    set_clause += ", updated_at = NOW()"

    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE accounts SET {set_clause} WHERE id_account = :id_account"),
            fields,
        )

    return {"message": "Profil berhasil diupdate."}