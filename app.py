"""
Sistema de Control de Calidad para Concreto en Obra
Archivo principal de la aplicación
Autor: Ing. Edson Pérez
Versión: 2.5
"""

import streamlit as st
from auth.login import mostrar_acceso, verificar_sesion
from components.sidebar import mostrar_sidebar
from modules.dashboard import mostrar_dashboard
from modules.muestreo import mostrar_muestreo
"""from modules.slump import mostrar_slump"""
"""from modules.probetas import mostrar_probetas"""
"""from modules.reportes import mostrar_reportes"""
from database.supabase_client import inicializar_supabase

# Configuración de página
st.set_page_config(
    page_title="Control de Calidad - Concreto",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS globales
def cargar_estilos():
    """Carga los estilos CSS personalizados de la aplicación"""
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
            Desarrollado por el Ing. Edson Pérez | Sistema de Calidad v2.5
        </div>
    """
    st.markdown(estilo_personalizado, unsafe_allow_html=True)

# Inicialización de la aplicación
def main():
    """Función principal que controla el flujo de la aplicación"""
    
    # Cargar estilos
    cargar_estilos()
    
    # Inicializar conexión a Supabase
    supabase = inicializar_supabase()
    
    # Verificar estado de sesión
    if not verificar_sesion():
        # Usuario no autenticado - mostrar pantalla de login
        mostrar_acceso(supabase)
    else:
        # Usuario autenticado - mostrar aplicación principal
        mostrar_aplicacion(supabase)

def mostrar_aplicacion(supabase):
    """Renderiza la aplicación principal después del login"""
    
    # Mostrar sidebar con información del usuario
    mostrar_sidebar(supabase)
    
    # Header principal
    st.title("Panel de Control 🧱")
    
    # Información del usuario y métricas
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**Bienvenido:** {st.session_state['usuario'].email}")
    with col2:
        st.metric("Estado", "Activo", delta="Online")
    with col3:
        st.metric("Versión", "v2.51")
    
    st.divider()
    
    # Menú de navegación principal
    modulo = st.selectbox(
        "🔧 Selecciona un Módulo:",
        [
            "🏠 Inicio",
            "📊 Registro de Muestreo",
            "🎯 Ensayo de Slump",
            "🧪 Probetas en Laboratorio",
            "📈 Reportes y Estadísticas"
        ],
        key="menu_principal"
    )
    
    st.divider()
    
    # Router - Renderiza el módulo seleccionado
    if modulo == "🏠 Inicio":
        mostrar_dashboard(supabase)
    elif modulo == "📊 Registro de Muestreo":
        mostrar_muestreo(supabase)
    elif modulo == "🎯 Ensayo de Slump":
        mostrar_slump(supabase)
    elif modulo == "🧪 Probetas en Laboratorio":
        mostrar_probetas(supabase)
    elif modulo == "📈 Reportes y Estadísticas":
        mostrar_reportes(supabase)

# Punto de entrada de la aplicación
if __name__ == "__main__":
    main()