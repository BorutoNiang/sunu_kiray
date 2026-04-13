from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os

load_dotenv()

ALGORITHM = "HS256"
bearer    = HTTPBearer(auto_error=False)

def _secret() -> str:
    return os.getenv("JWT_SECRET", "fallback_secret_change_me")

def _expire() -> int:
    return int(os.getenv("JWT_EXPIRE", 86400))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=_expire())
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[ALGORITHM])

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Token manquant.")
    try:
        data = decode_token(credentials.credentials)
        # sub est stocké en string, on le remet en int pour les requêtes SQL
        if "sub" in data:
            data["sub"] = int(data["sub"])
        return data
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")

def require_role(*roles: str):
    def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Accès refusé.")
        return user
    return checker
