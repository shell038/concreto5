import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Control de Calidad", page_icon="🏗️")

# --- 2. ESTILOS ---
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
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.06
    </div>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN SUPABASE ---
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase = create_client(url, key)
except:
    st.error("⚠️ Error de conexión con Supabase.")
    st.stop()

# --- 4. VARIABLES DE SESIÓN ---
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None
# [CRÍTICO] Variable para guardar la llave maestra y evitar "Auth session missing"
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None

# --- 5. PANTALLA DE ACCESO ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Ingreso con Código"])
    
    # --- TAB 1: LOGIN ---
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Correo", key="log_email")
            password = st.text_input("Contraseña", type="password", key="log_pass")
            if st.form_submit_button("Ingresar", type="primary"):
                try:
                    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['usuario'] = session.user
                    st.session_state['access_token'] = session.access_token # Guardamos llave
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
                    st.success("✅ Revisa tu correo para confirmar.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- TAB 3: RECUPERAR (MÉTODO CÓDIGO NUMÉRICO) ---
    with tab3:
        st.write("Ingresa con un código temporal si olvidaste tu clave.")
        
        # PASO 1: ENVIAR
        email_otp = st.text_input("Tu correo registrado", key="otp_email")
        if st.button("1. Enviar Código"):
            if email_otp:
                try:
                    supabase.auth.sign_in_with_otp({"email": email_otp})
                    st.info("📧 Código enviado. Busca el número en tu correo.")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        
        # PASO 2: INGRESAR CÓDIGO
        st.write("Escribe el código aquí:")
        otp_code = st.text_input("Código de 6 dígitos", key="otp_code_input", placeholder="Ej: 123456")
        
        if st.button("2. Validar y Entrar", type="primary"):
            if email_otp and otp_code:
                try:
                    # Canjeamos el código por una sesión
                    session = supabase.auth.verify_otp({
                        "email": email_otp, 
                        "token": otp_code, 
                        "type": "magiclink"
                    })
                    
                    if session.user:
                        st.session_state['usuario'] = session.user
                        st.session_state['access_token'] = session.access_token # Guardamos llave aquí también
                        st.success("✅ ¡Código correcto! Entrando...")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ Código incorrecto o expirado.")
            else:
                st.warning("Falta el correo o el código.")

# --- 6. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # --- CAMBIO DE CONTRASEÑA ---
        with st.expander("🔐 Cambiar Contraseña"):
            with st.form("change_pass_form"):
                new_pass = st.text_input("Nueva contraseña", type="password")
                confirm_pass = st.text_input("Confirmar contraseña", type="password")
                
                if st.form_submit_button("Actualizar Clave"):
                    if new_pass == confirm_pass and len(new_pass) >= 6:
                        try:
                            # [TRUCO] Restauramos la sesión antes de intentar cambiar la clave
                            if st.session_state['access_token']:
                                supabase.auth.set_session(st.session_state['access_token'], "dummy_refresh")
                            
                            supabase.auth.update_user({"password": new_pass})
                            st.success("✅ ¡Clave actualizada!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Las contraseñas no coinciden o son muy cortas.")

        st.divider()
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state['usuario'] = None
            st.session_state['access_token'] = None
            st.rerun()
            
    st.title("Panel de Control 🧱")
    st.info("Bienvenido al sistema v1.06")

# --- 7. FLUJO ---
if st.session_state['usuario']:
    mostrar_app_principal()
else:
    mostrar_acceso()