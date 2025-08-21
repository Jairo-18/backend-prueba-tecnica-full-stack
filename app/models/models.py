"""
models.py
---------
Definición de modelos ORM con SQLAlchemy.

Tablas incluidas:
- StateType: Estados de una marca (ej. pendiente, aprobada, rechazada).
- RoleType: Roles de usuario (ej. admin, cliente).
- RegisterBrand: Marcas registradas por usuarios.
- User: Usuarios del sistema.
- RefreshToken: Manejo de tokens de sesión (JWT refresh).

Cada clase hereda de `Base` (Declarative Base) y representa una tabla
en la base de datos con sus relaciones.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class StateType(Base):
    """
    Modelo: state_type
    ------------------
    Representa los diferentes estados que puede tener una marca
    (ejemplo: pendiente, aprobada, rechazada).

    Campos:
        - id (int): Identificador único.
        - code (str): Código único del estado.
        - name (str): Nombre descriptivo.
    Relaciones:
        - brands → lista de `RegisterBrand` asociados a este estado.
    """
    __tablename__ = "state_type"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

    brands = relationship("RegisterBrand", back_populates="state_type")


class RoleType(Base):
    """
    Modelo: role_type
    -----------------
    Representa los roles de usuario dentro del sistema
    (ejemplo: administrador, cliente).

    Campos:
        - id (int): Identificador único.
        - code (str): Código único del rol.
        - name (str): Nombre descriptivo.
    Relaciones:
        - brands → lista de `User` que tienen este rol.
    """
    __tablename__ = "role_type"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

    brands = relationship("User", back_populates="role_type")


class RegisterBrand(Base):
    """
    Modelo: register_brand
    ----------------------
    Representa una marca registrada en el sistema.

    Campos:
        - id (int): Identificador único.
        - brand_title (str): Nombre o título de la marca.
        - user_id (int): ID del usuario que registró la marca.
        - state_type_id (int): ID del estado de la marca.
    Relaciones:
        - user → `User` que creó la marca.
        - state_type → `StateType` que indica el estado actual.
    """
    __tablename__ = "register_brand"

    id = Column(Integer, primary_key=True, index=True)
    brand_title = Column(String(200), nullable=False)

    # Relaciones con otras tablas
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state_type_id = Column(Integer, ForeignKey("state_type.id"), nullable=False)

    user = relationship("User", back_populates="brands")
    state_type = relationship("StateType", back_populates="brands")


class User(Base):
    """
    Modelo: users
    -------------
    Representa un usuario del sistema.

    Campos:
        - id (int): Identificador único.
        - email (str): Email del usuario (único).
        - username (str): Nombre de usuario (único).
        - fullName (str): Nombre completo.
        - password (str): Contraseña (hasheada).
        - role_type_id (int): Rol del usuario.
    Relaciones:
        - role_type → `RoleType` al que pertenece.
        - tokens → Lista de `RefreshToken` asociados.
        - brands → Lista de marcas (`RegisterBrand`) registradas por este usuario.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    fullName = Column(String(200), nullable=True)
    password = Column(String(255), nullable=False)

    # Relación con RoleType
    role_type_id = Column(Integer, ForeignKey("role_type.id"), nullable=False)
    role_type = relationship("RoleType", back_populates="brands")

    # Relación con RefreshToken y RegisterBrand
    tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    brands = relationship("RegisterBrand", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """
    Modelo: refresh_tokens
    ----------------------
    Representa los tokens de sesión de un usuario para autenticación.

    Campos:
        - id (int): Identificador único.
        - user_id (int): Usuario al que pertenece el token.
        - refresh_token (str): Token de refresco (larga duración).
        - access_token (str): Token de acceso (corta duración).
    Relaciones:
        - user → Usuario (`User`) dueño del token.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    refresh_token = Column(Text, nullable=False)
    access_token = Column(Text, nullable=False)

    user = relationship("User", back_populates="tokens")
