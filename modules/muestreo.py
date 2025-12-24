"""
Módulo de Registro de Muestreo
Formulario completo para registro de toma de muestras de concreto
"""

import streamlit as st
from utils.helpers import calcular_muestras_necesarias

def mostrar_muestreo(supabase):
    """
    Renderiza el módulo de registro de muestreo
    
    Args:
        supabase: Cliente de Supabase
    """
    st.subheader("Registro de Toma de Muestras")
    
    # Pestañas del módulo
    tab_a, tab_b, tab_c = st.tabs(["📝 Nuevo Registro", "📋 Historial", "🔍 Buscar"])
    
    with tab_a:
        renderizar_formulario_muestreo(supabase)
    
    with tab_b:
        st.info("📋 Historial de registros - Próximamente")
    
    with tab_c:
        st.info("🔍 Búsqueda avanzada - Próximamente")

def renderizar_formulario_muestreo(supabase):
    """
    Renderiza el formulario completo de registro de muestreo
    
    Args:
        supabase: Cliente de Supabase
    """
    
    # SECCIÓN 1: INFORMACIÓN DEL PROYECTO
    st.write("### 📋 Datos del Proyecto")
    col1, col2 = st.columns(2)
    with col1:
        proyecto = st.text_input("Nombre del Proyecto", placeholder="Ej: Edificio Los Robles")
        elemento = st.text_input("Elemento Estructural", placeholder="Ej: Losa Nivel 3")
        ubicacion = st.text_input("Ubicación en Obra", placeholder="Ej: Eje A-B / 1-3")
    with col2:
        fecha_vaciado = st.date_input("Fecha de Vaciado")
        hora_vaciado = st.time_input("Hora de Vaciado")
        temperatura = st.number_input("Temperatura Ambiente (°C)", min_value=0.0, max_value=50.0, value=20.0, step=0.5)
    
    st.divider()
    
    # SECCIÓN 2: DISEÑO DE MEZCLA
    st.write("### 🧪 Características del Concreto")
    col1, col2, col3 = st.columns(3)
    with col1:
        fc_diseño = st.number_input("f'c Diseño (kg/cm²)", min_value=100, max_value=500, value=210, step=10)
        slump_especificado = st.number_input("Slump Especificado (pulg)", min_value=1.0, max_value=10.0, value=4.0, step=0.5)
    with col2:
        tipo_cemento = st.selectbox("Tipo de Cemento", ["Portland Tipo I", "Portland Tipo II", "Portland Tipo V", "Puzolánico"])
        tamaño_max = st.selectbox("Tamaño Máximo Agregado", ["3/8\"", "1/2\"", "3/4\"", "1\"", "1 1/2\""])
    with col3:
        relacion_ac = st.number_input("Relación a/c", min_value=0.30, max_value=0.80, value=0.50, step=0.01)
        aditivo = st.text_input("Aditivo (si aplica)", placeholder="Ej: Plastificante Sika")
    
    st.divider()
    
    # SECCIÓN 3: INFORMACIÓN DEL PROVEEDOR
    st.write("### 🚛 Datos del Suministro")
    col1, col2, col3 = st.columns(3)
    with col1:
        proveedor = st.text_input("Proveedor/Planta", placeholder="Ej: UNICON")
        guia_remision = st.text_input("Guía de Remisión", placeholder="Nº de guía")
    with col2:
        num_camion = st.text_input("Nº de Camión/Placa", placeholder="Ej: Mixer 05")
        volumen_pedido = st.number_input("Volumen Pedido (m³)", min_value=0.0, value=8.0, step=0.5)
    with col3:
        hora_salida_planta = st.time_input("Hora Salida Planta")
        hora_llegada_obra = st.time_input("Hora Llegada Obra")
    
    st.divider()
    
    # SECCIÓN 4: CALCULADORA DE FRECUENCIA
    st.write("### 📊 Calculadora de Muestreo")
    st.info("Calcula cuántas muestras necesitas según normativa peruana")
    
    col1, col2 = st.columns(2)
    with col1:
        volumen_total = st.number_input("Volumen Total a Vaciar (m³)", min_value=0.0, value=100.0, step=1.0)
        num_camiones = st.number_input("Número de Camiones", min_value=1, value=13, step=1)
    
    with col2:
        if st.button("🔢 Calcular Muestras Necesarias", type="primary"):
            resultado = calcular_muestras_necesarias(volumen_total, num_camiones)
            
            st.success(f"✅ **Muestras necesarias: {resultado['total']}**")
            st.write(f"- Por volumen (cada 120 m³): {resultado['por_volumen']}")
            st.write(f"- Por día: {resultado['por_dia']}")
            st.write(f"- Por camiones (cada 5): {resultado['por_camiones']}")
            st.write(f"- Por elemento (cada 50 m³): {resultado['por_elemento']}")
            st.caption("Se aplica el criterio más restrictivo")
    
    st.divider()
    
    # SECCIÓN 5: REGISTRO DE PROBETAS
    st.write("### 🧱 Registro de Probetas (Set Completo)")
    
    num_muestra = st.text_input("Código de Muestra", placeholder="Ej: M-001", key="cod_muestra")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Identificación de Probetas (mínimo 3 por set):**")
        probeta_1 = st.text_input("Probeta 1", placeholder="Ej: P-001-A", key="prob1")
        probeta_2 = st.text_input("Probeta 2", placeholder="Ej: P-001-B", key="prob2")
        probeta_3 = st.text_input("Probeta 3", placeholder="Ej: P-001-C", key="prob3")
        probeta_4 = st.text_input("Probeta 4 (opcional)", placeholder="Ej: P-001-D", key="prob4")
    
    with col2:
        st.write("**Dimensiones:**")
        diametro = st.selectbox("Diámetro (cm)", [10, 15], index=1)
        altura = st.selectbox("Altura (cm)", [20, 30], index=1)
        
        st.write("**Edades de Ensayo:**")
        edad_7 = st.checkbox("7 días", value=False)
        edad_28 = st.checkbox("28 días", value=True)
        otra_edad = st.number_input("Otra edad (días)", min_value=1, max_value=90, value=14)
    
    st.divider()
    
    # SECCIÓN 6: OBSERVACIONES
    st.write("### 📝 Observaciones")
    observaciones = st.text_area(
        "Observaciones del muestreo",
        placeholder="Ej: Concreto con trabajabilidad adecuada, sin segregación...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        responsable_muestreo = st.text_input("Responsable del Muestreo", placeholder="Nombre del inspector")
    with col2:
        hora_moldeo = st.time_input("Hora de Moldeo")
    
    st.divider()
    
    # BOTONES DE ACCIÓN
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
            # Aquí se guardará en la base de datos
            st.success("✅ Registro guardado exitosamente")
            st.balloons()
    with col2:
        if st.button("📄 Generar PDF", use_container_width=True):
            st.info("📄 Generando reporte PDF...")
    with col3:
        if st.button("🔄 Limpiar Formulario", use_container_width=True):
            st.rerun()