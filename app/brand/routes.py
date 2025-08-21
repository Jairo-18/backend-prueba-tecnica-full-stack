from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.models import User, RegisterBrand, StateType
from app.database import get_db
from app.core.security import get_current_user
from app.brand.schemas import BrandCreate, BrandUpdate, BrandResponse, StateTypeResponse

router = APIRouter()

# Crear marca
@router.post("/", response_model=BrandResponse)
def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_brand = RegisterBrand(
        brand_title=brand.brand_title,
        state_type_id=brand.state_type_id,
        user_id=brand.user_id  # si quieres pasar por body
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand

# Obtener lista paginada de marcas con respuesta estructurada
@router.get("/")
def list_brands(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener lista paginada de marcas con información de paginación
    """
    # Obtener el total de registros
    total = db.query(RegisterBrand).count()
    
    # Obtener los registros paginados
    brands = db.query(RegisterBrand).offset(skip).limit(limit).all()
    
    # Convertir a formato de respuesta
    brands_response = [BrandResponse.from_orm(brand) for brand in brands]
    
    return {
        "brands": brands_response,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }

# Obtener una marca por ID
@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    brand = db.query(RegisterBrand).filter(RegisterBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return brand

# Editar marca
@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

# Eliminar marca
@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    brand = db.query(RegisterBrand).filter(RegisterBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    db.delete(brand)
    db.commit()
    return {"message": f"Marca con id {brand_id} eliminada"}

# Obtener tipos de estado (sin paginación ya que son pocos)
@router.get("/state-types/", response_model=List[StateTypeResponse])
def list_state_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    state_types = db.query(StateType).all()
    if not state_types:
        raise HTTPException(status_code=404, detail="No hay estados disponibles")
    return state_types