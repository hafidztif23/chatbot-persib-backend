import os
import bcrypt
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# CONFIG
SECRET_KEY                  = os.getenv("JWT_SECRET_KEY", "ganti-ini-dengan-secret-yang-kuat")
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# PASSWORD
def hash_password(plain_password: str) -> str:
    """Hash plain-text password menggunakan bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Bandingkan plain-text password dengan hash-nya."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

# JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Buat JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Dekode dan validasi JWT token.

    Raises:
        JWTError jika token tidak valid atau kadaluarsa.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])