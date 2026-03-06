import json
import urllib.request
from app.core.config import settings 

def send_reset_password_email(to_email: str, token: str):
    reset_link = f"https://front-ut-extracurricular-production.up.railway.app/auth/reset-password?token={token}"
    
    data = {
        "sender": {
            "name": "Soporte UT Cancún", 
            # Usamos tu correo institucional verificado que me mostraste
            "email": "support@utextracurricular.com" 
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
    
    url = "https://api.brevo.com/v3/smtp/email"
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"))
    
    req.add_header("accept", "application/json")
    # Usamos la variable con el nombre correcto
    req.add_header("api-key", settings.BREVO_API_KEY) 
    req.add_header("content-type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            # Mensaje súper limpio en la consola, sin el JSON raro
            print(f"✅ ¡Éxito! Correo de recuperación enviado a {to_email}")
    except Exception as e:
        print("❌ Error al enviar correo de recuperación:", e)