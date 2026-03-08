"""Auth helpers: password hashing and JWT."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from .config import settings

# Prefer bcrypt; fall back to PBKDF2 if bcrypt fails (e.g. on some Windows setups)
_using_bcrypt = False
try:
    import bcrypt
    _using_bcrypt = True
except Exception:
    bcrypt = None


def hash_password(password: str) -> str:
    if _using_bcrypt:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2${salt}${key.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    if _using_bcrypt:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    if not hashed.startswith("pbkdf2$"):
        return False
    _, salt, stored = hashed.split("$", 2)
    key = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), 100000)
    return secrets.compare_digest(key.hex(), stored)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
