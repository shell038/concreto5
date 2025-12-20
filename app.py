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
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.05
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
# [NUEVO] Variable para guardar la llave maestra
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None

# --- 5. PANTALLA DE ACCESO ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Recuperar Contraseña"])
    
    # LOGIN
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Correo", key="log_email")
            password = st.text_input("Contraseña", type="password", key="log_pass")
            if st.form_submit_button("Ingresar", type="primary"):
                try:
                    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['usuario'] = session.user
                    # [NUEVO] Guardamos el token de seguridad
                    st.session_state['access_token'] = session.access_token 
                    st.success("✅ Bienvenido")
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("❌ Credenciales incorrectas")

    # REGISTRO
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

    # RECUPERAR
    with tab3:
        st.write("Te enviaremos un enlace mágico.")
        rec_email = st.text_input("Tu correo", key="rec_email")
        if st.button("Enviar Enlace"):
            try:
                # Ajusta esta URL a tu proyecto real
                mi_url = "https://concreto5-tu-proyecto.streamlit.app" 
                supabase.auth.sign_in_with_otp({
                    "email": rec_email,
                    "options": {"email_redirect_to": mi_url}
                })
                st.success("✅ Enlace enviado. Revisa tu correo.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- 6. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        
        with st.expander("🔐 Cambiar Contraseña"):
            with st.form("change_pass_form"):
                new_pass = st.text_input("Nueva contraseña", type="password")
                confirm_pass = st.text_input("Confirmar contraseña", type="password")
                
                if st.form_submit_button("Actualizar Clave"):
                    if new_pass == confirm_pass and len(new_pass) >= 6:
                        try:
                            # [NUEVO] Le recordamos a Supabase quiénes somos antes de actualizar
                            if st.session_state['access_token']:
                                supabase.auth.set_session(st.session_state['access_token'], "dummy_refresh_token")
                            
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
    st.info("Bienvenido al sistema v1.05")

# --- 7. FLUJO ---
if st.session_state['usuario']:
    mostrar_app_principal()
else:
    mostrar_acceso()