from typing import cast, Optional
import secrets
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database.models import User, StudentProfile, Role, Career
from app.api.schemas import UserLoginRequest, UserRegisterRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import create_refresh_token, get_password_hash, verify_password, create_access_token, generate_mfa_secret, get_mfa_uri, verify_mfa_code
from app.core.email import send_reset_password_email
from datetime import datetime, timedelta, timezone

def register_new_student(db: Session, user_data: UserRegisterRequest):
    # 1. Validar si el usuario o matrícula ya existen
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado.")
    
    if db.query(StudentProfile).filter(StudentProfile.matricula == user_data.matricula).first():
        raise HTTPException(status_code=400, detail="Matrícula ya registrada.")

    # 2. VALIDACIÓN DE CARRERA: Verificar que el ID exista
    career_exists = db.query(Career).filter(Career.career_id == user_data.career_id).first()
    if not career_exists:
        raise HTTPException(status_code=400, detail="La carrera seleccionada no es válida.")

    # 3. Obtener o crear rol 'student'
    student_role = db.query(Role).filter(Role.role_name == "student").first()
    if not student_role:
        student_role = Role(role_name="student")
        db.add(student_role)
        db.commit()
        db.refresh(student_role)

    # 4. Crear Usuario
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role_id=student_role.role_id
    )
    db.add(new_user)
    db.flush() 

    # 5. Crear Perfil vinculado a la carrera por ID
    new_profile = StudentProfile(
        user_id=new_user.user_id,
        matricula=user_data.matricula,
        career_id=user_data.career_id, # Usamos el ID de la tabla careers
        preferences=user_data.preferences.model_dump()
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(db: Session, login_data: UserLoginRequest):
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # 1. Verificación de bloqueos (Fuerza Bruta)
    lockout = cast(Optional[datetime], user.lockout_until)
    if lockout and lockout > datetime.now(timezone.utc):
        tiempo_restante = (lockout - datetime.now(timezone.utc)).seconds // 60
        raise HTTPException(status_code=403, detail=f"Cuenta bloqueada. Intenta en {tiempo_restante} minutos.")

    # 2. Verificar contraseña
    if not verify_password(login_data.password, cast(str, user.password_hash)):
        current_attempts = cast(int, user.failed_attempts) + 1
        user.failed_attempts = current_attempts # type: ignore
        if current_attempts >= 5:
            user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=15) # type: ignore
            db.commit()
            raise HTTPException(status_code=403, detail="Demasiados intentos. Bloqueado por 15 minutos.")
        db.commit()
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # ==========================================
    # 3. ¡NUEVO! VERIFICACIÓN DE MFA
    # ==========================================
    if cast(bool, user.is_mfa_enabled):
        # Si tiene MFA pero no mandó el código en la petición
        if not login_data.mfa_code:
            # Le mandamos un estado 202 al Frontend con una bandera "mfa_required"
            return JSONResponse(
                status_code=202,
                content={"mfa_required": True, "message": "Credenciales correctas. Ingrese su código MFA."}
            )
        
        # Si mandó el código, verificamos que sea válido
        if not verify_mfa_code(cast(str, user.mfa_secret), login_data.mfa_code):
            raise HTTPException(status_code=401, detail="Código MFA inválido o expirado.")
    # ==========================================

    # 4. Login exitoso: Limpiamos bloqueos
    user.failed_attempts = 0 # type: ignore
    user.lockout_until = None # type: ignore
    db.commit()

    token_data = {"sub": str(user.user_id), "role": user.role.role_name}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token, 
        "token_type": "bearer",
        "user_name": f"{user.first_name} {user.last_name}"
    }

def process_forgot_password(db: Session, request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    user = db.query(User).filter(User.email == request.email).first()
    
    generic_message = "Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña."
    
    if not user:
        return {"message": generic_message}

    # 1. Generar token
    token = secrets.token_urlsafe(32)
    user.reset_token = token # type: ignore
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=15) # type: ignore
    db.commit()

    # 2. ENVIAR CORREO REAL EN SEGUNDO PLANO
    # Le decimos a FastAPI: "Responde al usuario ya, y ponte a mandar el correo por detrás"
    background_tasks.add_task(send_reset_password_email, to_email=cast(str, user.email), token=token)

    return {"message": generic_message}

def setup_mfa(db: Session, user_id: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    secret = generate_mfa_secret()
    # Le decimos a Pylance que ignore la asignación a la columna
    user.mfa_secret = secret  # type: ignore
    db.commit()
    
    # Usamos cast para asegurar que el email se lea como string
    return {
        "mfa_uri": get_mfa_uri(cast(str, user.email), secret),
        "secret_helper": secret
    }

def confirm_mfa(db: Session, user_id: str, code: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or user.mfa_secret is None:
        raise HTTPException(status_code=400, detail="MFA no configurado")
    
    # Validamos el código usando el secreto guardado
    if verify_mfa_code(cast(str, user.mfa_secret), code):
        user.is_mfa_enabled = True  # type: ignore
        db.commit()
        return {"message": "MFA activado exitosamente"}
    
    raise HTTPException(status_code=400, detail="Código inválido")

def process_reset_password(db: Session, request: ResetPasswordRequest):
    # 1. Buscar al usuario usando el token exacto que llegó por correo
    user = db.query(User).filter(User.reset_token == request.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido o no existe.")

    # 2. Verificar que el token no haya expirado (límite de 15 min)
    expires = cast(Optional[datetime], user.reset_token_expires)
    if not expires or expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="El token ha expirado. Solicita uno nuevo.")

    # 3. Hashear la NUEVA contraseña y guardarla
    user.password_hash = get_password_hash(request.new_password) # type: ignore
    
    # 4. SEGURIDAD: Destruir el token para que no se pueda volver a usar (Single-use)
    user.reset_token = None # type: ignore
    user.reset_token_expires = None # type: ignore
    
    # 5. BONUS: Desbloqueamos la cuenta por si el usuario estaba bloqueado por intentos fallidos
    user.failed_attempts = 0 # type: ignore
    user.lockout_until = None # type: ignore
    
    db.commit()
    return {"message": "Contraseña actualizada exitosamente. Ya puedes iniciar sesión."}