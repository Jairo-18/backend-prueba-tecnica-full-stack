import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

# Detectar si estamos en Vercel (serverless)
IS_VERCEL = os.getenv("VERCEL") == "1"

# Convertir URL para usar asyncpg en Vercel
if IS_VERCEL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if IS_VERCEL:
    # Configuración optimizada para serverless (Vercel)
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # No pool de conexiones en serverless
        pool_pre_ping=True,  # Verificar conexión antes de usar
        echo=False,  # Sin logs en producción
    )
else:
    # Configuración para desarrollo local (mantener psycopg2)
    engine = create_engine(
        DATABASE_URL, 
        echo=True,  # Logs en desarrollo
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para cerrar conexiones (útil en serverless)
def close_db_connections():
    """Cierra todas las conexiones de la base de datos"""
    engine.dispose()