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
    # Verificar si el usuario o email ya existe
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        else:
            raise HTTPException(status_code=400, detail="El username ya está registrado")

    try:
        # ✅ SOLUCIÓN: Asignar role_type_id por defecto si no viene
        default_role_id = getattr(user, 'role_type_id', None) or 1  # 1 = Usuario por defecto
        
        new_user = User(
            email=user.email,
            username=user.username,
            fullName=user.fullName,
            password=get_password_hash(user.password),  # 🔒 Hasheo aquí
            role_type_id=default_role_id  # ✅ Agregar el rol
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creando usuario: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor: {str(e)}"
        )

# Obtener lista paginada de usuarios con respuesta estructurada
@router.get("/")
def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido con JWT
):
    """
    Obtener lista paginada de usuarios con información de paginación
    """
    try:
        # Obtener el total de registros
        total = db.query(User).count()
        
        # Obtener los registros paginados
        users = db.query(User).offset(skip).limit(limit).all()
        
        # Convertir a formato de respuesta
        users_response = [UserResponse.from_orm(user) for user in users]
        
        return {
            "users": users_response,
            "total": total,
            "skip": skip,
            "limit": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except Exception as e:
        print(f"❌ Error listando usuarios: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo usuarios: {str(e)}"
        )

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

# Editar usuario (protegido) - MEJORADO
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

    try:
        # ✅ MEJORAR: Verificar duplicados solo si se cambia email/username
        if user_update.email is not None and user_update.email != user.email:
            existing_email = db.query(User).filter(
                User.email == user_update.email,
                User.id != user_id  # Excluir el usuario actual
            ).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="El email ya está en uso")
            user.email = user_update.email

        if user_update.username is not None and user_update.username != user.username:
            existing_username = db.query(User).filter(
                User.username == user_update.username,
                User.id != user_id  # Excluir el usuario actual
            ).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="El username ya está en uso")
            user.username = user_update.username

        # Actualizar otros campos
        if user_update.fullName is not None:
            user.fullName = user_update.fullName
            
        # ✅ MEJORAR: Solo hashear si se proporciona nueva contraseña
        if user_update.password is not None and user_update.password.strip():
            user.password = get_password_hash(user_update.password)  # 🔒 Hasheo
        
        # ✅ AGREGAR: Actualizar rol si se proporciona
        if hasattr(user_update, 'role_type_id') and user_update.role_type_id is not None:
            user.role_type_id = user_update.role_type_id

        db.commit()
        db.refresh(user)
        return user
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error actualizando usuario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando usuario: {str(e)}"
        )

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

    try:
        db.delete(user)
        db.commit()
        return {"message": f"Usuario con id {user_id} eliminado correctamente"}
    except Exception as e:
        db.rollback()
        print(f"❌ Error eliminando usuario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando usuario: {str(e)}"
        )