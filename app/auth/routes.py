from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets

from app.core.security import get_current_user
from app.database import get_db
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.models import User, RefreshToken
from app.auth.schemas import LoginRequest, TokenResponse

router = APIRouter()

# ==========================================================
# 🔑 Autenticación: Login y gestión de tokens
# ==========================================================

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(login: LoginRequest, db: Session = Depends(get_db)):
    """
    ### Inicia sesión y genera tokens de autenticación.
    
    - **Body (LoginRequest)**: `email`, `password`
    - Verifica las credenciales contra la base de datos.
    - Si son correctas:
        - Genera un `access_token` con vencimiento definido en la configuración.
        - Genera un `refresh_token` único y lo guarda en la DB.
        - Devuelve la información del usuario, su rol y los tokens.

    - **Errores**:
        - 401: Si las credenciales son inválidas.
    
    #### Respuesta:
    ```json
    {
        "access_token": "jwt...",
        "refresh_token": "token...",
        "token_type": "bearer",
        "role": { "code": "ADMIN", "name": "Administrador" },
        "user": {
            "id": 1,
            "email": "test@test.com",
            "username": "jdoe",
            "fullName": "John Doe"
        }
    }
    ```
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == login.email).first()
    
    # Validar credenciales
    if not user or not verify_password(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear access token (JWT)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  # `sub` = identificador estándar en JWT
        expires_delta=access_token_expires
    )

    # Crear refresh token aleatorio y guardarlo en la DB
    refresh_token_str = secrets.token_urlsafe(32)
    refresh_token = RefreshToken(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token_str
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    # Obtener el rol relacionado del usuario
    role = None
    if user.role_type:
        role = {
            "code": user.role_type.code,
            "name": user.role_type.name
        }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "role": role,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "fullName": user.fullName
        }
    }


# ==========================================================
# 🚪 Logout: Revocar tokens
# ==========================================================

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    ### Cierra la sesión del usuario actual.
    
    - Elimina **todos** los refresh tokens asociados al usuario en la base de datos.
    - Con esto, el usuario debe volver a autenticarse para generar un nuevo token.

    #### Respuesta:
    ```json
    { "message": "Sesión cerrada correctamente" }
    ```
    """
    # Buscar todos los refresh tokens activos del usuario
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id
    ).all()

    # Eliminar tokens de la DB (revocar sesión)
    for token in tokens:
        db.delete(token)

    db.commit()
    return {"message": "Sesión cerrada correctamente"}
