from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets
from app.core.security import get_current_user
from app.database import get_db
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.models import User
from app.models.models import RefreshToken
from app.auth.schemas import LoginRequest, TokenResponse

router = APIRouter()

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(login: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    
    if not user or not verify_password(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Crear refresh token
    refresh_token_str = secrets.token_urlsafe(32)
    refresh_token = RefreshToken(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token_str
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    # Obtener rol relacionado
    role = None
    if user.role_type:
        role = {  "code": user.role_type.code, "name": user.role_type.name}

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "role": role,  # <-- aquí va el rol
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "fullName": user.fullName
        }
    }


# Cerrar sesión
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Buscar todos los refresh tokens activos del usuario y revocarlos
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id
    ).all()

    for token in tokens:
        db.delete(token)

    db.commit()
    return {"message": "Sesión cerrada correctamente"}
