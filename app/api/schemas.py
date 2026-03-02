import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional

class StudentPreferences(BaseModel):
    hobbies: List[str]
    horario_preferido: str

# Esquema para mostrar carreras en el Select del Frontend
class CareerResponse(BaseModel):
    career_id: int
    career_name: str
    class Config:
        from_attributes = True

class UserRegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    email: EmailStr 
    password: str = Field(..., min_length=12)
    matricula: str = Field(..., min_length=8)
    
    # El ID que el usuario elegirá en el front
    career_id: int = Field(..., gt=0) 
    preferences: StudentPreferences

    # @field_validator('email')
    # def validate_utcancun_email(cls, v):
    #     if not v.endswith('@utcancun.edu.mx'):
    #         raise ValueError('El correo debe ser @utcancun.edu.mx')
    #     return v

    @field_validator('password')
    def validate_password_strength(cls, v):
        pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if not re.match(pattern, v):
            raise ValueError('La contraseña debe incluir mayúscula, número y símbolo.')
        return v



class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
    
# Asegúrate de tener esto hasta abajo en schemas.py
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=12)

    @field_validator('new_password')
    def validate_password_strength(cls, v):
        pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if not re.match(pattern, v):
            raise ValueError('Contraseña débil: requiere mayúscula, número y símbolo.')
        return v