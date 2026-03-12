# app/api/routes.py
from fastapi import APIRouter, Depends, status, BackgroundTasks, Response, Cookie, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database import models
from app.api.schemas import (
    UserLoginRequest, UserRegisterRequest, CareerResponse, 
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.security import verify_refresh_token, create_access_token
from app.api import services

# Importamos TODA la documentación homologada
from app.api.docs import (
    CAREERS_SUMMARY, CAREERS_DESC,
    REGISTER_SUMMARY, REGISTER_DESC, REGISTER_RESPONSES,
    LOGIN_SUMMARY, LOGIN_DESC, LOGIN_RESPONSES,
    FORGOT_PWD_SUMMARY, FORGOT_PWD_DESC, FORGOT_PWD_RESPONSES,
    RESET_PWD_SUMMARY, RESET_PWD_DESC, RESET_PWD_RESPONSES,
    MFA_SETUP_SUMMARY, MFA_SETUP_DESC, MFA_SETUP_RESPONSES,
    MFA_VERIFY_SUMMARY, MFA_VERIFY_DESC, MFA_VERIFY_RESPONSES
)

router = APIRouter(prefix="/auth", tags=["Autenticación y Seguridad"])

@router.get(
    "/careers", 
    response_model=List[CareerResponse],
    summary=CAREERS_SUMMARY,
    description=CAREERS_DESC
)
def get_all_careers(db: Session = Depends(get_db)):
    return db.query(models.Career).all()

@router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED,
    summary=REGISTER_SUMMARY,
    description=REGISTER_DESC,
    responses=REGISTER_RESPONSES
)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    new_user = services.register_new_student(db, user_data)
    return {
        "message": "Usuario registrado exitosamente",
        "user_email": new_user.email
    }

@router.post("/login",
    summary="Iniciar Sesión",
    tags=["Autenticación y Seguridad"],
    responses=LOGIN_RESPONSES
)
def login(login_data: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    auth_result = services.authenticate_user(db, login_data)
    
    if isinstance(auth_result, JSONResponse):
        return auth_result
        
    # Cookie 1: Refresh Token (Vive 7 días)
    response.set_cookie(
        key="refresh_token",
        value=auth_result['refresh_token'],
        httponly=True, secure=True, samesite="none", max_age=7 * 24 * 60 * 60 
    )
    
    # Y le damos el access token al Front en la respuesta (Vive 15 mins)
    return {
        "message": "Autenticación exitosa", 
        "user_name": auth_result['user_name'],
        "access_token": auth_result['access_token']
    }

@router.post("/logout", summary="Cerrar Sesión", tags=["Autenticación y Seguridad"])
def logout(response: Response):
    """Destruye la cookie de sesión del Refresh Token."""
    # Ya solo borramos la cookie del refresh_token, la del access_token ya no existe
    response.delete_cookie(key="refresh_token", secure=True, httponly=True, samesite="none")
    return {"message": "Sesión cerrada exitosamente."}

@router.post(
    "/forgot-password",
    summary=FORGOT_PWD_SUMMARY,
    description=FORGOT_PWD_DESC,
    responses=FORGOT_PWD_RESPONSES
)
def forgot_password(
    request: ForgotPasswordRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return services.process_forgot_password(db, request, background_tasks)

@router.post(
    "/reset-password",
    summary=RESET_PWD_SUMMARY,
    description=RESET_PWD_DESC,
    responses=RESET_PWD_RESPONSES
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return services.process_reset_password(db, request)

@router.post("/refresh", summary="Renovar Token de Acceso", tags=["Autenticación y Seguridad"])
def refresh_access_token(refresh_token: str | None = Cookie(None)):
    """Lee la cookie 'refresh_token' y devuelve un nuevo 'access_token' en JSON."""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No se encontró el Refresh Token.")
        
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh Token inválido o expirado.")
        
    # Generamos nuevo access token (15 mins)
    new_token_data = {"sub": payload.get("sub"), "role": payload.get("role")}
    new_access_token = create_access_token(data=new_token_data)
    
    # y ahora mandamos el token directo en la respuesta para el Frontend
    return {
        "message": "Token renovado exitosamente",
        "access_token": new_access_token
    }

@router.post(
    "/mfa/setup",
    summary=MFA_SETUP_SUMMARY,
    description=MFA_SETUP_DESC,
    responses=MFA_SETUP_RESPONSES
)
def mfa_setup(user_id: str, db: Session = Depends(get_db)):
    return services.setup_mfa(db, user_id)

@router.post(
    "/mfa/verify",
    summary=MFA_VERIFY_SUMMARY,
    description=MFA_VERIFY_DESC,
    responses=MFA_VERIFY_RESPONSES
)
def mfa_verify(user_id: str, code: str, db: Session = Depends(get_db)):
    return services.confirm_mfa(db, user_id, code)