# api/index.py
"""
Módulo principal para la inicialización de la API.

Este archivo se encarga de:
- Configurar la aplicación FastAPI.
- Manejar posibles problemas de importación (útil en despliegues en Vercel).
- Configurar middlewares (CORS).
- Registrar los routers de los diferentes módulos (auth, users, brand).
- Definir la ruta raíz de prueba.
"""

import sys
import os

# 🔹 Ajuste de rutas para que Python encuentre los módulos de la carpeta `app/`.
# Esto es especialmente útil en despliegues (ej. Vercel) donde la estructura de carpetas
# puede causar problemas al importar.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # FastAPI y middlewares
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Rutas de la aplicación
    from app.auth.routes import router as auth_router
    from app.users.routes import router as users_router
    from app.brand.routes import router as brand_router

    print("✓ Todas las importaciones exitosas")
except ImportError as e:
    # En caso de error de importación, mostrar detalles y listar archivos en `app/`
    print(f"✗ Error de importación: {e}")
    app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
    if os.path.exists(app_dir):
        print("Archivos en app/:")
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                print(f"  {os.path.join(root, file)}")
    raise

# 🔹 Inicialización de la aplicación FastAPI
app = FastAPI(
    title="Prueba Técnica Backend",
    description="API construida con FastAPI, JWT y documentación Swagger.",
    version="1.0.0",
)

# 🔹 Configuración de CORS (Cross-Origin Resource Sharing)
# Se permiten todas las solicitudes desde cualquier origen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # No se permiten cookies o credenciales
    allow_methods=["*"],      # Permite todos los métodos HTTP
    allow_headers=["*"],      # Permite todos los headers
)

# 🔹 Registro de routers
# Cada router maneja un módulo diferente de la API.
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(users_router, prefix="/users", tags=["Usuarios"])
app.include_router(brand_router, prefix="/brand", tags=["Registro de Marcas"])

@app.get("/")
def root():
    """
    Ruta raíz de la API.
    
    Returns:
        dict: Mensaje de confirmación de que la API está funcionando.
    """
    return {"message": "API OK"}

# 🔹 `handler` es usado por Vercel u otros entornos serverless como punto de entrada.
handler = app
