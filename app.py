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
        Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v1.15
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
if 'acceso_temporal' not in st.session_state:
    st.session_state['acceso_temporal'] = False

# --- 5. PANTALLA DE ACCESO ---
def mostrar_acceso():
    st.title("🏗️ Concreto 5")
    st.write("Control de Calidad para Concreto en Obra")
    
    tab1, tab2, tab3 = st.tabs(["Iniciar Sesión", "Crear Usuario", "Recuperar Acceso"])
    
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
                    st.session_state['acceso_temporal'] = False
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
    
    # --- PESTAÑA 3: RECUPERAR CON CÓDIGO ---
    with tab3:
        st.write("### 🔑 Recuperación de Acceso")
        st.info("Te enviaremos un código de 8 dígitos a tu correo.")
        
        # PASO 1: Solicitar código
        st.write("**Paso 1:** Ingresa tu correo")
        email_otp = st.text_input("Correo registrado", key="otp_email", placeholder="ejemplo@correo.com")
        
        if st.button("📧 Enviar Código", type="primary", use_container_width=True):
            if email_otp:
                try:
                    supabase.auth.sign_in_with_otp({"email": email_otp})
                    st.success("✅ ¡Código enviado! Revisa tu correo (también spam).")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("⚠️ Ingresa tu correo primero.")
        
        st.divider()
        
        # PASO 2: Ingresar código
        st.write("**Paso 2:** Ingresa el código que recibiste")
        otp_code = st.text_input("Código (8 dígitos)", placeholder="12345678", key="otp_code_input", max_chars=8)
        
        if st.button("✅ Validar e Ingresar", use_container_width=True):
            if email_otp and otp_code:
                try:
                    response = supabase.auth.verify_otp({
                        "email": email_otp, 
                        "token": otp_code, 
                        "type": "email"
                    })
                    
                    if response.user:
                        st.session_state['usuario'] = response.user
                        st.session_state['acceso_temporal'] = True
                        st.success("✅ ¡Código correcto! Accediendo...")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ Código incorrecto o expirado. Solicita uno nuevo.")
            else:
                st.warning("⚠️ Debes ingresar el correo y el código.")

# --- 6. PANTALLA DE CAMBIO DE CONTRASEÑA (OBLIGATORIO) ---
def mostrar_cambio_obligatorio():
    st.title("🔐 Establecer Nueva Contraseña")
    st.warning("⚠️ Accediste con código temporal. Por seguridad, debes crear una nueva contraseña permanente.")
    
    with st.form("cambio_obligatorio"):
        nueva = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirma = st.text_input("Confirmar Contraseña", type="password", placeholder="Repite la contraseña")
        submit = st.form_submit_button("💾 Guardar y Continuar", type="primary")
        
        if submit:
            if nueva == confirma:
                if len(nueva) >= 6:
                    try:
                        response = supabase.auth.update_user({"password": nueva})
                        if response.user:
                            st.success("✅ ¡Contraseña actualizada exitosamente!")
                            st.session_state['acceso_temporal'] = False
                            st.info("Ahora puedes usar tu nueva contraseña para ingresar.")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Error al actualizar. Intenta de nuevo.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("⚠️ La contraseña debe tener al menos 6 caracteres.")
            else:
                st.error("❌ Las contraseñas no coinciden.")
    
    st.divider()
    
    if st.button("Saltar este paso (no recomendado)"):
        st.session_state['acceso_temporal'] = False
        st.rerun()

# --- 7. APP PRINCIPAL ---
def mostrar_app_principal():
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # --- CAMBIO DE CONTRASEÑA ---
        with st.expander("🔐 Cambiar Contraseña"):
            with st.form("cambiar_pass_sidebar"):
                actual = st.text_input("Contraseña Actual", type="password", key="pass_actual")
                nueva = st.text_input("Nueva Contraseña", type="password", key="pass_nueva")
                confirma = st.text_input("Confirmar Nueva", type="password", key="pass_confirma")
                cambiar = st.form_submit_button("Actualizar")
                
                if cambiar:
                    # Primero verificar que la contraseña actual sea correcta
                    if nueva == confirma and len(nueva) >= 6:
                        try:
                            # Intentar login con contraseña actual para verificarla
                            test_login = supabase.auth.sign_in_with_password({
                                "email": st.session_state['usuario'].email,
                                "password": actual
                            })
                            
                            # Si llegó aquí, la contraseña actual es correcta
                            response = supabase.auth.update_user({"password": nueva})
                            if response.user:
                                st.success("✅ ¡Contraseña actualizada!")
                                time.sleep(1)
                            else:
                                st.error("Error al actualizar.")
                        except:
                            st.error("❌ Contraseña actual incorrecta.")
                    elif nueva != confirma:
                        st.error("❌ Las contraseñas no coinciden.")
                    else:
                        st.warning("⚠️ Mínimo 6 caracteres.")
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", type="primary"):
            supabase.auth.sign_out()
            st.session_state['usuario'] = None
            st.session_state['acceso_temporal'] = False
            st.success("Sesión cerrada")
            time.sleep(1)
            st.rerun()
    
    # --- ÁREA PRINCIPAL ---
    st.title("Panel de Control 🧱")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"Bienvenido al sistema v1.15")
    
    with col2:
        st.metric("Estado", "Activo", delta="Online")
    
    st.divider()
    
    # CONTENIDO PRINCIPAL
    st.subheader("Módulo de Control de Calidad")
    st.write("Sistema listo para trabajar.")
    
    tab_a, tab_b, tab_c = st.tabs(["📊 Probetas", "🎯 Slump", "📈 Reportes"])
    
    with tab_a:
        st.info("Sección de control de probetas - En desarrollo")
    
    with tab_b:
        st.info("Sección de medición de slump - En desarrollo")
    
    with tab_c:
        st.info("Sección de reportes y análisis - En desarrollo")

# --- 8. CONTROL DE FLUJO ---
if st.session_state['usuario'] is None:
    mostrar_acceso()
elif st.session_state['acceso_temporal']:
    mostrar_cambio_obligatorio()
else:
    mostrar_app_principal()