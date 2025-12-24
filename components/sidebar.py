"""
Componente de Sidebar
Muestra información del usuario y opciones de navegación
"""

import streamlit as st
from auth.login import cerrar_sesion

def mostrar_sidebar(supabase):
    """
    Renderiza el sidebar con información del usuario y opciones
    
    Args:
        supabase: Cliente de Supabase
    """
    with st.sidebar:
        # Información del usuario
        st.write(f"👤 {st.session_state['usuario'].email}")
        st.divider()
        
        # Información sobre cambio de contraseña
        st.info("🔐 **Para cambiar tu contraseña:** Cierra sesión y usa la pestaña 'Cambiar Contraseña'.")
        
        st.divider()
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", type="primary", use_container_width=True):
            cerrar_sesion(supabase)