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
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v2.0
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

# --- 5. PANTALLA DE ACCESO ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Olvidé mi Contraseña"])
    
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
                        st.success("✅ Usuario creado. ¡Revisa tu correo para confirmar!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("La contraseña debe tener al menos 6 caracteres.")
    
    # --- PESTAÑA 3: OLVIDÉ MI CONTRASEÑA ---
    with tab3:
        st.write("### 🔑 Recuperar Acceso")
        st.info("Te enviaremos un código de 8 dígitos para ingresar temporalmente.")
        
        email_otp = st.text_input("Tu correo", key="otp_email", placeholder="ejemplo@correo.com")
        
        if st.button("📧 Enviar Código", type="primary", use_container_width=True):
            if email_otp:
                try:
                    supabase.auth.sign_in_with_otp({"email": email_otp})
                    st.success("✅ Código enviado. Revisa tu correo.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Ingresa tu correo.")
        
        st.divider()
        
        otp_code = st.text_input("Código de 8 dígitos", placeholder="12345678", key="otp_code", max_chars=8)
        
        if st.button("✅ Ingresar", use_container_width=True):
            if email_otp and otp_code:
                try:
                    response = supabase.auth.verify_otp({
                        "email": email_otp, 
                        "token": otp_code, 
                        "type": "email"
                    })
                    
                    if response.user:
                        st.session_state['usuario'] = response.user
                        st.success("✅ Acceso concedido")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ Código incorrecto o expirado.")
            else:
                st.warning("Completa ambos campos.")

# --- 6. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        st.info("💡 **Cambio de contraseña:** Contacta al administrador del sistema.")
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", type="primary"):
            supabase.auth.sign_out()
            st.session_state['usuario'] = None
            st.success("Sesión cerrada")
            time.sleep(1)
            st.rerun()
    
    # --- ÁREA PRINCIPAL ---
    st.title("Panel de Control 🧱")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.success(f"✅ Bienvenido al sistema v2.0")
    
    with col2:
        st.metric("Estado", "Activo", delta="Online")
    
    st.divider()
    
    st.subheader("Módulo de Control de Calidad")
    
    tab_a, tab_b, tab_c = st.tabs(["📊 Probetas", "🎯 Slump", "📈 Reportes"])
    
    with tab_a:
        st.info("Módulo de probetas - En desarrollo")
    
    with tab_b:
        st.info("Módulo de slump - En desarrollo")
    
    with tab_c:
        st.info("Módulo de reportes - En desarrollo")

# --- 7. CONTROL DE FLUJO ---
if st.session_state['usuario'] is None:
    mostrar_acceso()
else:
    mostrar_app_principal()