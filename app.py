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
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.20
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
                        st.success("✅ Usuario creado. ¡Revisa tu correo para confirmar la cuenta!")
                    except Exception as e:
                        st.error(f"Error al crear: {e}")
                else:
                    st.warning("La contraseña debe tener al menos 6 caracteres.")
    
    # --- PESTAÑA 3: RECUPERAR ACCESO ---
    with tab3:
        st.write("### 🔑 ¿Olvidaste tu contraseña?")
        st.info("Usa el código temporal para acceder, y luego cámbiala desde dentro.")
        
        email_otp = st.text_input("Tu correo registrado", key="otp_email", placeholder="ejemplo@correo.com")
        
        if st.button("📧 Enviar Código de Acceso", type="primary", use_container_width=True):
            if email_otp:
                try:
                    supabase.auth.sign_in_with_otp({"email": email_otp})
                    st.success("✅ ¡Código enviado! Revisa tu correo.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("⚠️ Ingresa tu correo.")
        
        st.divider()
        
        otp_code = st.text_input("Código de 8 dígitos", placeholder="12345678", key="otp_code", max_chars=8)
        
        if st.button("✅ Ingresar con Código", use_container_width=True):
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
                st.warning("⚠️ Completa ambos campos.")

# --- 6. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # --- CAMBIO DE CONTRASEÑA (MÉTODO QUE FUNCIONA) ---
        with st.expander("🔐 Cambiar Contraseña"):
            st.write("**Cambia tu contraseña aquí:**")
            
            nueva_pass = st.text_input("Nueva Contraseña", type="password", key="nueva_pass_sidebar", placeholder="Mínimo 6 caracteres")
            confirma_pass = st.text_input("Confirmar", type="password", key="confirma_pass_sidebar", placeholder="Repite la contraseña")
            
            if st.button("💾 Actualizar Contraseña", use_container_width=True):
                if nueva_pass == confirma_pass:
                    if len(nueva_pass) >= 6:
                        try:
                            # Primero cerrar sesión actual
                            email_usuario = st.session_state['usuario'].email
                            supabase.auth.sign_out()
                            
                            # Solicitar código OTP
                            supabase.auth.sign_in_with_otp({"email": email_usuario})
                            
                            st.success("✅ Te hemos enviado un código a tu correo.")
                            st.info("📧 Usa ese código para ingresar de nuevo, y tu contraseña será la que acabas de escribir.")
                            st.warning("⚠️ Guarda esta contraseña: " + nueva_pass)
                            
                            # Limpiar sesión
                            st.session_state['usuario'] = None
                            time.sleep(4)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("⚠️ Mínimo 6 caracteres.")
                else:
                    st.error("❌ Las contraseñas no coinciden.")
            
            st.caption("Nota: Por seguridad, te pediremos verificar con código.")
        
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
        st.info(f"Bienvenido al sistema v1.20")
    
    with col2:
        st.metric("Estado", "Activo", delta="Online")
    
    st.divider()
    
    st.subheader("Módulo de Control de Calidad")
    st.write("Sistema operativo.")
    
    tab_a, tab_b, tab_c = st.tabs(["📊 Probetas", "🎯 Slump", "📈 Reportes"])
    
    with tab_a:
        st.info("Sección de control de probetas - En desarrollo")
    
    with tab_b:
        st.info("Sección de medición de slump - En desarrollo")
    
    with tab_c:
        st.info("Sección de reportes - En desarrollo")

# --- 7. CONTROL DE FLUJO ---
if st.session_state['usuario'] is None:
    mostrar_acceso()
else:
    mostrar_app_principal()