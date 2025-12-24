"""
Módulo de autenticación
Maneja login, registro y cambio de contraseña
"""

import streamlit as st
import time

def verificar_sesion():
    """
    Verifica si existe una sesión activa
    
    Returns:
        bool: True si hay sesión activa, False en caso contrario
    """
    if 'usuario' not in st.session_state:
        st.session_state['usuario'] = None
    
    return st.session_state['usuario'] is not None

def mostrar_acceso(supabase):
    """
    Renderiza la pantalla de acceso con login, registro y cambio de contraseña
    
    Args:
        supabase: Cliente de Supabase
    """
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Cambiar Contraseña"])
    
    with tab1:
        renderizar_login(supabase)
    
    with tab2:
        renderizar_registro(supabase)
    
    with tab3:
        renderizar_cambio_password(supabase)

def renderizar_login(supabase):
    """
    Renderiza el formulario de inicio de sesión
    
    Args:
        supabase: Cliente de Supabase
    """
    with st.form("login_form"):
        email = st.text_input(
            "Correo Electrónico",
            key="login_email",
            placeholder="Ingresa tu correo"
        )
        password = st.text_input(
            "Contraseña",
            type="password",
            key="login_pass",
            placeholder="Ingresa tu contraseña"
        )
        submit = st.form_submit_button("Ingresar al Sistema", type="primary")
        
        if submit:
            autenticar_usuario(supabase, email, password)

def autenticar_usuario(supabase, email, password):
    """
    Autentica un usuario con email y contraseña
    
    Args:
        supabase: Cliente de Supabase
        email (str): Correo electrónico del usuario
        password (str): Contraseña del usuario
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state['usuario'] = response.user
        st.success("✅ Acceso autorizado")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error("❌ Usuario o contraseña incorrectos")

def renderizar_registro(supabase):
    """
    Renderiza el formulario de registro de nuevos usuarios
    
    Args:
        supabase: Cliente de Supabase
    """
    st.info("Solo para personal autorizado.")
    
    with st.form("signup_form"):
        new_email = st.text_input(
            "Nuevo Correo",
            key="new_email",
            placeholder="Ingresa tu correo"
        )
        new_pass = st.text_input(
            "Contraseña Temporal",
            type="password",
            key="new_pass",
            placeholder="Mínimo 6 caracteres"
        )
        submit_new = st.form_submit_button("Crear Usuario")
        
        if submit_new:
            crear_usuario(supabase, new_email, new_pass)

def crear_usuario(supabase, email, password):
    """
    Crea un nuevo usuario en el sistema
    
    Args:
        supabase: Cliente de Supabase
        email (str): Correo electrónico del nuevo usuario
        password (str): Contraseña temporal del usuario
    """
    if len(password) >= 6:
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.success("✅ Usuario creado. El usuario debe revisar su correo.")
            st.warning("⚠️ Informar al usuario que debe cambiar su contraseña.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("La contraseña debe tener al menos 6 caracteres.")

def renderizar_cambio_password(supabase):
    """
    Renderiza el formulario de cambio de contraseña con verificación OTP
    
    Args:
        supabase: Cliente de Supabase
    """
    st.write("### 🔐 Cambiar mi Contraseña")
    st.info("Este proceso es 100% privado. Nadie más conocerá tu nueva contraseña.")
    
    # Paso 1: Solicitar código OTP
    st.write("**Paso 1:** Solicita un código de verificación")
    email_change = st.text_input(
        "Tu correo",
        key="email_change",
        placeholder="ejemplo@correo.com"
    )
    
    if st.button("📧 Enviar Código de Verificación", type="primary", use_container_width=True):
        solicitar_codigo_otp(supabase, email_change)
    
    st.divider()
    
    # Paso 2: Verificar y cambiar contraseña
    st.write("**Paso 2:** Verifica tu identidad e ingresa tu nueva contraseña")
    
    col1, col2 = st.columns(2)
    
    with col1:
        otp_code = st.text_input(
            "Código de 8 dígitos",
            placeholder="12345678",
            key="otp_change",
            max_chars=8
        )
    
    with col2:
        new_password = st.text_input(
            "Nueva Contraseña",
            type="password",
            key="new_pass_change",
            placeholder="Mínimo 6 caracteres"
        )
    
    confirm_password = st.text_input(
        "Confirmar Nueva Contraseña",
        type="password",
        key="confirm_pass_change",
        placeholder="Repite tu contraseña"
    )
    
    if st.button("✅ Verificar y Cambiar Contraseña", use_container_width=True):
        cambiar_password(supabase, email_change, otp_code, new_password, confirm_password)

def solicitar_codigo_otp(supabase, email):
    """
    Solicita un código OTP para el email proporcionado
    
    Args:
        supabase: Cliente de Supabase
        email (str): Correo electrónico del usuario
    """
    if email:
        try:
            supabase.auth.sign_in_with_otp({"email": email})
            st.success("✅ Código enviado. Revisa tu correo.")
            st.info("Usa el código de 8 dígitos para verificar tu identidad.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Ingresa tu correo.")

def cambiar_password(supabase, email, otp_code, new_password, confirm_password):
    """
    Cambia la contraseña del usuario después de verificar el código OTP
    
    Args:
        supabase: Cliente de Supabase
        email (str): Correo del usuario
        otp_code (str): Código OTP de verificación
        new_password (str): Nueva contraseña
        confirm_password (str): Confirmación de nueva contraseña
    """
    if not all([email, otp_code, new_password, confirm_password]):
        st.warning("⚠️ Completa todos los campos.")
        return
    
    if new_password != confirm_password:
        st.error("❌ Las contraseñas no coinciden.")
        return
    
    if len(new_password) < 6:
        st.warning("⚠️ La contraseña debe tener al menos 6 caracteres.")
        return
    
    try:
        # Verificar código OTP
        response = supabase.auth.verify_otp({
            "email": email,
            "token": otp_code,
            "type": "email"
        })
        
        if response.user:
            # Actualizar contraseña
            update_response = supabase.auth.update_user({"password": new_password})
            
            if update_response.user:
                st.success("🎉 ¡Contraseña actualizada exitosamente!")
                st.info("Ahora puedes iniciar sesión con tu nueva contraseña.")
                
                # Cerrar sesión temporal
                supabase.auth.sign_out()
                time.sleep(3)
                st.rerun()
            else:
                st.error("Error al actualizar la contraseña.")
    except Exception as e:
        st.error(f"❌ Código incorrecto o expirado. Solicita uno nuevo.")

def cerrar_sesion(supabase):
    """
    Cierra la sesión del usuario actual
    
    Args:
        supabase: Cliente de Supabase
    """
    supabase.auth.sign_out()
    st.session_state['usuario'] = None
    st.success("Sesión cerrada")
    time.sleep(1)
    st.rerun()