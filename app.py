import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Calidad", page_icon="🏗️")

# --- 2. ESTILOS CSS ---
estilo_personalizado = """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        .footer-personalizado {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f0f2f6;
            color: #333;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            border-top: 1px solid #ddd;
        }
    </style>
    
    <div class="footer-personalizado">
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.02.08
    </div>
"""
st.markdown(estilo_personalizado, unsafe_allow_html=True)

# --- 3. CONEXIÓN A SUPABASE ---
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error: No se detectaron los secretos de conexión.")
    st.stop()

# --- 4. GESTIÓN DE SESIÓN ---
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None
if 'modo_recuperacion' not in st.session_state:
    st.session_state['modo_recuperacion'] = False

# --- 4.5 DETECTAR SI VIENE DEL ENLACE DE RECUPERACIÓN ---
query_params = st.query_params
if 'type' in query_params and query_params['type'] == 'recovery':
    st.session_state['modo_recuperacion'] = True
    if 'access_token' in query_params:
        st.session_state['recovery_token'] = query_params['access_token']

# --- 5. PANTALLA DE RECUPERACIÓN DE CONTRASEÑA ---
def mostrar_cambio_password():
    st.title("🔐 Cambiar Contraseña")
    st.write("Crea tu nueva contraseña de acceso")
    
    with st.form("reset_password_form"):
        new_pass = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirm_pass = st.text_input("Confirmar Contraseña", type="password", placeholder="Repite la contraseña")
        submit = st.form_submit_button("✅ Establecer Nueva Contraseña", type="primary")
        
        if submit:
            if new_pass == confirm_pass:
                if len(new_pass) >= 6:
                    try:
                        # Usar el token de recuperación para cambiar la contraseña
                        response = supabase.auth.update_user({"password": new_pass})
                        
                        if response.user:
                            st.success("✅ ¡Contraseña actualizada exitosamente!")
                            st.info("Ahora puedes iniciar sesión con tu nueva contraseña.")
                            time.sleep(2)
                            # Limpiar el modo recuperación
                            st.session_state['modo_recuperacion'] = False
                            if 'recovery_token' in st.session_state:
                                del st.session_state['recovery_token']
                            # Limpiar query params
                            st.query_params.clear()
                            st.rerun()
                        else:
                            st.error("Error al actualizar la contraseña.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("⚠️ La contraseña debe tener al menos 6 caracteres.")
            else:
                st.error("❌ Las contraseñas no coinciden.")
    
    if st.button("← Volver al inicio"):
        st.session_state['modo_recuperacion'] = False
        if 'recovery_token' in st.session_state:
            del st.session_state['recovery_token']
        st.query_params.clear()
        st.rerun()

# --- 6. PANTALLA DE ACCESO ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Recuperar Contraseña"])
    
    # --- PESTAÑA 1: LOGIN ---
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico", key="login_email", placeholder="Ingresa tu correo")
            password = st.text_input("Contraseña", type="password", key="login_pass", placeholder="Ingresa tu contraseña")
            submit = st.form_submit_button("Ingresar al Sistema", type="primary")
            
            if submit:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['usuario'] = response.user
                    st.success("✅ Acceso autorizado")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error("❌ Usuario o contraseña incorrectos")
    
    # --- PESTAÑA 2: CREAR USUARIO ---
    with tab2:
        st.info("Solo para personal autorizado.")
        with st.form("signup_form"):
            new_email = st.text_input("Nuevo Correo", key="new_email", placeholder="Ingresa tu correo")
            new_pass = st.text_input("Nueva Contraseña", type="password", key="new_pass", placeholder="Mínimo 6 caracteres")
            submit_new = st.form_submit_button("Registrar Usuario")
            
            if submit_new:
                if len(new_pass) >= 6:
                    try:
                        supabase.auth.sign_up({"email": new_email, "password": new_pass})
                        st.success("✅ Usuario creado. ¡Revisa tu correo para confirmar la cuenta!")
                    except Exception as e:
                        st.error(f"Error al crear: {e}")
                else:
                    st.warning("La contraseña debe tener al menos 6 caracteres.")
    
    # --- PESTAÑA 3: RECUPERAR CONTRASEÑA ---
    with tab3:
        st.write("**Opción 1: Restablecer contraseña por correo** ✉️")
        st.info("Recibirás un enlace para crear una nueva contraseña de forma segura.")
        
        email_reset = st.text_input("Ingresa tu correo registrado", key="reset_email", placeholder="ejemplo@correo.com")
        
        if st.button("📧 Enviar enlace de restablecimiento", type="primary"):
            if email_reset:
                try:
                    supabase.auth.reset_password_email(email_reset)
                    st.success("✅ ¡Enlace enviado! Revisa tu correo (también en spam).")
                    st.info("📌 Haz clic en el enlace del correo para establecer tu nueva contraseña.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("⚠️ Por favor, ingresa tu correo primero.")
        
        st.divider()
        
        st.write("**Opción 2: Acceso temporal con código** 🔢")
        st.info("Si prefieres, te enviamos un código de 6 dígitos para acceso inmediato.")
        
        email_otp = st.text_input("Correo registrado", key="otp_email", placeholder="ejemplo@correo.com")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Enviar código"):
                if email_otp:
                    try:
                        supabase.auth.sign_in_with_otp({"email": email_otp})
                        st.success("📧 Código enviado. Revisa tu correo.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Ingresa tu correo primero.")
        
        otp_code = st.text_input("Ingresa el código de 6 dígitos", placeholder="123456", key="otp_code_input", max_chars=6)
        
        with col2:
            if st.button("Validar código"):
                if email_otp and otp_code:
                    try:
                        response = supabase.auth.verify_otp({
                            "email": email_otp, 
                            "token": otp_code, 
                            "type": "email"
                        })
                        
                        if response.user:
                            st.session_state['usuario'] = response.user
                            st.success("✅ ¡Acceso concedido!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error("❌ Código incorrecto o expirado.")
                else:
                    st.warning("Completa ambos campos.")

# --- 7. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # --- INFORMACIÓN SOBRE CAMBIO DE CONTRASEÑA ---
        with st.expander("🔐 Cambiar Contraseña"):
            st.write("**Para cambiar tu contraseña:**")
            st.write("1. Cierra sesión (botón abajo)")
            st.write("2. Ve a la pestaña 'Recuperar Contraseña'")
            st.write("3. Usa la opción de correo electrónico")
            st.write("4. Haz clic en el enlace del correo")
            st.write("5. Establece tu nueva contraseña")
            
            st.success("✅ Método seguro y confiable.")
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", type="primary"):
            supabase.auth.sign_out()
            st.session_state['usuario'] = None
            st.success("Sesión cerrada correctamente")
            time.sleep(1)
            st.rerun()
    
    # --- ÁREA PRINCIPAL ---
    st.title("Panel de Control 🧱")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"Bienvenido al sistema v1.11")
    
    with col2:
        st.metric("Usuario", "Activo", delta="Online")
    
    st.divider()
    
    # AQUÍ VA TU CONTENIDO PRINCIPAL
    st.subheader("Módulo de Control de Calidad")
    st.write("Selecciona una opción del menú para comenzar.")
    
    # Ejemplo de tabs para futuras secciones
    tab_a, tab_b, tab_c = st.tabs(["📊 Probetas", "🎯 Slump", "📈 Reportes"])
    
    with tab_a:
        st.info("Sección de control de probetas - Próximamente")
    
    with tab_b:
        st.info("Sección de medición de slump - Próximamente")
    
    with tab_c:
        st.info("Sección de reportes y análisis - Próximamente")

# --- 8. CONTROL DE FLUJO ---
# Prioridad 1: Si viene del enlace de recuperación
if st.session_state['modo_recuperacion']:
    mostrar_cambio_password()
# Prioridad 2: Si hay usuario logueado
elif st.session_state['usuario'] is not None:
    mostrar_app_principal()
# Prioridad 3: Pantalla de login
else:
    mostrar_acceso()