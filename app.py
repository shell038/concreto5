import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Calidad", page_icon="🏗️")

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .footer-personalizado {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: #f0f2f6; text-align: center; padding: 10px;
            font-size: 14px; font-weight: bold; border-top: 1px solid #ddd;
        }
    </style>
    <div class="footer-personalizado">
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.08
    </div>
""", unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE VARIABLES (ESTADO) ---
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None
if 'refresh_token' not in st.session_state:
    st.session_state['refresh_token'] = None

# --- 4. CONEXIÓN A SUPABASE Y RECONEXIÓN AUTOMÁTICA ---
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase = create_client(url, key)

    # [CRÍTICO] ESTO ES LO QUE ARREGLA EL "AUTH SESSION MISSING"
    # Si existen tokens guardados, reconectamos la sesión ANTES de hacer cualquier otra cosa.
    if st.session_state['access_token'] and st.session_state['refresh_token']:
        try:
            supabase.auth.set_session(
                st.session_state['access_token'], 
                st.session_state['refresh_token']
            )
        except Exception as e:
            # Si el token caducó, limpiamos todo para evitar bucles de error
            st.session_state['usuario'] = None
            st.session_state['access_token'] = None
            st.session_state['refresh_token'] = None
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.stop()

# --- 5. PANTALLA DE ACCESO (LOGIN / OTP) ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Ingreso con Código"])
    
    # --- TAB 1: LOGIN CON CLAVE ---
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Correo", key="log_email")
            password = st.text_input("Contraseña", type="password", key="log_pass")
            if st.form_submit_button("Ingresar", type="primary"):
                try:
                    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    # GUARDAMOS LAS LLAVES
                    st.session_state['usuario'] = session.user
                    st.session_state['access_token'] = session.access_token
                    st.session_state['refresh_token'] = session.refresh_token
                    st.success("✅ Bienvenido")
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("❌ Credenciales incorrectas")

    # --- TAB 2: REGISTRO ---
    with tab2:
        st.info("Registro de nuevos ingenieros.")
        with st.form("signup_form"):
            new_email = st.text_input("Correo", key="new_email")
            new_pass = st.text_input("Contraseña", type="password", key="new_pass")
            if st.form_submit_button("Registrar"):
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("✅ Usuario creado. Revisa tu correo.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- TAB 3: INGRESO CON CÓDIGO (OTP) ---
    with tab3:
        st.write("Usa esta opción si olvidaste tu contraseña.")
        email_otp = st.text_input("Tu correo registrado", key="otp_email")
        
        if st.button("1. Enviar Código"):
            if email_otp:
                try:
                    supabase.auth.sign_in_with_otp({"email": email_otp})
                    st.info("📧 Código enviado. Revisa tu correo.")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        otp_code = st.text_input("Ingresa el código de 6 dígitos", key="otp_code_in")
        
        if st.button("2. Validar y Entrar", type="primary"):
            if email_otp and otp_code:
                try:
                    # Canjeamos código por sesión
                    session = supabase.auth.verify_otp({
                        "email": email_otp, 
                        "token": otp_code, 
                        "type": "magiclink"
                    })
                    
                    if session.user:
                        # GUARDAMOS LAS LLAVES (CRÍTICO)
                        st.session_state['usuario'] = session.user
                        st.session_state['access_token'] = session.access_token
                        st.session_state['refresh_token'] = session.refresh_token
                        
                        st.success("✅ Código correcto. Entrando...")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ Código incorrecto o expirado.")
            else:
                st.warning("Faltan datos.")

# --- 6. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # --- MÓDULO DE CAMBIO DE CONTRASEÑA ---
        with st.expander("🔐 Cambiar Contraseña"):
            with st.form("change_pass_form"):
                new_pass = st.text_input("Nueva contraseña", type="password")
                confirm_pass = st.text_input("Confirmar contraseña", type="password")
                
                if st.form_submit_button("Actualizar Clave"):
                    if new_pass == confirm_pass and len(new_pass) >= 6:
                        try:
                            # Como ya reconectamos en la línea 40, esto DEBE funcionar directo
                            supabase.auth.update_user({"password": new_pass})
                            st.success("✅ ¡Clave actualizada correctamente!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Las claves no coinciden o son muy cortas.")

        st.divider()
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            # Limpiamos todo para que no quede rastro
            st.session_state['usuario'] = None
            st.session_state['access_token'] = None
            st.session_state['refresh_token'] = None
            st.rerun()
            
    st.title("Panel de Control 🧱")
    st.info("Bienvenido al sistema v1.08")

# --- 7. CONTROL DE FLUJO ---
# Si hay usuario, mostramos la app. Si no, el login.
if st.session_state['usuario']:
    mostrar_app_principal()
else:
    mostrar_acceso()