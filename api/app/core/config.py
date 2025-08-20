# app/core/config.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno (solo funciona en desarrollo local)
load_dotenv()

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "clave-insegura-por-defecto-solo-para-desarrollo")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Detectar si estamos en Vercel
IS_VERCEL = os.getenv("VERCEL") == "1"

# Validar configuración
if not DATABASE_URL:
    if IS_VERCEL:
        raise ValueError("❌ DATABASE_URL debe estar configurada en las variables de entorno de Vercel")
    else:
        raise ValueError("❌ DATABASE_URL no está configurada en el archivo .env")

# Verificar SECRET_KEY en producción
if IS_VERCEL and SECRET_KEY == "clave-insegura-por-defecto-solo-para-desarrollo":
    raise ValueError("❌ SECRET_KEY debe estar configurada en las variables de entorno de Vercel")

print(f"🔧 Configuración cargada:")
print(f"   - DATABASE: Neon PostgreSQL {'✅' if DATABASE_URL else '❌'}")
print(f"   - SECRET_KEY configurado: {'✅' if SECRET_KEY != 'clave-insegura-por-defecto-solo-para-desarrollo' else '⚠️'}")
print(f"   - Entorno: {'Vercel' if IS_VERCEL else 'Local'}")