from pydantic import BaseModel
from typing import Optional

class BrandBase(BaseModel):
    brand_title: str
    state_type_id: int
    user_id: Optional[int] = None

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    brand_title: Optional[str] = None
    state_type_id: Optional[int] = None

class BrandResponse(BrandBase):
    id: int
    
    class Config:
        from_attributes = True   

class StateTypeResponse(BaseModel):
    id: int
    name: str
    code: str
    
    class Config:
        from_attributes = True   
        
class RoleTypeResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True