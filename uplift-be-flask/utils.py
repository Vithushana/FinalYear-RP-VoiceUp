import os
import time
import bcrypt
import jwt
from dotenv import load_dotenv
from typing import Optional, Dict  # ✅ for Python 3.8 compatibility

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))


def hash_password(password: str) -> bytes:
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed)
    except Exception:
        return False


def make_jwt(payload: dict) -> str:
    """Generate a JWT token with expiration and issued-at times."""
    now = int(time.time())
    exp = now + JWT_EXPIRES_MIN * 60
    body = {**payload, "iat": now, "exp": exp}
    return jwt.encode(body, JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> Optional[Dict]:
    """Decode and verify a JWT token. Returns dict if valid, else None."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None
