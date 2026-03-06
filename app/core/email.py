import json
import urllib.request
from app.core.config import settings 

def send_reset_password_email(to_email: str, token: str):
    # Enlace al frontend (Ajusta el puerto si tu compañero usa otro)
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    
    # 1. Armamos el paquete de datos en formato JSON
    data = {
        "sender": {
            "name": "Sistema RAG UT Cancún", 
            "email": "support@utextracurricular.com" # Tu correo verificado en Brevo
        },
        "to": [{"email": to_email}],
        "subject": "Recuperación de Contraseña",
        "htmlContent": f"""
        <h3>Hola,</h3>
        <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
        <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>Este enlace expirará en 15 minutos.</p>
        """
    }
    
    # 2. Preparamos la petición HTTP hacia la API de Brevo
    url = "https://api.brevo.com/v3/smtp/email"
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"))
    
    # 3. Agregamos las cabeceras (Inyectamos la llave maestra)
    req.add_header("accept", "application/json")
    req.add_header("api-key", settings.SMTP_PASSWORD) 
    req.add_header("content-type", "application/json")
    
    # 4. Disparamos la petición HTTP
    try:
        with urllib.request.urlopen(req) as response:
            print("✅ ¡Éxito! Correo enviado vía API:", response.read().decode())
    except Exception as e:
        print("❌ Error al enviar vía API HTTP:", str(e))