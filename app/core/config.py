import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Cargamos las variables del archivo .env
load_dotenv()

class Settings(BaseSettings):
    # Agregamos 'or ""' para asegurarle a Pylance que siempre será un string (str)
    DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
    SECRET_KEY: str = os.getenv("SECRET_KEY") or ""
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))
    
    SMTP_SERVER: str = os.getenv("SMTP_SERVER") or ""
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME") or ""
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD") or ""

    class Config:
        env_file = ".env"

settings = Settings()