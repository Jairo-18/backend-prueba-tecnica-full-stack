from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class StateType(Base):
    __tablename__ = "state_type"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    brands = relationship("RegisterBrand", back_populates="state_type")


class RegisterBrand(Base):
    __tablename__ = "register_brand"

    id = Column(Integer, primary_key=True, index=True)
    brand_title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state_type_id = Column(Integer, ForeignKey("state_type.id"), nullable=False)
    user = relationship("User", back_populates="brands")
    state_type = relationship("StateType", back_populates="brands")


# Modificar User para relacionar marcas
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    fullName = Column(String(200), nullable=True)
    password = Column(String(255), nullable=False)
    tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    brands = relationship("RegisterBrand", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(Text, nullable=False)
    access_token = Column(Text, nullable=False)
    user = relationship("User", back_populates="tokens")