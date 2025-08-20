import sys
import os

# Añadir el directorio actual al path de Python para que encuentre la carpeta 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI

# Ahora las importaciones funcionarán
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.brand.routes import router as brand_router

app = FastAPI(
    title="Prueba Técnica Backend",
    description="FastAPI + JWT + Swagger",
    version="1.0.0",
)

# Rutas principales
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(users_router, prefix="/users", tags=["Usuarios"])
app.include_router(brand_router, prefix="/brand", tags=["Registro de Marcas"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "API OK"}

# Handler para Vercel
handler = app