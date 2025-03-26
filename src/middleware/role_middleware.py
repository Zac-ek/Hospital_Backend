from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.middleware.auth_middleware import auth_middleware

def role_required(required_roles: list[str]):
    """Middleware para verificar si el usuario tiene el rol requerido."""
    def decorator(usuario=Depends(auth_middleware.autenticate_login)):
        if usuario.rol not in required_roles:
            raise HTTPException(status_code=403, detail="Acceso denegado: Rol insuficiente")
        return usuario
    return decorator
