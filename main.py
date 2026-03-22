"""
Calculadora de Ampacidad de Líneas de Transmisión
Basado en el estándar IEEE 738 para cálculo de ampacidad
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math

@dataclass
class LineParameters:
    """Parámetros de la línea de transmisión"""
    conductor_diameter: float  # mm
    conductor_resistance: float  # Ω/km a 20°C
    conductor_material: str  # 'ACSR', 'AAC', 'AAAC', 'CU'
    ambient_temperature: float  # °C
    wind_speed: float  # m/s
    solar_radiation: float  # W/m²
    emissivity: float  # adimensional
    absorption_coefficient: float  # adimensional
    max_conductor_temp: float  # °C
    
@dataclass
class EnvironmentalConditions:
    """Condiciones ambientales"""
    ambient_temp: float  # °C
    wind_speed: float  # m/s
    wind_angle: float  # grados
    solar_radiation: float  # W/m²
    altitude: float  # m
    atmospheric_pressure: float  # kPa

class AmpacityCalculator:
    """Calculador de ampacidad basado en IEEE 738"""
    
    def __init__(self):
        self.stefan_boltzmann = 5.67e-8  # W/(m²·K⁴)
        
    def calculate_air_density(self, altitude: float, temp_celsius: float) -> float:
        """Calcular densidad del aire basada en altitud y temperatura"""
        # Simplificación: densidad del aire a nivel del mar a 20°C = 1.204 kg/m³
        # Factor de corrección por altitud
        sea_level_density = 1.204  # kg/m³
        altitude_factor = math.exp(-altitude / 8000)  # Aproximación exponencial
        temp_factor = 293.15 / (temp_celsius + 273.15)  # Corrección por temperatura
        
        return sea_level_density * altitude_factor * temp_factor
    
    def calculate_heat_convection(self, temp_diff: float, wind_speed: float, 
                                 conductor_diameter: float, air_density: float) -> float:
        """Calcular pérdida de calor por convección (W/m)"""
        # Convección forzada y natural combinada
        if wind_speed > 0.1:
            # Convección forzada
            Re = air_density * wind_speed * conductor_diameter / 1.8e-5  # Número de Reynolds
            Nu = 0.65 + 0.35 * Re**0.52  # Número de Nusselt
        else:
            # Convección natural
            Gr = 9.81 * temp_diff * (conductor_diameter/1000)**3 / ((temp_diff + 273.15) * (1.8e-5/air_density)**2)
            Nu = 0.48 * Gr**0.25
        
        k_air = 0.024  # Conductividad térmica del aire W/(m·K)
        h_conv = Nu * k_air / (conductor_diameter / 1000)  # Coeficiente de convección
        
        return h_conv * math.pi * (conductor_diameter / 1000) * temp_diff
    
    def calculate_heat_radiation(self, conductor_temp: float, ambient_temp: float, 
                               emissivity: float, conductor_diameter: float) -> float:
        """Calcular pérdida de calor por radiación (W/m)"""
        T_conductor = conductor_temp + 273.15
        T_ambient = ambient_temp + 273.15
        
        q_rad = self.stefan_boltzmann * emissivity * math.pi * (conductor_diameter / 1000) * \
                (T_conductor**4 - T_ambient**4)
        
        return q_rad
    
    def calculate_solar_heat_gain(self, solar_radiation: float, absorption_coefficient, 
                                conductor_diameter: float) -> float:
        """Calcular ganancia de calor solar (W/m)"""
        return solar_radiation * absorption_coefficient * conductor_diameter / 1000
    
    def calculate_resistance_at_temperature(self, resistance_20c: float, temp: float, 
                                          material: str) -> float:
        """Calcular resistencia a temperatura dada"""
        # Coeficientes de temperatura de resistencia (1/°C)
        temp_coefficients = {
            'ACSR': 0.00393,  # Aluminio
            'AAC': 0.00393,
            'AAAC': 0.00393,
            'CU': 0.00393     # Cobre (similar para simplificación)
        }
        
        alpha = temp_coefficients.get(material, 0.00393)
        return resistance_20c * (1 + alpha * (temp - 20))
    
    def calculate_ampacity(self, line_params: LineParameters, 
                          env_conditions: EnvironmentalConditions) -> float:
        """Calcular ampacidad máxima del conductor"""
        # Temperatura del conductor permitida
        max_temp = line_params.max_conductor_temp
        ambient_temp = env_conditions.ambient_temp
        
        # Calcular pérdidas de calor
        temp_diff = max_temp - ambient_temp
        air_density = self.calculate_air_density(env_conditions.altitude, ambient_temp)
        
        q_conv = self.calculate_heat_convection(
            temp_diff, env_conditions.wind_speed, 
            line_params.conductor_diameter, air_density
        )
        
        q_rad = self.calculate_heat_radiation(
            max_temp, ambient_temp, line_params.emissivity, 
            line_params.conductor_diameter
        )
        
        # Calcular ganancia de calor solar
        q_solar = self.calculate_solar_heat_gain(
            env_conditions.solar_radiation, line_params.absorption_coefficient,
            line_params.conductor_diameter
        )
        
        # Calcular resistencia a temperatura máxima
        resistance = self.calculate_resistance_at_temperature(
            line_params.conductor_resistance, max_temp, line_params.conductor_material
        )
        
        # Balance de calor: I²R = q_conv + q_rad - q_solar
        heat_loss = q_conv + q_rad - q_solar
        
        if heat_loss <= 0:
            return 0  # No hay disipación de calor posible
        
        # Calcular corriente máxima (Ampacidad)
        ampacity = math.sqrt(heat_loss / resistance)
        
        return ampacity

def create_streamlit_app():
    """Crear interfaz de usuario con Streamlit"""
    
    st.set_page_config(
        page_title="Calculadora de Ampacidad",
        page_icon="⚡",
        layout="wide"
    )
    
    st.title("⚡ Calculadora de Ampacidad de Líneas de Transmisión")
    st.markdown("Basado en el estándar IEEE 738 para cálculo de ampacidad")
    
    # Sidebar para parámetros de entrada
    st.sidebar.header("Parámetros del Conductor")
    
    # Material del conductor
    conductor_material = st.sidebar.selectbox(
        "Material del Conductor",
        ["ACSR", "AAC", "AAAC", "CU"],
        help="ACSR: Aluminum Conductor Steel Reinforced"
    )
    
    # Diámetro del conductor
    conductor_diameter = st.sidebar.number_input(
        "Diámetro del Conductor (mm)",
        min_value=10.0,
        max_value=50.0,
        value=28.6,
        step=0.1
    )
    
    # Resistencia del conductor
    conductor_resistance = st.sidebar.number_input(
        "Resistencia (Ω/km a 20°C)",
        min_value=0.01,
        max_value=1.0,
        value=0.09,
        step=0.01
    )
    
    # Temperatura máxima del conductor
    max_conductor_temp = st.sidebar.number_input(
        "Temperatura Máxima del Conductor (°C)",
        min_value=50.0,
        max_value=100.0,
        value=75.0,
        step=1.0
    )
    
    # Propiedades térmicas
    emissivity = st.sidebar.slider(
        "Emisividad",
        min_value=0.2,
        max_value=1.0,
        value=0.5,
        step=0.05
    )
    
    absorption_coefficient = st.sidebar.slider(
        "Coeficiente de Absorción Solar",
        min_value=0.2,
        max_value=1.0,
        value=0.5,
        step=0.05
    )
    
    st.sidebar.header("Condiciones Ambientales")
    
    ambient_temp = st.sidebar.number_input(
        "Temperatura Ambiente (°C)",
        min_value=-20.0,
        max_value=50.0,
        value=25.0,
        step=1.0
    )
    
    wind_speed = st.sidebar.number_input(
        "Velocidad del Viento (m/s)",
        min_value=0.0,
        max_value=20.0,
        value=1.0,
        step=0.1
    )
    
    solar_radiation = st.sidebar.number_input(
        "Radiación Solar (W/m²)",
        min_value=0.0,
        max_value=1000.0,
        value=900.0,
        step=10.0
    )
    
    altitude = st.sidebar.number_input(
        "Altitud (m)",
        min_value=0,
        max_value=3000,
        value=0,
        step=100
    )
    
    # Botón de cálculo
    if st.sidebar.button("Calcular Ampacidad", type="primary"):
        
        # Crear objetos de parámetros
        line_params = LineParameters(
            conductor_diameter=conductor_diameter,
            conductor_resistance=conductor_resistance,
            conductor_material=conductor_material,
            ambient_temperature=ambient_temp,
            wind_speed=wind_speed,
            solar_radiation=solar_radiation,
            emissivity=emissivity,
            absorption_coefficient=absorption_coefficient,
            max_conductor_temp=max_conductor_temp
        )
        
        env_conditions = EnvironmentalConditions(
            ambient_temp=ambient_temp,
            wind_speed=wind_speed,
            wind_angle=90,  # Perpendicular al conductor
            solar_radiation=solar_radiation,
            altitude=altitude,
            atmospheric_pressure=101.3  # kPa
        )
        
        # Calcular ampacidad
        calculator = AmpacityCalculator()
        ampacity = calculator.calculate_ampacity(line_params, env_conditions)
        
        # Mostrar resultados
        st.header("📊 Resultados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Ampacidad Máxima",
                f"{ampacity:.1f} A",
                delta=None
            )
        
        with col2:
            # Calcular potencia para voltaje típico de transmisión
            voltage = 230  # kV (típico)
            power = ampacity * voltage * math.sqrt(3) / 1000  # MW
            st.metric(
                "Potencia Máxima",
                f"{power:.1f} MW",
                delta=None
            )
        
        with col3:
            # Margen de seguridad (asumiendo carga actual del 70%)
            current_load = ampacity * 0.7
            margin = (ampacity - current_load) / ampacity * 100
            st.metric(
                "Margen de Seguridad",
                f"{margin:.1f}%",
                delta=None
            )
        
        # Análisis detallado
        st.header("🔍 Análisis Detallado")
        
        # Calcular componentes del balance térmico
        temp_diff = max_conductor_temp - ambient_temp
        air_density = calculator.calculate_air_density(altitude, ambient_temp)
        
        q_conv = calculator.calculate_heat_convection(
            temp_diff, wind_speed, conductor_diameter, air_density
        )
        
        q_rad = calculator.calculate_heat_radiation(
            max_conductor_temp, ambient_temp, emissivity, conductor_diameter
        )
        
        q_solar = calculator.calculate_solar_heat_gain(
            solar_radiation, absorption_coefficient, conductor_diameter
        )
        
        resistance = calculator.calculate_resistance_at_temperature(
            conductor_resistance, max_conductor_temp, conductor_material
        )
        
        heat_loss = q_conv + q_rad - q_solar
        
        # Tabla de balance térmico
        balance_data = {
            "Componente": ["Pérdida por Convección", "Pérdida por Radiación", 
                          "Ganancia Solar", "Pérdida Total Neta"],
            "Valor (W/m)": [f"{q_conv:.2f}", f"{q_rad:.2f}", f"{q_solar:.2f}", f"{heat_loss:.2f}"]
        }
        
        balance_df = pd.DataFrame(balance_data)
        st.table(balance_df)
        
        # Gráfico de sensibilidad
        st.header("📈 Análisis de Sensibilidad")
        
        # Sensibilidad a temperatura ambiente
        temp_range = np.linspace(10, 40, 10)
        ampacity_vs_temp = []
        
        for temp in temp_range:
            env_temp = EnvironmentalConditions(
                ambient_temp=temp,
                wind_speed=wind_speed,
                wind_angle=90,
                solar_radiation=solar_radiation,
                altitude=altitude,
                atmospheric_pressure=101.3
            )
            amp = calculator.calculate_ampacity(line_params, env_temp)
            ampacity_vs_temp.append(amp)
        
        fig_temp = px.line(
            x=temp_range, y=ampacity_vs_temp,
            title="Ampacidad vs Temperatura Ambiente",
            labels={"x": "Temperatura Ambiente (°C)", "y": "Ampacidad (A)"}
        )
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Sensibilidad a velocidad del viento
        wind_range = np.linspace(0, 10, 11)
        ampacity_vs_wind = []
        
        for wind in wind_range:
            env_wind = EnvironmentalConditions(
                ambient_temp=ambient_temp,
                wind_speed=wind,
                wind_angle=90,
                solar_radiation=solar_radiation,
                altitude=altitude,
                atmospheric_pressure=101.3
            )
            amp = calculator.calculate_ampacity(line_params, env_wind)
            ampacity_vs_wind.append(amp)
        
        fig_wind = px.line(
            x=wind_range, y=ampacity_vs_wind,
            title="Ampacidad vs Velocidad del Viento",
            labels={"x": "Velocidad del Viento (m/s)", "y": "Ampacidad (A)"}
        )
        st.plotly_chart(fig_wind, use_container_width=True)

if __name__ == "__main__":
    create_streamlit_app()
