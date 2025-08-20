from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.models import User, RegisterBrand
from app.database import get_db
from app.core.security import get_current_user
from app.brand.schemas import BrandCreate, BrandUpdate, BrandResponse

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

# Obtener lista paginada de marcas
@router.get("/", response_model=List[BrandResponse])
def list_brands(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(RegisterBrand).offset(skip).limit(limit).all()

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
