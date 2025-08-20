# api/index.py
import sys
import os
from pathlib import Path

# Obtener la ruta absoluta del directorio actual
current_dir = Path(__file__).parent.absolute()
# Obtener la ruta del directorio padre (raíz del proyecto)
project_root = current_dir.parent

# Agregar el directorio raíz al path de Python
sys.path.insert(0, str(project_root))

print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ahora las importaciones funcionarán
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.brand.routes import router as brand_router

app = FastAPI(
    title="Prueba Técnica Backend",
    description="FastAPI + JWT + Swagger",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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