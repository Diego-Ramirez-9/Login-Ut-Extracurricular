import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_reset_password_email(to_email: str, token: str):
    """Envía el correo real usando el servidor SMTP de Brevo."""
    
    # Esta es la URL de prueba de React (cambiará cuando lo suban a la web)
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    
    msg = EmailMessage()
    msg['Subject'] = "Recuperación de Contraseña - UT Cancún RAG"
    
    # Brevo requiere que el remitente coincida o esté verificado. 
    # Usaremos tu identificador como remitente por ahora.
    # Usa exactamente el correo que verificaste en el Paso 1 en Brevo
    msg['From'] = "support@utextracurricular.com"
    msg['To'] = to_email
    
    cuerpo_correo = f"""
    Hola,
    
    Hemos recibido una solicitud para restablecer tu contraseña en el sistema RAG de la UT Cancún.
    
    Por favor, haz clic en el siguiente enlace para crear una nueva contraseña:
    {reset_link}
    
    Este enlace expirará en 15 minutos por tu seguridad.
    
    Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
    """
    msg.set_content(cuerpo_correo)

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Correo enviado exitosamente a {to_email}")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")