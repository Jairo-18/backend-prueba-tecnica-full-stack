# app/core/config.py
import os
from dotenv import load_dotenv

# ==========================================================
# ⚙️ Carga de variables de entorno
# ==========================================================

# Carga las variables definidas en un archivo .env (solo en desarrollo local).
# En producción (ej: Vercel), las variables vienen de la configuración del servidor.
load_dotenv()

# ==========================================================
# 🔑 Configuración de seguridad / JWT
# ==========================================================

# Clave secreta para firmar y verificar JWT.
# ⚠️ En producción debe estar definida en las variables de entorno.
SECRET_KEY = os.getenv("SECRET_KEY", "clave-insegura-por-defecto-solo-para-desarrollo")

# Algoritmo de encriptación usado para JWT (ej: HS256).
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Tiempo de expiración de los access tokens en minutos.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ==========================================================
# 🗄️ Configuración de la base de datos
# ==========================================================

# URL de conexión a la base de datos (PostgreSQL en Neon o local).
DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================================
# 🌐 Detección de entorno
# ==========================================================

# Vercel establece la variable VERCEL=1 en producción.
IS_VERCEL = os.getenv("VERCEL") == "1"

# ==========================================================
# ✅ Validaciones de configuración
# ==========================================================

# Verificar que DATABASE_URL esté configurada
if not DATABASE_URL:
    if IS_VERCEL:
        # Si es producción (Vercel), debe estar configurada en el dashboard de Vercel
        raise ValueError("❌ DATABASE_URL debe estar configurada en las variables de entorno de Vercel")
    else:
        # Si es local, debe estar en el archivo .env
        raise ValueError("❌ DATABASE_URL no está configurada en el archivo .env")

# Verificar que no se use la SECRET_KEY insegura en producción
if IS_VERCEL and SECRET_KEY == "clave-insegura-por-defecto-solo-para-desarrollo":
    raise ValueError("❌ SECRET_KEY debe estar configurada en las variables de entorno de Vercel")

# ==========================================================
# 🖨️ Debug: Mostrar configuración cargada
# ==========================================================
# Esto es útil en desarrollo para verificar que todo se cargó correctamente.
print(f"🔧 Configuración cargada:")
print(f"   - DATABASE: Neon PostgreSQL {'✅' if DATABASE_URL else '❌'}")
print(f"   - SECRET_KEY configurado: {'✅' if SECRET_KEY != 'clave-insegura-por-defecto-solo-para-desarrollo' else '⚠️'}")
print(f"   - Entorno: {'Vercel' if IS_VERCEL else 'Local'}")
