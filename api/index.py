# api/index.py
import sys
import os

# Solución más directa para Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.auth.routes import router as auth_router
    from app.users.routes import router as users_router
    from app.brand.routes import router as brand_router
    print("✓ Todas las importaciones exitosas")
except ImportError as e:
    print(f"✗ Error de importación: {e}")
    # Listar archivos para debug
    app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
    if os.path.exists(app_dir):
        print("Archivos en app/:")
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                print(f"  {os.path.join(root, file)}")
    raise

app = FastAPI(
    title="Prueba Técnica Backend",
    description="FastAPI + JWT + Swagger",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(users_router, prefix="/users", tags=["Usuarios"])
app.include_router(brand_router, prefix="/brand", tags=["Registro de Marcas"])

@app.get("/")
def root():
    return {"message": "API OK"}

handler = app