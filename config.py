"""
Archivo de configuración para la calculadora de ampacidad
"""

# Constantes físicas
STEFAN_BOLTZMANN = 5.67e-8  # W/(m²·K⁴)
GRAVITY = 9.81  # m/s²
AIR_VISCOSITY = 1.8e-5  # Pa·s
AIR_THERMAL_CONDUCTIVITY = 0.024  # W/(m·K)
SEA_LEVEL_DENSITY = 1.204  # kg/m³

# Parámetros por defecto
DEFAULT_PARAMETERS = {
    'ambient_temperature': 40.0,  # °C
    'conductor_temperature_limit': 75.0,  # °C
    'altitude': 0.0,  # m
    'wind_speed': 0.61,  # m/s
    'solar_radiation': 1000.0,  # W/m²
    'emissivity': 0.8,
    'absorptivity': 0.8,
    'angle_of_sun': 90.0,  # grados
}

# Tipos de conductores disponibles
CONDUCTOR_TYPES = {
    'AAC': 'Aluminum Conductor Alloy Reinforced',
    'AAAC': 'All Aluminum Alloy Conductor', 
    'ACSR': 'Aluminum Conductor Steel Reinforced',
    'ACAR': 'Aluminum Conductor Alloy Reinforced',
    'CU': 'Copper Conductor'
}

# Unidades y conversiones
UNITS = {
    'diameter': 'mm',
    'area': 'mm²',
    'resistance': 'Ω/km',
    'temperature': '°C',
    'altitude': 'm',
    'wind_speed': 'm/s',
    'solar_radiation': 'W/m²',
    'current': 'A'
}
