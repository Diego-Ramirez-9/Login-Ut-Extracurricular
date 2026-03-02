from fastapi import APIRouter, Depends, status
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database import models
from app.api.schemas import UserLoginRequest, UserRegisterRequest, CareerResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.api import services

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Endpoint para que el Front cargue las carreras
@router.get("/careers", response_model=List[CareerResponse])
def get_all_careers(db: Session = Depends(get_db)):
    """Obtiene el catálogo de carreras de la UT Cancún."""
    return db.query(models.Career).all()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    return services.register_new_student(db, user_data)

@router.post("/login")
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Verifica credenciales y devuelve un Token JWT.
    Este token debe ser guardado por el Frontend para futuras peticiones.
    """
    return services.authenticate_user(db, login_data)

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest, 
    background_tasks: BackgroundTasks, # Lo inyectamos aquí
    db: Session = Depends(get_db)
):
    """Genera un token de recuperación y envía un correo real por Brevo."""
    return services.process_forgot_password(db, request, background_tasks)

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Verifica el token enviado por correo y actualiza la contraseña del usuario."""
    return services.process_reset_password(db, request)

@router.post("/mfa/setup")
def mfa_setup(user_id: str, db: Session = Depends(get_db)):
    """Inicia el proceso de MFA devolviendo la URI para el código QR."""
    return services.setup_mfa(db, user_id)

@router.post("/mfa/verify")
def mfa_verify(user_id: str, code: str, db: Session = Depends(get_db)):
    """Recibe el código de 6 dígitos para activar el MFA definitivamente."""
    return services.confirm_mfa(db, user_id, code)

