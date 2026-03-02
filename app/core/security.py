from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
import pyotp
from app.core.config import settings

# ==========================================
# 1. CONFIGURACIÓN DE HASHING (ARGON2)
# ==========================================
# Le decimos a Passlib que use Argon2, el estándar más seguro actualmente
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña que escribe el usuario con el hash de la BD."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Toma la contraseña limpia y devuelve un hash seguro con salting automático."""
    return pwd_context.hash(password)


# ==========================================
# 2. GENERACIÓN DE TOKENS (JWT)
# ==========================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea el 'gafete' digital (JWT) para el usuario."""
    # Hacemos una copia de los datos (que incluirán el ID de usuario y el rol)
    to_encode = data.copy()
    
    # Calculamos a qué hora va a caducar el token (cierre de sesión automático)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Si no le pasamos tiempo, usa los 120 minutos que pusiste en el .env
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Agregamos la fecha de expiración ('exp' es una palabra reservada en JWT)
    to_encode.update({"exp": expire})
    
    # Generamos el token firmado con tu llave secreta
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

# Genera una base32 aleatoria (la "semilla" del MFA)
def generate_mfa_secret() -> str:
    return pyotp.random_base32()

def get_mfa_uri(email: str, secret: str) -> str:
    # Usamos pyotp.TOTP (con mayúsculas) que es la clase correcta
    return pyotp.TOTP(secret).provisioning_uri(
        name=email, 
        issuer_name="UT_Cancun_RAG"
    )

def verify_mfa_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)