"""
Cliente de conexión a Supabase
Maneja todas las operaciones con la base de datos
"""

import streamlit as st
from supabase import create_client

def inicializar_supabase():
    """
    Inicializa y retorna el cliente de Supabase
    
    Returns:
        Client: Cliente de Supabase configurado
    
    Raises:
        Exception: Si no se encuentran las credenciales
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
        return supabase
    except Exception as e:
        st.error("⚠️ Error: No se detectaron los secretos de conexión.")
        st.stop()

def guardar_registro_muestreo(supabase, datos):
    """
    Guarda un registro de muestreo en la base de datos
    
    Args:
        supabase: Cliente de Supabase
        datos (dict): Diccionario con los datos del muestreo
    
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    try:
        response = supabase.table('muestreos').insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

def obtener_registros_muestreo(supabase, filtros=None):
    """
    Obtiene registros de muestreo de la base de datos
    
    Args:
        supabase: Cliente de Supabase
        filtros (dict, optional): Filtros a aplicar en la consulta
    
    Returns:
        list: Lista de registros
    """
    try:
        query = supabase.table('muestreos').select('*')
        
        if filtros:
            for key, value in filtros.items():
                query = query.eq(key, value)
        
        response = query.execute()
        return response.data
    except Exception as e:
        st.error(f"Error al obtener registros: {e}")
        return []

def actualizar_registro(supabase, tabla, id, datos):
    """
    Actualiza un registro existente
    
    Args:
        supabase: Cliente de Supabase
        tabla (str): Nombre de la tabla
        id (int): ID del registro a actualizar
        datos (dict): Datos a actualizar
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        response = supabase.table(tabla).update(datos).eq('id', id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar: {e}")
        return False

def eliminar_registro(supabase, tabla, id):
    """
    Elimina un registro de la base de datos
    
    Args:
        supabase: Cliente de Supabase
        tabla (str): Nombre de la tabla
        id (int): ID del registro a eliminar
    
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        response = supabase.table(tabla).delete().eq('id', id).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
        return False