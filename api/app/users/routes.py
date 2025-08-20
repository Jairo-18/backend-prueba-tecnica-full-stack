from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User
from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.core.security import get_current_user, get_password_hash

router = APIRouter()

# Crear usuario
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email o Username ya registrados")

    new_user = User(
        email=user.email,
        username=user.username,
        fullName=user.fullName,
        password=get_password_hash(user.password)  # 🔒 Hasheo aquí
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Obtener lista paginada de usuarios (protegido)
@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido con JWT
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Obtener un usuario por ID (protegido)
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Editar usuario (protegido)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user_update.email is not None:
        user.email = user_update.email
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.fullName is not None:
        user.fullName = user_update.fullName
    if user_update.password is not None:
        user.password = get_password_hash(user_update.password)  # 🔒 Hasheo

    db.commit()
    db.refresh(user)
    return user

# Eliminar usuario (protegido)
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(user)
    db.commit()
    return {"message": f"Usuario con id {user_id} eliminado"}
