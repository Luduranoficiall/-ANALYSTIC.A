# ============================================
# file: auth.py
# ============================================
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, Request
import os

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


# Simulação de usuário
USERS = {
    "admin@aliancia.com": {"password": "123456", "role": "admin"},
}


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def login_user(email: str, password: str):
    user = USERS.get(email)
    if not user or user["password"] != password:
        return None

    return create_access_token({"sub": email})


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Não autenticado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(401, "Token inválido")
