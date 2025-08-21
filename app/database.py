"""
db.py
-----
Configuración de la base de datos para la aplicación.

Este módulo se encarga de:
- Cargar la URL de la base de datos desde variables de entorno.
- Configurar el motor de conexión con SQLAlchemy.
- Crear la sesión para interactuar con la base de datos.
- Definir la clase base para los modelos (ORM).
- Proveer funciones utilitarias para obtener y cerrar conexiones.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# 🔹 Cargar variables de entorno desde el archivo .env
load_dotenv()

# 🔹 URL de conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Si no está configurada, se lanza un error
    raise ValueError("DATABASE_URL no está configurada")

# 🔹 Ajuste de driver:
# Cambiar `postgresql://` a `postgresql+psycopg://` para usar psycopg3 en lugar de psycopg2
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# 🔹 Crear motor de conexión
# echo=True → muestra las consultas en consola (útil en desarrollo).
engine = create_engine(
    DATABASE_URL,
    echo=True,           # Logs de SQL en consola (desactívalo en producción con False)
    pool_size=5,         # Número de conexiones en el pool
    max_overflow=10,     # Conexiones extra si el pool está lleno
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_recycle=3600,   # Recicla conexiones cada hora
)

# 🔹 Crear sesión para interactuar con la BD
SessionLocal = sessionmaker(
    autocommit=False,  # No confirmar cambios automáticamente
    autoflush=False,   # No enviar datos automáticamente antes de ejecutar queries
    bind=engine        # Vincular al motor creado
)

# 🔹 Base declarativa
# Esta clase es usada por los modelos para mapear tablas en la base de datos.
Base = declarative_base()

def get_db():
    """
    Generador de sesiones de base de datos.
    
    Se usa en dependencias de FastAPI para obtener una sesión
    y cerrarla automáticamente al final.
    
    Yields:
        Session: Sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def close_db_connections():
    """
    Cierra todas las conexiones activas en el motor.
    
    Útil cuando la aplicación se detiene o se reinicia,
    especialmente en entornos de despliegue (ej. Vercel, Docker).
    """
    engine.dispose()
