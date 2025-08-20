from pydantic import BaseModel

class BrandBase(BaseModel):
    brand_title: str
    state_type_id: int

class BrandCreate(BrandBase):
    user_id: int 

class BrandUpdate(BaseModel):
    brand_title: str | None = None
    state_type_id: int | None = None

class BrandResponse(BaseModel):
    id: int
    brand_title: str
    user_id: int
    state_type_id: int

    class Config:
        orm_mode = True
