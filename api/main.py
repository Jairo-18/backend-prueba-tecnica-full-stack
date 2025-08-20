from fastapi import FastAPI

# Importar routers desde la carpeta app
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
