# ============================================
# file: auth.py — ANALYSTIC.A PRO ULTRA SECURE
# ============================================
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Request
from fastapi.responses import RedirectResponse
import os
import hashlib
import json

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Arquivo para persistir usuários (em produção use um banco de dados)
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _hash_password(password: str) -> str:
    """Hash simples de senha (em produção use bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    """Carrega usuários do arquivo JSON"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Usuários padrão
    default_users = {
        "admin@aliancia.com": {"password": _hash_password("123456"), "name": "Admin Aliança", "role": "admin"},
        "admin@analystic.a": {"password": _hash_password("admin123"), "name": "Admin", "role": "admin"},
        "demo@analystic.a": {"password": _hash_password("demo123"), "name": "Demo User", "role": "user"},
    }
    _save_users(default_users)
    return default_users


def _save_users(users: dict):
    """Salva usuários no arquivo JSON"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


# Carregar usuários ao iniciar
USERS = _load_users()


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register_user(email: str, password: str, name: str) -> dict:
    """Registra um novo usuário"""
    global USERS
    
    email = email.lower().strip()
    
    if email in USERS:
        return {"success": False, "error": "E-mail já cadastrado"}
    
    USERS[email] = {
        "password": _hash_password(password),
        "name": name,
        "role": "user",
        "created_at": datetime.utcnow().isoformat()
    }
    
    _save_users(USERS)
    
    return {"success": True, "message": "Usuário criado com sucesso"}


def login_user(email: str, password: str):
    email = email.lower().strip()
    user = USERS.get(email)
    
    if not user:
        return None
    
    # Verificar senha (hash ou texto puro para retrocompatibilidade)
    hashed = _hash_password(password)
    if user["password"] != hashed and user["password"] != password:
        return None

    return create_access_token({"sub": email, "name": user.get("name", "User")})


def get_current_user(request: Request):
    """Retorna o usuário atual ou None se não autenticado"""
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        return None


def get_current_user_or_redirect(request: Request):
    """Retorna o usuário atual ou redireciona para login"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return user
