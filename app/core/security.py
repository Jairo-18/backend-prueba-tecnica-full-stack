# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models.models import User

# ==========================================================
# 🔒 Configuración de seguridad
# ==========================================================

# Contexto de encriptación de contraseñas usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticación: Bearer token (en vez de OAuth2PasswordBearer)
bearer_scheme = HTTPBearer()


# ==========================================================
# 🗝️ Manejo de contraseñas
# ==========================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash almacenado.

    - `plain_password`: Contraseña en texto plano ingresada por el usuario.
    - `hashed_password`: Hash almacenado en la base de datos.

    Retorna:
    - `True` si coincide, `False` si no.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro a partir de una contraseña en texto plano.

    - `password`: Contraseña ingresada por el usuario.

    Retorna:
    - `str`: Hash de la contraseña (bcrypt).
    """
    return pwd_context.hash(password)


# ==========================================================
# 🔑 Manejo de tokens JWT
# ==========================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un access token (JWT) firmado con la clave secreta.

    - `data`: Diccionario con los datos a codificar en el token (ej: {"sub": "username"}).
    - `expires_delta`: Tiempo de expiración del token (por defecto usa `ACCESS_TOKEN_EXPIRE_MINUTES`).

    Retorna:
    - `str`: Token JWT firmado.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Añadimos fecha de expiración y de emisión
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================================
# 👤 Dependencia para autenticación de usuarios
# ==========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que valida el token Bearer y devuelve el usuario autenticado.

    - Extrae el token JWT del encabezado `Authorization: Bearer <token>`.
    - Decodifica el token con la clave secreta.
    - Obtiene el `username` del payload (`sub`).
    - Busca el usuario en la base de datos.
    - Si el token es inválido o el usuario no existe, lanza `401 Unauthorized`.

    Retorna:
    - Objeto `User` correspondiente al usuario autenticado.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Buscar usuario en la base de datos
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user
