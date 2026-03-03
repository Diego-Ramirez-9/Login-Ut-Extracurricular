from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database import models
from app.api.schemas import (
    UserLoginRequest, UserRegisterRequest, CareerResponse, 
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.api import services

# Importamos la documentación que creamos en docs.py
from app.api.docs import (
    CAREERS_SUMMARY, CAREERS_DESC,
    REGISTER_SUMMARY, REGISTER_DESC,
    LOGIN_SUMMARY, LOGIN_DESC,
    FORGOT_PWD_SUMMARY, FORGOT_PWD_DESC,
    RESET_PWD_SUMMARY, RESET_PWD_DESC,
    MFA_SETUP_SUMMARY, MFA_SETUP_DESC,
    MFA_VERIFY_SUMMARY, MFA_VERIFY_DESC,
    COMMON_RESPONSES, LOGIN_RESPONSES
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
    responses=COMMON_RESPONSES
)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    return services.register_new_student(db, user_data)

@router.post(
    "/login",
    summary=LOGIN_SUMMARY,
    description=LOGIN_DESC,
    responses=LOGIN_RESPONSES
)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    return services.authenticate_user(db, login_data)

@router.post(
    "/forgot-password",
    summary=FORGOT_PWD_SUMMARY,
    description=FORGOT_PWD_DESC,
    responses=COMMON_RESPONSES
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
    responses=COMMON_RESPONSES
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return services.process_reset_password(db, request)

@router.post(
    "/mfa/setup",
    summary=MFA_SETUP_SUMMARY,
    description=MFA_SETUP_DESC,
    responses=COMMON_RESPONSES
)
def mfa_setup(user_id: str, db: Session = Depends(get_db)):
    return services.setup_mfa(db, user_id)

@router.post(
    "/mfa/verify",
    summary=MFA_VERIFY_SUMMARY,
    description=MFA_VERIFY_DESC,
    responses=COMMON_RESPONSES
)
def mfa_verify(user_id: str, code: str, db: Session = Depends(get_db)):
    return services.confirm_mfa(db, user_id, code)