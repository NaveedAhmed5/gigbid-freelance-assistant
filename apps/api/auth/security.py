"""Authentication, JWT token lifecycle, and Tenant-Scoped Fernet Encryption."""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "gigbid-insecure-dev-secret-key-change-in-prod-1234")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
FERNET_KEY = os.getenv("OAUTH_FERNET_KEY", "").encode("utf-8")
if len(FERNET_KEY) < 32:
    FERNET_KEY = Fernet.generate_key()

cipher_suite = Fernet(FERNET_KEY)
security = HTTPBearer(auto_error=False)

PRELOADED_REVIEWER = {
    "user_id": "usr_reviewer_01",
    "email": os.getenv("REVIEWER_EMAIL", "reviewer@gigbid.ai"),
    "password_hash": hashlib.sha256(
        os.getenv("REVIEWER_PASSWORD", "reviewer-demo-pass").encode("utf-8")
    ).hexdigest(),
    "role": "reviewer",
    "tenant_id": "tenant_default",
    "active_persona": "ai_ml_engineer",
}

USERS_DB: Dict[str, Dict[str, Any]] = {
    PRELOADED_REVIEWER["email"]: PRELOADED_REVIEWER,
}

TENANT_OAUTH_STORE: Dict[str, bytes] = {}


class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    tenant_id: str
    active_persona: str
    exp: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    if not credentials:
        # Fallback to demo reviewer for frictionless local UI & test runs
        return PRELOADED_REVIEWER
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    for u in USERS_DB.values():
        if u["user_id"] == user_id:
            return u
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")


def encrypt_oauth_token(tenant_id: str, plain_token: str) -> None:
    encrypted = cipher_suite.encrypt(plain_token.encode("utf-8"))
    TENANT_OAUTH_STORE[tenant_id] = encrypted


def clear_oauth_token(tenant_id: str) -> None:
    if tenant_id in TENANT_OAUTH_STORE:
        del TENANT_OAUTH_STORE[tenant_id]


def decrypt_oauth_token(tenant_id: str) -> Optional[str]:
    encrypted = TENANT_OAUTH_STORE.get(tenant_id)
    if not encrypted:
        return None
    return cipher_suite.decrypt(encrypted).decode("utf-8")
