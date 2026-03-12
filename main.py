from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database.database import engine
from app.database import models
# 1. ¡NUEVO! Importamos el router que acabas de crear
from app.api.routes import router as auth_router 

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Microservice - UT Cancún",
    description="Microservicio de Identidad y Acceso para el sistema RAG",
    version="1.0.0"
)

origins = [
    "https://front-ut-extracurricular-production.up.railway.app",
    "http://localhost:3000", # Por si tu compañero prueba en su compu local con React
    "http://localhost:5173",# El frontend de tu compañero en Railway
]

# 3. Añadir las reglas a la aplicación
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Solo deja pasar a los de la lista VIP
    allow_credentials=True,      # Permite el uso de cookies y tokens
    allow_methods=["*"],         # Permite todos los métodos (GET, POST, PUT, DELETE, options)
    allow_headers=["*"],         # Permite todos los encabezados
)

# 2. ¡NUEVO! Conectamos el router a la aplicación principal
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Microservicio de Autenticación conectado a Supabase 🚀"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)