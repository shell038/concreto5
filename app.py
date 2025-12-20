import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Calidad", page_icon="🏗️")

# --- 2. ESTILOS CSS (Visuales) ---
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
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.02.04
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
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None

# --- 5. PANTALLA DE ACCESO (LOGIN / REGISTRO / RECUPERAR) ---
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
                    st.session_state['access_token'] = response.session.access_token
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
            new_pass = st.text_input("Nueva Contraseña", type="password", key="new_pass", placeholder="Ingresa tu contraseña")
            submit_new = st.form_submit_button("Registrar Usuario")
            
            if submit_new:
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("✅ Usuario creado. ¡Revisa tu correo para confirmar la cuenta!")
                except Exception as e:
                    st.error(f"Error al crear: {e}")
    
    # --- PESTAÑA 3: INGRESO CON CÓDIGO ---
    with tab3:
        st.write("Si olvidaste tu clave, ingresa usando un código temporal que enviaremos a tu correo.")
        
        email_otp = st.text_input("Ingresa tu correo registrado", key="otp_email")
        
        if st.button("1. Enviar Código de Acceso"):
            if email_otp:
                try:
                    supabase.auth.sign_in_with_otp({"email": email_otp})
                    st.info("📧 Código enviado. Revisa tu bandeja de entrada (busca el número grande).")
                except Exception as e:
                    st.error(f"Error al enviar: {e}")
            else:
                st.warning("Por favor, escribe tu correo primero.")
        
        st.divider()
        
        st.write("Una vez tengas el código, ingrésalo aquí:")
        otp_code = st.text_input("Código de 6 dígitos", placeholder="Ej: 123456", key="otp_code_input")
        
        if st.button("2. Validar y Entrar", type="primary"):
            if email_otp and otp_code:
                try:
                    response = supabase.auth.verify_otp({
                        "email": email_otp, 
                        "token": otp_code, 
                        "type": "email"
                    })
                    
                    if response.user:
                        st.session_state['usuario'] = response.user
                        st.session_state['access_token'] = response.session.access_token
                        st.success("✅ ¡Código correcto! Iniciando sesión...")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ El código es incorrecto o ha expirado. Pide uno nuevo.")
            else:
                st.warning("Debes ingresar el correo y el código.")

# --- 6. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # --- CAMBIO DE CONTRASEÑA CORREGIDO ---
        with st.expander("🔐 Cambiar Contraseña"):
            with st.form("change_pass_form"):
                new_password = st.text_input("Nueva contraseña", type="password")
                confirm_password = st.text_input("Confirmar contraseña", type="password")
                submit_change = st.form_submit_button("Actualizar Clave")
            
                if submit_change:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            try:
                                # Configurar el token de acceso antes de actualizar
                                supabase.postgrest.auth(st.session_state['access_token'])
                                
                                response = supabase.auth.update_user({"password": new_password})
                                
                                if response.user:
                                    st.success("✅ ¡Contraseña actualizada!")
                                    time.sleep(1)
                                else:
                                    st.error("Error: Auth session missing!")
                                    st.info("💡 Intenta cerrar sesión y volver a entrar.")
                            except Exception as e:
                                st.error(f"Error: {e}")
                                st.info("💡 Cierra sesión e ingresa de nuevo para cambiar tu contraseña.")
                        else:
                            st.warning("Mínimo 6 caracteres.")
                    else:
                        st.error("Las contraseñas no coinciden.")
        
        st.divider()
        
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state['usuario'] = None
            st.session_state['access_token'] = None
            st.rerun()
    
    # --- ÁREA PRINCIPAL ---
    st.title("Panel de Control 🧱")
    st.info("Bienvenido al sistema v1.08")
    st.divider()
    
    st.info("Bienvenido al módulo de control. Selecciona una opción en el menú.")

# --- 7. CONTROL DE FLUJO ---
if st.session_state['usuario'] is None:
    mostrar_acceso()
else:
    mostrar_app_principal()