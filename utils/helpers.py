"""
Funciones auxiliares y utilidades
Cálculos, validaciones y funciones reutilizables
"""

def calcular_muestras_necesarias(volumen_total, num_camiones):
    """
    Calcula el número de muestras necesarias según normativa peruana
    
    Args:
        volumen_total (float): Volumen total de concreto en m³
        num_camiones (int): Número de camiones mixer
    
    Returns:
        dict: Diccionario con el desglose de muestras por criterio
    """
    # Criterio 1: Cada 120 m³
    por_volumen = max(1, int(volumen_total / 120))
    
    # Criterio 2: Por día (mínimo 1)
    por_dia = 1
    
    # Criterio 3: Cada 5 camiones (aprox 40 m³)
    por_camiones = max(1, int(num_camiones / 5))
    
    # Criterio 4: Cada 50 m³ en elementos estructurales
    por_elemento = max(1, int(volumen_total / 50))
    
    # Se aplica el criterio más restrictivo
    muestras_necesarias = max(por_volumen, por_dia, por_camiones, por_elemento)
    
    return {
        'total': muestras_necesarias,
        'por_volumen': por_volumen,
        'por_dia': por_dia,
        'por_camiones': por_camiones,
        'por_elemento': por_elemento
    }

def validar_slump(slump_medido, slump_especificado, tolerancia=1.5):
    """
    Valida si el slump medido está dentro de la tolerancia
    
    Args:
        slump_medido (float): Valor de slump medido en pulgadas
        slump_especificado (float): Valor de slump especificado en pulgadas
        tolerancia (float): Tolerancia permitida en pulgadas (default: 1.5")
    
    Returns:
        tuple: (bool, str) - (cumple_especificacion, mensaje)
    """
    diferencia = abs(slump_medido - slump_especificado)
    
    if diferencia <= tolerancia:
        return True, f"✅ Slump conforme (diferencia: {diferencia:.1f}\")"
    else:
        return False, f"❌ Slump fuera de especificación (diferencia: {diferencia:.1f}\")"

def calcular_resistencia_promedio(resistencias):
    """
    Calcula la resistencia promedio de un set de probetas
    
    Args:
        resistencias (list): Lista de resistencias en kg/cm²
    
    Returns:
        float: Resistencia promedio
    """
    if not resistencias:
        return 0
    return sum(resistencias) / len(resistencias)

def validar_resistencia(resistencia_promedio, fc_diseño):
    """
    Valida si la resistencia cumple con el diseño según ACI 318
    
    Args:
        resistencia_promedio (float): Resistencia promedio en kg/cm²
        fc_diseño (float): Resistencia de diseño en kg/cm²
    
    Returns:
        tuple: (bool, str) - (cumple_especificacion, mensaje)
    """
    porcentaje = (resistencia_promedio / fc_diseño) * 100
    
    if resistencia_promedio >= fc_diseño:
        return True, f"✅ Concreto conforme ({porcentaje:.1f}% del f'c)"
    else:
        return False, f"❌ Concreto no conforme ({porcentaje:.1f}% del f'c)"

def generar_codigo_muestra(fecha, consecutivo):
    """
    Genera un código único para una muestra
    
    Args:
        fecha (datetime): Fecha del muestreo
        consecutivo (int): Número consecutivo del día
    
    Returns:
        str: Código de muestra (ej: M-20240115-001)
    """
    fecha_str = fecha.strftime("%Y%m%d")
    return f"M-{fecha_str}-{consecutivo:03d}"

def generar_codigo_probeta(codigo_muestra, letra):
    """
    Genera código para una probeta individual
    
    Args:
        codigo_muestra (str): Código de la muestra
        letra (str): Letra identificadora (A, B, C, etc.)
    
    Returns:
        str: Código de probeta (ej: M-20240115-001-A)
    """
    return f"{codigo_muestra}-{letra}"