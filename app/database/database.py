from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Creamos el "motor" que se conecta a tu PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# 2. Creamos una "fábrica de sesiones" (Cada vez que alguien hace login, abre una sesión)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. La clase "Base" de la que heredarán todos nuestros modelos (tablas)
Base = declarative_base()

# 4. Función de dependencia para que FastAPI maneje la base de datos de forma segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()