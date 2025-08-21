"""
users/routes.py
---------------
Rutas para gestionar usuarios (CRUD).

Incluye:
- Crear usuario.
- Listar usuarios (con paginación).
- Obtener usuario por ID.
- Actualizar usuario (protegido).
- Eliminar usuario (protegido).

Todas las operaciones críticas (listar, actualizar, eliminar) 
requieren autenticación a través de `get_current_user`.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User
from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.core.security import get_current_user, get_password_hash

router = APIRouter()

# --------------------------------------------------------------------
# 📌 Crear usuario
# --------------------------------------------------------------------
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario en la base de datos.

    - Verifica que el email y username sean únicos.
    - Hashea la contraseña antes de guardarla.
    - Si no se especifica rol, asigna el rol por defecto (ID=1).

    Args:
        user (UserCreate): Datos de entrada para crear usuario.
        db (Session): Sesión de la base de datos (inyectada con Depends).

    Returns:
        UserResponse: Usuario creado.
    """
    # Verificar si ya existe un usuario con el mismo email o username
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        else:
            raise HTTPException(status_code=400, detail="El username ya está registrado")

    try:
        # Rol por defecto (si no se envía en la request)
        default_role_id = getattr(user, 'role_type_id', None) or 1

        # Crear instancia de usuario
        new_user = User(
            email=user.email,
            username=user.username,
            fullName=user.fullName,
            password=get_password_hash(user.password),  # 🔒 Hasheo de la contraseña
            role_type_id=default_role_id
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

# --------------------------------------------------------------------
# 📌 Listar usuarios
# --------------------------------------------------------------------
@router.get("/")
def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    """
    Obtener una lista paginada de usuarios.

    Args:
        skip (int): Número de registros a omitir.
        limit (int): Máximo de registros a devolver.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        dict: Contiene usuarios, total de registros, skip, limit y páginas totales.
    """
    try:
        total = db.query(User).count()
        users = db.query(User).offset(skip).limit(limit).all()

        # Convertir ORM → Schema
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

# --------------------------------------------------------------------
# 📌 Obtener usuario por ID
# --------------------------------------------------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    """
    Obtener un usuario por su ID.

    Args:
        user_id (int): ID del usuario.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        UserResponse: Usuario encontrado o error 404 si no existe.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# --------------------------------------------------------------------
# 📌 Actualizar usuario
# --------------------------------------------------------------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    """
    Actualizar los datos de un usuario existente.

    - Verifica duplicados de email y username si se cambian.
    - Hashea la nueva contraseña si se actualiza.
    - Permite actualizar rol si se envía.

    Args:
        user_id (int): ID del usuario a modificar.
        user_update (UserUpdate): Datos nuevos.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        UserResponse: Usuario actualizado.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        # Validar duplicado de email
        if user_update.email is not None and user_update.email != user.email:
            existing_email = db.query(User).filter(
                User.email == user_update.email,
                User.id != user_id
            ).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="El email ya está en uso")
            user.email = user_update.email

        # Validar duplicado de username
        if user_update.username is not None and user_update.username != user.username:
            existing_username = db.query(User).filter(
                User.username == user_update.username,
                User.id != user_id
            ).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="El username ya está en uso")
            user.username = user_update.username

        # Actualizar otros campos
        if user_update.fullName is not None:
            user.fullName = user_update.fullName

        # Actualizar contraseña solo si se envía
        if user_update.password is not None and user_update.password.strip():
            user.password = get_password_hash(user_update.password)

        # Actualizar rol si se envía
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

# --------------------------------------------------------------------
# 📌 Eliminar usuario
# --------------------------------------------------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔑 Protegido
):
    """
    Eliminar un usuario de la base de datos.

    Args:
        user_id (int): ID del usuario a eliminar.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        dict: Mensaje de confirmación.
    """
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
