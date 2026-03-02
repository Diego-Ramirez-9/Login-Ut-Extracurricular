from sqlalchemy import Boolean, Column, Integer, String, Text, SmallInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database.database import Base

# ==========================================
# 1. TABLA: ROLES (Catálogo)
# ==========================================
class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", back_populates="role")

# ==========================================
# 2. TABLA: CAREERS (Catálogo de Carreras)
# ==========================================
class Career(Base):
    __tablename__ = "careers"
    career_id = Column(Integer, primary_key=True, index=True)
    career_name = Column(Text, unique=True, nullable=False)
    
    # Relación: Una carrera tiene muchos perfiles de estudiantes
    profiles = relationship("StudentProfile", back_populates="career_rel")

# ==========================================
# 3. TABLA: USERS (Credenciales)
# ==========================================
class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    
    failed_attempts = Column(SmallInteger, default=0)
    lockout_until = Column(DateTime(timezone=True), nullable=True)
    
    reset_token = Column(String(100), unique=True, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    mfa_secret = Column(String(32), nullable=True)
    is_mfa_enabled = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="users")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)

# ==========================================
# 4. TABLA: STUDENT_PROFILES (Relacionada a Carreras)
# ==========================================
class StudentProfile(Base):
    __tablename__ = "student_profiles"
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True, nullable=False)
    
    matricula = Column(String(20), unique=True, nullable=False)
    
    # RELACIÓN CLAVE: FK a la tabla de carreras
    career_id = Column(Integer, ForeignKey("careers.career_id"), nullable=False)
    
    preferences = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="student_profile")
    career_rel = relationship("Career", back_populates="profiles")