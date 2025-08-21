"""
brand/routes.py
---------------
Rutas para gestionar marcas y catálogos de apoyo.

Incluye:
- CRUD de marcas (`RegisterBrand`).
- Listar tipos de estado (`StateType`).
- Listar tipos de rol (`RoleType`).

Todas las operaciones requieren autenticación con `get_current_user`.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import User, RegisterBrand, StateType, RoleType
from app.database import get_db
from app.core.security import get_current_user
from app.brand.schemas import BrandCreate, BrandUpdate, BrandResponse, StateTypeResponse, RoleTypeResponse

router = APIRouter()

# --------------------------------------------------------------------
# 📌 Crear marca
# --------------------------------------------------------------------
@router.post("/", response_model=BrandResponse)
def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear una nueva marca en el sistema.

    Args:
        brand (BrandCreate): Datos de la marca.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        BrandResponse: Marca creada.
    """
    new_brand = RegisterBrand(
        brand_title=brand.brand_title,
        state_type_id=brand.state_type_id,
        user_id=brand.user_id
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand

# --------------------------------------------------------------------
# 📌 Listar marcas (paginadas)
# --------------------------------------------------------------------
@router.get("/")
def list_brands(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener lista paginada de marcas.

    Args:
        skip (int): Número de registros a omitir.
        limit (int): Número máximo de registros a devolver.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        dict: Lista de marcas con datos de paginación.
    """
    total = db.query(RegisterBrand).count()
    brands = db.query(RegisterBrand).offset(skip).limit(limit).all()
    
    brands_response = []
    for brand in brands:
        brands_response.append({
            "id": brand.id,
            "brand_title": brand.brand_title,
            "state_type_id": brand.state_type_id,
            "user_id": brand.user_id
        })
    
    return {
        "brands": brands_response,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }

# --------------------------------------------------------------------
# 📌 Obtener marca por ID
# --------------------------------------------------------------------
@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener una marca específica por ID.

    Args:
        brand_id (int): ID de la marca.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        BrandResponse: Marca encontrada o error 404 si no existe.
    """
    brand = db.query(RegisterBrand).filter(RegisterBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return brand

# --------------------------------------------------------------------
# 📌 Actualizar marca
# --------------------------------------------------------------------
@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar una marca existente.

    Args:
        brand_id (int): ID de la marca.
        brand_update (BrandUpdate): Datos actualizados.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        BrandResponse: Marca actualizada.
    """
    brand = db.query(RegisterBrand).filter(RegisterBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    if brand_update.brand_title is not None:
        brand.brand_title = brand_update.brand_title
    if brand_update.state_type_id is not None:
        brand.state_type_id = brand_update.state_type_id

    db.commit()
    db.refresh(brand)
    return brand

# --------------------------------------------------------------------
# 📌 Eliminar marca
# --------------------------------------------------------------------
@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar una marca existente.

    Args:
        brand_id (int): ID de la marca.
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        dict: Mensaje de confirmación.
    """
    brand = db.query(RegisterBrand).filter(RegisterBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    db.delete(brand)
    db.commit()
    return {"message": f"Marca con id {brand_id} eliminada"}

# --------------------------------------------------------------------
# 📌 Listar tipos de estado
# --------------------------------------------------------------------
@router.get("/state-types/")
def list_state_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve todos los tipos de estado disponibles para las marcas.

    Args:
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        list: Lista de estados (id, name, code).
    """
    state_types = db.query(StateType).all()
    if not state_types:
        raise HTTPException(status_code=404, detail="No hay estados disponibles")
    
    state_types_response = []
    for state_type in state_types:
        state_types_response.append({
            "id": state_type.id,
            "name": state_type.name,
            "code": state_type.code
        })
    
    return state_types_response

# --------------------------------------------------------------------
# 📌 Listar tipos de rol
# --------------------------------------------------------------------
@router.get("/role-types/")
def list_role_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve todos los tipos de rol disponibles en el sistema.

    Args:
        db (Session): Sesión de la base de datos.
        current_user (User): Usuario autenticado.

    Returns:
        list: Lista de roles (id, name, code).
    """
    role_types = db.query(RoleType).all()
    if not role_types:
        raise HTTPException(status_code=404, detail="No hay tipos de rol disponibles")
    
    role_types_response = []
    for role_type in role_types:
        role_types_response.append({
            "id": role_type.id,
            "name": role_type.name,
            "code": role_type.code 
        })
    
    return role_types_response
