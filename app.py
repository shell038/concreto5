import streamlit as st
from supabase import create_client
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Calidad", page_icon="🏗️")

# --- 2. GESTIÓN DE ESTADO (Inicialización de variables) ---
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None
if 'sesion_activa' not in st.session_state:
    st.session_state['sesion_activa'] = None

# --- 3. ESTILOS CSS ---
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
            z-index: 999;
        }
    </style>
    <div class="footer-personalizado">
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.03
    </div>
"""
st.markdown(estilo_personalizado, unsafe_allow_html=True)

# --- 4. CONEXIÓN A SUPABASE Y RESTAURACIÓN DE SESIÓN ---
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase = create_client(url, key)
    
    # [CRÍTICO] RESTAURAR SESIÓN SI EXISTE
    # Esto evita el error "Auth session missing" al recargar la página
    if st.session_state['sesion_activa']:
        try:
            supabase.auth.set_session(
                st.session_state['sesion_activa'].access_token, 
                st.session_state['sesion_activa'].refresh_token
            )
        except Exception as e:
            # Si el token venció o hay error, limpiamos todo para obligar a reloguear
            st.session_state['usuario'] = None
            st.session_state['sesion_activa'] = None
except Exception as e:
    st.error(f"⚠️ Error de conexión con la base de datos: {e}")
    st.stop()

# --- 5. PANTALLA DE ACCESO ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Ingreso con Código (Olvidé Clave)"])
    
    # --- LOGIN CLÁSICO ---
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico", key="login_email")
            password = st.text_input("Contraseña", type="password", key="login_pass")
            submit = st.form_submit_button("Ingresar al Sistema", type="primary")
            
            if submit:
                try:
                    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['usuario'] = session.user
                    st.session_state['sesion_activa'] = session # <--- GUARDAMOS LA SESIÓN TÉCNICA
                    st.success("✅ Acceso autorizado")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error("❌ Usuario o contraseña incorrectos")

    # --- REGISTRO DE USUARIO ---
    with tab2:
        st.info("Solo para personal autorizado.")
        with st.form("signup_form"):
            new_email = st.text_input("Nuevo Correo", key="new_email")
            new_pass = st.text_input("Nueva Contraseña", type="password", key="new_pass")
            submit_new = st.form_submit_button("Registrar Usuario")
            
            if submit_new:
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("✅ Usuario creado. ¡Revisa tu correo para confirmar!")
                except Exception as e:
                    st.error(f"Error al crear: {e}")

    # --- INGRESO CON CÓDIGO (OTP) ---
    with tab3:
        st.write("Si olvidaste tu clave, ingresa usando un código temporal.")
        
        # Paso 1: Pedir código
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
        
        # Paso 2: Validar código
        st.write("Una vez tengas el código, ingrésalo aquí:")
        otp_code = st.text_input("Código de 6 dígitos", placeholder="Ej: 123456", key="otp_code_input")
        
        if st.button("2. Validar y Entrar", type="primary"):
            if email_otp and otp_code:
                try:
                    session = supabase.auth.verify_otp({
                        "email": email_otp, 
                        "token": otp_code, 
                        "type": "magiclink"
                    })
                    
                    if session.user:
                        st.session_state['usuario'] = session.user
                        st.session_state['sesion_activa'] = session # <--- GUARDAMOS LA SESIÓN TÉCNICA AQUÍ TAMBIÉN
                        st.success("✅ ¡Código correcto! Iniciando sesión...")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ El código es incorrecto o ha expirado. Pide uno nuevo.")
            else:
                st.warning("Debes ingresar el correo y el código.")

# --- 6. APP PRINCIPAL (Panel de Control) ---
def mostrar_app_principal():
    with st.sidebar:
        # --- Datos del Usuario ---
        st.write(f"👤 Ing. {st.session_state['usuario'].email}")
        st.divider()

        # --- Cambio de Contraseña ---
        with st.expander("🔐 Cambiar Contraseña"):
            with st.form("change_pass_form"):
                new_password = st.text_input("Nueva Contraseña", type="password")
                confirm_password = st.text_input("Confirmar Contraseña", type="password")
                submit_change = st.form_submit_button("Actualizar Clave")
            
                if submit_change:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            try:
                                supabase.auth.update_user({"password": new_password})
                                st.success("✅ ¡Contraseña actualizada!")
                                time.sleep(1)
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.warning("Mínimo 6 caracteres.")
                    else:
                        st.error("Las contraseñas no coinciden.")

        # --- Botón de Salida ---
        st.divider()
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state['usuario'] = None
            st.session_state['sesion_activa'] = None # <--- LIMPIEZA TOTAL
            st.rerun()
            
    # --- ÁREA DE TRABAJO ---
    st.title("Panel de Control 🧱")
    st.divider()
    st.info("Bienvenido al módulo de control. Selecciona una opción en el menú.")

# --- 7. CONTROL DE FLUJO ---
if st.session_state['usuario'] is None:
    mostrar_acceso()
else:
    mostrar_app_principal()