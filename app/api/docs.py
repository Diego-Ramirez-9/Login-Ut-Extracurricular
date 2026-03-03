from typing import Dict, Any, Union
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
* Requiere una contraseña robusta (Mayúscula, número, carácter especial, min 12 caracteres (@$!%*?&)).
* El `career_id` debe existir en el catálogo de carreras.
"""

LOGIN_SUMMARY = "Iniciar Sesión (Obtener JWT)"
LOGIN_DESC = """
Autentica al usuario y devuelve el Token JWT de acceso.

**Flujo de Autenticación (MFA):**
1. Si el usuario tiene MFA activo , devuelve el token directo.
2. Si **no tiene MFA**, devolverá un error `401` pidiendo el código.
3. El frontend debe volver a llamar a esta ruta incluyendo el `mfa_code`.

**Seguridad:** Bloquea la cuenta por 15 minutos tras 5 intentos fallidos.
"""

FORGOT_PWD_SUMMARY = "Solicitar Recuperación de Contraseña"
FORGOT_PWD_DESC = """
Genera un token de un solo uso y simula el envío de un correo vía Brevo.
**Nota:** Por seguridad (anti-enumeración), siempre devuelve éxito incluso si el correo no existe.
"""

RESET_PWD_SUMMARY = "Restablecer Contraseña"
RESET_PWD_DESC = """
Recibe el token enviado al correo del usuario y establece una nueva contraseña.
* El token caduca en 15 minutos.
* El token es de un solo uso (se destruye al usarse).
* Desbloquea automáticamente la cuenta si estaba bloqueada por fuerza bruta.
"""

MFA_SETUP_SUMMARY = "Paso 1: Configurar MFA (Generar QR)"
MFA_SETUP_DESC = """
Inicia la configuración del Autenticador de Google.
Devuelve una `mfa_uri` que el Frontend debe convertir en un Código QR para que el usuario lo escanee.
"""

MFA_VERIFY_SUMMARY = "Paso 2: Activar MFA (Verificar Código)"
MFA_VERIFY_DESC = """
Recibe el código de 6 dígitos de la app del celular para confirmar que el usuario configuró todo correctamente. Al ser exitoso, el MFA queda activo permanentemente.
"""

# ==========================================
# DICCIONARIOS DE RESPUESTAS DE ERROR
# ==========================================

# Errores comunes para casi todas las rutas
COMMON_RESPONSES: Dict[Union[int, str], Dict[str, Any]] = {
    400: {"description": "Petición incorrecta o regla de negocio no cumplida."},
    404: {"description": "Recurso o usuario no encontrado."},
    500: {"description": "Error interno del servidor."}
}

LOGIN_RESPONSES: Dict[Union[int, str], Dict[str, Any]] = {
    401: {"description": "Credenciales incorrectas, código MFA inválido o código MFA faltante."},
    403: {"description": "Cuenta bloqueada temporalmente por demasiados intentos (Fuerza Bruta)."}
}

LOGIN_RESPONSES.update(COMMON_RESPONSES)