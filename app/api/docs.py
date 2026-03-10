# app/api/docs.py
from typing import Dict, Any, Union

# ==========================================
# TIPO PARA CALMAR A PYLANCE
# ==========================================
ResponseType = Dict[Union[int, str], Dict[str, Any]]

# ==========================================
# TEXTOS PARA SWAGGER (Descripciones y Resúmenes)
# ==========================================

CAREERS_SUMMARY = "Catálogo de Carreras"
CAREERS_DESC = """
Obtiene la lista oficial de todas las carreras de la UT Cancún.
**Uso en Frontend:** Utiliza el `career_id` devuelto aquí para poblar el select en el formulario de registro.
"""

REGISTER_SUMMARY = "Registrar Nuevo Estudiante"
REGISTER_DESC = """
Crea una cuenta para un estudiante nuevo.
* Valida que el correo sea dominio `@utcancun.edu.mx`.
* Requiere una contraseña robusta.
* El `career_id` debe existir en el catálogo.
"""

LOGIN_SUMMARY = "Iniciar Sesión (Obtener JWT)"
LOGIN_DESC = """
Autentica al usuario y guarda el Token en una Cookie Segura.

**Flujo de Autenticación:**
1. Si el usuario **tiene MFA activo**, devuelve un código 202 pidiendo el MFA.
2. Si **no tiene MFA** o envía el código correcto, devuelve 200 e inyecta la Cookie HttpOnly.
"""

FORGOT_PWD_SUMMARY = "Solicitar Recuperación de Contraseña"
FORGOT_PWD_DESC = """
Genera un token de un solo uso y simula el envío de un correo vía Brevo.
"""

RESET_PWD_SUMMARY = "Restablecer Contraseña"
RESET_PWD_DESC = """
Recibe el token enviado al correo del usuario y establece una nueva contraseña.
"""

MFA_SETUP_SUMMARY = "Paso 1: Configurar MFA (Generar QR)"
MFA_SETUP_DESC = """
Inicia la configuración del Autenticador de Google.
Devuelve una `mfa_uri` que el Frontend debe convertir en un Código QR.
"""

MFA_VERIFY_SUMMARY = "Paso 2: Activar MFA (Verificar Código)"
MFA_VERIFY_DESC = """
Recibe el código de 6 dígitos de la app del celular para confirmar que el usuario configuró todo correctamente.
"""

# ==========================================
# DICCIONARIOS DE RESPUESTAS (ERRORES + ÉXITO)
# ==========================================

# Errores comunes que comparten todas las rutas
COMMON_RESPONSES: ResponseType = {
    400: {"description": "Petición incorrecta o regla de negocio no cumplida."},
    404: {"description": "Recurso o usuario no encontrado."},
    500: {"description": "Error interno del servidor."}
}

# 1. Respuestas de Registro
REGISTER_RESPONSES: ResponseType = {
    201: {
        "description": "Usuario creado exitosamente.",
        "content": {"application/json": {"example": {"message": "Usuario registrado exitosamente", "user_email": "alumno@utcancun.edu.mx"}}}
    }
}
REGISTER_RESPONSES.update(COMMON_RESPONSES)

# 2. Respuestas de Login
LOGIN_RESPONSES: ResponseType = {
    200: {
        "description": "Login exitoso. El token JWT se envía seguro en una Cookie HttpOnly.",
        "content": {"application/json": {"example": {"message": "Autenticación exitosa", "user_name": "Diego Ramirez"}}}
    },
    202: {
        "description": "Credenciales correctas, pero se requiere código MFA.",
        "content": {"application/json": {"example": {"mfa_required": True, "message": "Credenciales correctas. Ingrese su código MFA."}}}
    },
    401: {"description": "Credenciales incorrectas o código MFA inválido."},
    403: {"description": "Cuenta bloqueada temporalmente por demasiados intentos."}
}
LOGIN_RESPONSES.update(COMMON_RESPONSES)

# 3. Respuestas de Olvidé mi Contraseña
FORGOT_PWD_RESPONSES: ResponseType = {
    200: {
        "description": "Solicitud procesada (con protección anti-enumeración).",
        "content": {"application/json": {"example": {"message": "Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña."}}}
    }
}
FORGOT_PWD_RESPONSES.update(COMMON_RESPONSES)

# 4. Respuestas de Restablecer Contraseña
RESET_PWD_RESPONSES: ResponseType = {
    200: {
        "description": "Contraseña actualizada.",
        "content": {"application/json": {"example": {"message": "Contraseña actualizada exitosamente. Ya puedes iniciar sesión."}}}
    }
}
RESET_PWD_RESPONSES.update(COMMON_RESPONSES)

# 5. Respuestas de Configurar MFA
MFA_SETUP_RESPONSES: ResponseType = {
    200: {
        "description": "Secreto generado correctamente.",
        "content": {"application/json": {"example": {
            "mfa_uri": "otpauth://totp/UT%20Extracurricular:alumno@utcancun...?",
            "secret_helper": "JBSWY3DPEHPK3PXP"
        }}}
    }
}
MFA_SETUP_RESPONSES.update(COMMON_RESPONSES)

# 6. Respuestas de Verificar MFA
MFA_VERIFY_RESPONSES: ResponseType = {
    200: {
        "description": "MFA validado y activado.",
        "content": {"application/json": {"example": {"message": "MFA activado exitosamente"}}}
    }
}
MFA_VERIFY_RESPONSES.update(COMMON_RESPONSES)