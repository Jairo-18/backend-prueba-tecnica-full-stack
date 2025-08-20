 # app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-por-defecto-cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Validaciones importantes
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL no está configurada en las variables de entorno")

if not SECRET_KEY or SECRET_KEY == "tu-clave-secreta-por-defecto-cambiar-en-produccion":
 
    SECRET_KEY = "clave-insegura-por-defecto-solo-para-desarrollo"  # Solo para desarrollo