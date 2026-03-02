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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ¡NUEVO! Conectamos el router a la aplicación principal
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Microservicio de Autenticación conectado a Supabase 🚀"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)