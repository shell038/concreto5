"""
Módulo de Dashboard
Pantalla principal con métricas y accesos rápidos
"""

import streamlit as st

def mostrar_dashboard(supabase):
    """
    Renderiza el dashboard principal con métricas y accesos rápidos
    
    Args:
        supabase: Cliente de Supabase
    """
    st.subheader("Dashboard - Control de Calidad de Concreto")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Muestras Hoy", "0", delta="0")
    with col2:
        st.metric("Probetas Activas", "0", delta="0")
    with col3:
        st.metric("Ensayos Pendientes", "0", delta="0")
    with col4:
        st.metric("% Conformidad", "0%", delta="0%")
    
    st.divider()
    
    # Accesos rápidos
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📋 **Accesos Rápidos**")
        if st.button("➕ Nuevo Registro de Muestreo", use_container_width=True):
            st.session_state['menu_principal'] = "📊 Registro de Muestreo"
            st.rerun()
        if st.button("🔬 Registrar Ensayo de Slump", use_container_width=True):
            st.session_state['menu_principal'] = "🎯 Ensayo de Slump"
            st.rerun()
        if st.button("📊 Ver Reportes", use_container_width=True):
            st.session_state['menu_principal'] = "📈 Reportes y Estadísticas"
            st.rerun()
    
    with col2:
        st.warning("⚠️ **Próximos Ensayos**")
        st.write("No hay ensayos programados")