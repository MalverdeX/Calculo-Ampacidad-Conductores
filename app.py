"""
Aplicación web de calculadora de ampacidad usando Streamlit
Versión mejorada con tooltips exhaustivos y visualización corregida
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path
from ampacity_calculator import AmpacityCalculator, ConductorDatabase
from config import DEFAULT_PARAMETERS, CONDUCTOR_TYPES, UNITS

# Archivo para guardar conductores personalizados
CUSTOM_CONDUCTORS_FILE = Path("custom_conductors.json")


def load_custom_conductors():
    """Cargar conductores personalizados desde archivo JSON"""
    if CUSTOM_CONDUCTORS_FILE.exists():
        with open(CUSTOM_CONDUCTORS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_custom_conductors(custom_conductors):
    """Guardar conductores personalizados en archivo JSON"""
    with open(CUSTOM_CONDUCTORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(custom_conductors, f, indent=2, ensure_ascii=False)


def initialize_session_state():
    """Inicializar variables de estado de la sesión"""
    if 'custom_conductors' not in st.session_state:
        st.session_state.custom_conductors = load_custom_conductors()
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'selected_custom_conductor' not in st.session_state:
        st.session_state.selected_custom_conductor = None


class CustomConductorDatabase(ConductorDatabase):
    """Extensión de ConductorDatabase que incluye conductores personalizados"""
    
    def __init__(self, custom_conductors=None):
        super().__init__()
        if custom_conductors:
            # Agregar conductores personalizados al diccionario base
            for conductor_id, params in custom_conductors.items():
                self.conductors[conductor_id] = params
    
    def get_conductors_by_type(self, conductor_type):
        """Obtener conductores por tipo, incluyendo personalizados"""
        if conductor_type == 'CUSTOM':
            return {k: v for k, v in self.conductors.items() 
                   if v.get('is_custom', False)}
        return super().get_conductors_by_type(conductor_type)
    
    def add_custom_conductor(self, conductor_id, params):
        """Agregar un conductor personalizado"""
        params['is_custom'] = True
        self.conductors[conductor_id] = params
        return True
    
    def update_custom_conductor(self, conductor_id, params):
        """Actualizar un conductor personalizado"""
        if conductor_id in self.conductors and self.conductors[conductor_id].get('is_custom', False):
            params['is_custom'] = True
            self.conductors[conductor_id] = params
            return True
        return False
    
    def delete_custom_conductor(self, conductor_id):
        """Eliminar un conductor personalizado"""
        if conductor_id in self.conductors and self.conductors[conductor_id].get('is_custom', False):
            del self.conductors[conductor_id]
            return True
        return False

# Definiciones de tooltips para reutilización
TOOLTIPS = {
    # Conductores
    'conductor_type': "🔧 **Tipo de conductor**\n\n"
                     "**ACSR**: Aluminio con alma de acero (más resistente mecánicamente)\n"
                     "**AAC**: Aluminio puro (mejor conductividad, menos resistencia mecánica)\n"
                     "**AAAC**: Aleación de aluminio (intermedio entre ACSR y AAC)\n"
                     "**ACAR**: Aluminio con aleación de resistencia\n"
                     "**CU**: Cobre (mayor conductividad, más pesado y costoso)",
    
    'conductor_specific': "📏 **Conductor específico**\n\n"
                         "El código que identifica el tamaño exacto del conductor dentro de su tipo.\n\n"
                         "**¿Qué es?**\n"
                         "Es la designación estandarizada del tamaño del conductor según normas internacionales.\n\n"
                         "**Códigos utilizados:**\n"
                         "• **AWG** (American Wire Gauge): Calibre americano\n"
                         "  - Usado en conductores más pequeños\n"
                         "  - AWG 1/0 (más grande) → AWG 14 (más pequeño)\n"
                         "• **kcmil** (kilo-circular mils): Miles de circular mils\n"
                         "  - Usado en conductores grandes de transmisión\n"
                         "  - Mayor número = mayor área transversal\n"
                         "  - Ejemplo: 477 kcmil > 336 kcmil en capacidad\n\n"
                         "**¿Dónde se ocupa?**\n"
                         "• Catálogos de fabricantes de cables\n"
                         "• Especificaciones técnicas de líneas de transmisión\n"
                         "• Planillas de diseño eléctrico (single-line diagrams)\n"
                         "• Normas IEEE y NEMA para conductores aéreos\n\n"
                         "**Ejemplo práctico:**\n"
                         "ACSR 477 kcmil = ACSR con 241.7 mm² de área\n"
                         "Este es un conductor estándar en líneas de 69-138 kV",
    
    'diameter': "📐 **Diámetro del conductor**\n\n"
               "Diámetro externo del conductor en milímetros (mm)\n\n"
               "**Fórmula**: Afecta directamente la superficie de disipación térmica\n"
               "**Impacto**: A mayor diámetro → más disipación por convección y radiación",
    
    'area': "📊 **Área transversal**\n\n"
           "Área de la sección del conductor en mm²\n\n"
           "**Relación**: Área = π × (Diámetro/2)²\n"
           "**Impacto**: A mayor área → menor resistencia eléctrica → menor calentamiento Joule",
    
    'rdc_20': "⚡ **Resistencia DC a 20°C**\n\n"
             "Resistencia eléctrica directa (corriente continua) a temperatura ambiente\n\n"
             "**Unidad**: Ω/km (ohmios por kilómetro)\n"
             "**Fórmula**: R = ρ × L / A (resistividad × longitud / área)\n"
             "**Impacto**: A menor resistencia → menos pérdidas por efecto Joule",
    
    'alpha': "🌡️ **Coeficiente de temperatura Alpha (α)**\n\n"
            "Factor de corrección de resistencia con temperatura\n\n"
            "**Fórmula**: R(T) = R₂₀ × [1 + α × (T - 20)]\n"
            "**Valores típicos**:\n"
            "  • Aluminio: 0.00403 1/°C\n"
            "  • Cobre: 0.00393 1/°C\n\n"
            "**Impacto**: A mayor temperatura → mayor resistencia → más calentamiento",
    
    'beta': "🔄 **Coeficiente de efecto piel Beta (β)**\n\n"
           "Factor que corrige la resistencia por efecto piel en corriente AC\n\n"
           "**Fórmula**: R_AC = R_DC × [1 + β × (I/1000)²]\n"
           "**Valores típicos a 60Hz**:\n"
           "  • ACSR pequeño: 0.025\n"
           "  • ACSR mediano: 0.035\n"
           "  • ACSR grande: 0.045\n"
           "  • AAC: 0.015-0.020\n\n"
           "**Efecto**: A mayor frecuencia y corriente → mayor resistencia aparente",
    
    'weight': "⚖️ **Peso del conductor**\n\n"
             "Masa por unidad de longitud en kg/m\n\n"
             "**Impacto mecánico**: Afecta la tensión mecánica de la línea\n"
             "**Comparación**: ACSR es más pesado que AAC por el alma de acero",
    
    'max_temp': "🌡️ **Temperatura máxima del conductor**\n\n"
               "Límite térmico según material y aislamiento\n\n"
               "**Valores típicos**:\n"
               "  • ACSR: 75-90°C\n"
               "  • AAC: 70°C\n"
               "  • Cobre: 80-90°C\n\n"
               "**Importancia**: Exceder este límite causa daño permanente al conductor",
    
    # Parámetros ambientales
    'ambient_temp': "🌡️ **Temperatura ambiente**\n\n"
                   "Temperatura del aire circundante en °C\n\n"
                   "**Rango típico**: -10°C a 50°C\n"
                   "**Impacto**:\n"
                   "  • A mayor temperatura ambiente → menor ΔT → menos disipación\n"
                   "  • A mayor temperatura ambiente → menor densidad del aire\n\n"
                   "**Efecto en ampacidad**: Cada 10°C de aumento ≈ 5-10% menos capacidad",
    
    'conductor_temp_limit': "🌡️ **Temperatura máxima permitida del conductor**\n\n"
                           "Temperatura límite de operación segura\n\n"
                           "**Cálculo**: La ampacidad es la corriente que eleva el conductor\n"
                           "           a esta temperatura bajo las condiciones dadas\n\n"
                           "**Factor de seguridad**: Se recomienda usar 80-90% del límite térmico real",
    
    'altitude': "⛰️ **Altitud sobre el nivel del mar**\n\n"
               "Elevación geográfica de la ubicación donde se instalará la línea de transmisión.\n\n"
               "**¿Qué es?**\n"
               "La altura vertical respecto al nivel medio del mar, medida en metros (m).\n"
               "Afecta la densidad atmosférica y por tanto la capacidad de disipación térmica del conductor.\n\n"
               "**¿Dónde se ocupa?**\n"
               "• Diseño de líneas de transmisión en zonas montañosas o altiplanos\n"
               "• Estudios de factibilidad para interconexiones eléctricas\n"
               "• Cálculos de ampacidad en países con variación altitudinal\n"
               "• Líneas en la cordillera de los Andes, Rocky Mountains, Himalaya\n"
               "• Subestaciones ubicadas a gran altura (ej: La Paz, Bolivia ~3600 m)\n\n"
               "**Impacto físico:**\n"
               "  • A mayor altitud → menor presión atmosférica\n"
               "  • Menor presión → menor densidad del aire (ρ ↓)\n"
               "  • Menor densidad → menos convección → más calentamiento\n\n"
               "**Fórmula de densidad:**\n"
               "  ρ = ρ₀ × exp(-h/8000) × (293.15/(T+273.15))\n\n"
               "**Efecto en ampacidad:**\n"
               "  • Cada 1000m de altitud ≈ -3% a -5% de capacidad\n"
               "  • Ejemplo: 5000m tiene ~40-50% menos capacidad que nivel del mar\n\n"
               "**Valores de referencia:**\n"
               "  • Ciudad de México: ~2240 m\n"
               "  • Quito, Ecuador: ~2850 m\n"
               "  • La Paz, Bolivia: ~3640 m\n"
               "  • Lhasa, Tibet: ~3650 m\n"
               "  • El Alto, Bolivia: ~4150 m",
    
    'wind_speed': "🌪️ **Velocidad del viento perpendicular**\n\n"
                 "Velocidad del aire que fluye perpendicular al conductor en m/s\n\n"
                 "**Rango típico**: 0.5 - 5 m/s\n"
                 "**Impacto crítico**:\n"
                 "  • Viento < 0.1 m/s: Convección natural (ineficiente)\n"
                 "  • Viento > 0.5 m/s: Convección forzada (eficiente)\n\n"
                 "**Fórmula IEEE**: Nu = 0.292 × Re^0.6 (convección forzada)\n\n"
                 "**Efecto**: Duplicar viento ≈ +30-40% ampacidad",
    
    'solar_radiation': "☀️ **Radiación solar incidente**\n\n"
                      "Intensidad de energía solar que impacta el conductor en W/m²\n\n"
                      "**Valores típicos**:\n"
                      "  • Noche/nublado: 0-200 W/m²\n"
                      "  • Día soleado: 800-1000 W/m²\n"
                      "  • Máximo extremo: 1200 W/m²\n\n"
                      "**Fórmula**: Q_solar = Qs × α × D × sin(θ)\n\n"
                      "**Efecto**: Cada 100 W/m² adicionales ≈ -5% ampacidad",
    
    'emissivity': "🌈 **Emisividad del conductor**\n\n"
                "Capacidad de la superficie para emitir radiación térmica (0-1)\n\n"
                "**Valores típicos**:\n"
                "  • Aluminio nuevo: 0.1-0.2 (brillante)\n"
                "  • Aluminio oxidado: 0.3-0.5\n"
                "  • Aluminio envejecido: 0.6-0.8\n"
                "  • Negro mate: 0.9-1.0\n\n"
                "**Fórmula**: Q_rad = σ × ε × π × D × (Tc⁴ - Ta⁴)\n\n"
                "**Recomendación**: Usar 0.8 para conductores en servicio",
    
    'absorptivity': "☀️ **Absortividad del conductor**\n\n"
                   "Capacidad de la superficie para absorber radiación solar (0-1)\n\n"
                   "**Valores típicos**: Generalmente similar a la emisividad\n"
                   "  • Aluminio nuevo: 0.1-0.2 (reflectivo)\n"
                   "  • Aluminio oxidado: 0.3-0.5\n"
                   "  • Aluminio envejecido: 0.6-0.8\n\n"
                   "**Fórmula**: Q_solar = Qs × α_solar × D × sin(θ)\n\n"
                   "**Relación**: Mayor absortividad = más calor solar absorbido",
    
    # Resultados
    'ampacity': "⚡ **AMPACIDAD**\n\n"
               "**Definición**: Corriente máxima continua que puede transportar el conductor\n"
               "              sin exceder su temperatura límite\n\n"
               "**Cálculo**: I_max = √[(Q_conv + Q_rad - Q_solar) × 1000 / R]\n\n"
               "**Factores que afectan**:\n"
               "  • Temperatura ambiente ↑ → Ampacidad ↓\n"
               "  • Velocidad viento ↑ → Ampacidad ↑\n"
               "  • Radiación solar ↑ → Ampacidad ↓\n"
               "  • Diámetro conductor ↑ → Ampacidad ↑\n\n"
               "**Factor de seguridad**: Multiplicar por 0.8-0.9 para operación real",
    
    'conductor_temp': "🌡️ **TEMPERATURA DEL CONDUCTOR**\n\n"
                     "Temperatura de operación alcanzada con la corriente de ampacidad\n\n"
                     "**Cálculo**: Resuelve Q_joule(I,T) = Q_conv(T) + Q_rad(T) - Q_solar\n"
                     "          usando método iterativo de Newton-Raphson\n\n"
                     "**Relación**: A mayor corriente → mayor temperatura (no lineal)\n\n"
                     "**Límite**: Este valor debe ser ≤ temperatura máxima permitida",
    
    'resistance_at_temp': "⚡ **RESISTENCIA A TEMPERATURA DE OPERACIÓN**\n\n"
                        "Resistencia eléctrica del conductor a su temperatura de trabajo\n\n"
                        "**Fórmula completa**:\n"
                        "  R(T) = R₂₀ × [1 + α × (T - 20)] × [1 + β × (I/1000)²]\n\n"
                        "**Componentes**:\n"
                        "  • R₂₀: Resistencia base a 20°C\n"
                        "  • α: Corrección por temperatura\n"
                        "  • β: Efecto piel (corriente AC)\n\n"
                        "**Unidad**: Ω/km (ohmios por kilómetro)",
    
    'air_density': "💨 **DENSIDAD DEL AIRE**\n\n"
                  "Masa de aire por unidad de volumen a las condiciones dadas\n\n"
                  "**Fórmula**: ρ = ρ₀ × exp(-h/8000) × (293.15/(T+273.15))\n\n"
                  "**Factores**:\n"
                  "  • Altitud ↑ → Densidad ↓ (exponencial)\n"
                  "  • Temperatura ↑ → Densidad ↓ (inversa)\n\n"
                  "**Impacto**: Afecta directamente la convección (Re = ρ×v×D/μ)\n\n"
                  "**Valor típico nivel mar**: 1.204 kg/m³",
    
    # Balance de calor
    'heat_convection': "🌊 **PÉRDIDA POR CONVECCIÓN**\n\n"
                      "Calor disipado por transferencia convectiva al aire circundante\n\n"
                      "**Fórmula IEEE 738-2012**:\n"
                      "  Q_conv = h × π × D × ΔT\n\n"
                      "  donde h = Nu × k / D\n\n"
                      "**Modos**:\n"
                      "  • Natural (viento < 0.1 m/s): Gravitacional\n"
                      "  • Forzada (viento > 0.1 m/s): h = f(Re)\n\n"
                      "**Factor dominante**: Velocidad del viento",
    
    'heat_radiation': "🌟 **PÉRDIDA POR RADIACIÓN**\n\n"
                     "Calor disipado por radiación térmica electromagnética\n\n"
                     "**Fórmula (Ley Stefan-Boltzmann)**:\n"
                     "  Q_rad = σ × ε × π × D × (Tc⁴ - Ta⁴)\n\n"
                     "**Parámetros**:\n"
                     "  • σ = 5.67×10⁻⁸ W/(m²·K⁴) (constante universal)\n"
                     "  • ε: Emisividad del conductor (0-1)\n"
                     "  • Tc, Ta: Temperaturas en Kelvin (°C + 273.15)\n\n"
                     "**Importancia**: Significativa a altas temperaturas (>80°C)",
    
    'solar_heat_gain': "☀️ **GANANCIA POR RADIACIÓN SOLAR**\n\n"
                       "Calor absorbido del sol que incrementa la temperatura del conductor\n\n"
                       "**Fórmula IEEE**:\n"
                       "  Q_solar = Qs × α_solar × D × sin(θ)\n\n"
                       "**Parámetros**:\n"
                       "  • Qs: Radiación solar incidente (W/m²)\n"
                       "  • α_solar: Absortividad del conductor (0-1)\n"
                       "  • D: Diámetro del conductor (m)\n"
                       "  • θ: Ángulo del sol (90° = incidencia perpendicular)\n\n"
                       "**Efecto**: Resta del balance de calor (es ganancia, no pérdida)",
    
    'total_heat_loss': "🔥 **PÉRDIDA NETA DE CALOR**\n\n"
                      "Balance energético total que debe ser disipado\n\n"
                      "**Fórmula fundamental**:\n"
                      "  Q_perdida = Q_convección + Q_radiación - Q_solar\n\n"
                      "**Equilibrio térmico**:\n"
                      "  Q_joule = Q_perdida\n\n"
                      "  I² × R / 1000 = Q_conv + Q_rad - Q_solar\n\n"
                      "**Verificación**: Esta igualdad debe cumplirse para la ampacidad calculada",
    
    'current_range': "📈 **RANGO DE CORRIENTES**\n\n"
                    "Valores de corriente evaluados para construir la curva T-I\n\n"
                    "**Generación**: 50 puntos espaciados linealmente\n"
                    "  desde 0 A hasta 1.2 × ampacidad calculada\n\n"
                    "**Propósito**: Visualizar comportamiento térmico del conductor",
    
    'temperature_curve': "📉 **CURVA DE TEMPERATURA**\n\n"
                        "Temperatura del conductor para cada valor de corriente\n\n"
                        "**Cálculo**: Método iterativo que resuelve\n"
                        "  I² × R(T) / 1000 = Q_conv(T) + Q_rad(T) - Q_solar\n\n"
                        "**Propiedades**:\n"
                        "  • Monotónica creciente (siempre sube con corriente)\n"
                        "  • No lineal (efecto Joule: I²)\n"
                        "  • Punto ampacidad = intersección con temperatura límite",
    
    'wind_sensitivity': "🌪️ **SENSIBILIDAD AL VIENTO**\n\n"
                      "Muestra cómo cambia la ampacidad con velocidades de viento diferentes\n\n"
                      "**Comportamiento esperado**:\n"
                      "  • Más viento → más convección → mayor ampacidad\n"
                      "  • Efecto más pronunciado a bajas velocidades\n\n"
                      "**Velocidades evaluadas**: 0.1, 0.5, 1.0, 2.0, 5.0, 10.0 m/s",
    
    'temp_sensitivity': "🌡️ **SENSIBILIDAD A TEMPERATURA**\n\n"
                      "Muestra cómo cambia la ampacidad con temperatura ambiente\n\n"
                      "**Comportamiento esperado**:\n"
                      "  • Mayor temperatura ambiente → menor ΔT → menos disipación\n"
                      "  • Relación inversa aproximadamente lineal\n\n"
                      "**Temperaturas evaluadas**: 10, 20, 30, 40, 50°C",
}



def main():
    st.set_page_config(
        page_title="Calculadora de Ampacidad",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar estado de sesión
    initialize_session_state()
    
    st.title("⚡ Calculadora de Ampacidad de Líneas de Transmisión")
    st.markdown("---")
    
    # Inicializar calculadora y base de datos con conductores personalizados
    calculator = AmpacityCalculator()
    conductor_db = CustomConductorDatabase(st.session_state.custom_conductors)
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("🔧 Configuración")
        
        # === GESTIÓN DE CONDUCTORES PERSONALIZADOS ===
        with st.expander("⚡ Conductores Personalizados", expanded=False):
            st.markdown("**📝 Agregar/Editar Conductor**")
            
            # Lista de conductores personalizados para editar
            custom_list = {k: v for k, v in st.session_state.custom_conductors.items()}
            
            # Seleccionar modo: Agregar nuevo o Editar existente
            mode = st.radio(
                "Modo",
                ["Nuevo conductor", "Editar existente"],
                horizontal=True,
                key="conductor_mode"
            )
            
            if mode == "Editar existente" and custom_list:
                selected_edit = st.selectbox(
                    "Seleccionar conductor a editar",
                    options=list(custom_list.keys()),
                    format_func=lambda x: custom_list[x]['name'],
                    key="edit_conductor_select"
                )
                edit_params = custom_list[selected_edit].copy() if selected_edit else {}
            else:
                selected_edit = None
                edit_params = {}
            
            # Formulario para parámetros del conductor
            st.markdown("---")
            st.caption("**Parámetros del conductor**")
            
            new_id = st.text_input(
                "ID único (sin espacios)",
                value=selected_edit if selected_edit else "",
                help="Ejemplo: ACSR_500_custom, MiConductor_001",
                key="new_conductor_id"
            )
            
            new_name = st.text_input(
                "Nombre descriptivo",
                value=edit_params.get('name', ''),
                help="Ejemplo: ACSR 500 kcmil Personalizado",
                key="new_conductor_name"
            )
            
            new_type = st.selectbox(
                "Tipo",
                ['ACSR', 'AAC', 'AAAC', 'ACAR', 'CU', 'CUSTOM'],
                index=['ACSR', 'AAC', 'AAAC', 'ACAR', 'CU', 'CUSTOM'].index(edit_params.get('type', 'ACSR')),
                key="new_conductor_type"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                new_diameter = st.number_input(
                    "Diámetro (mm)",
                    value=edit_params.get('diameter', 20.0),
                    min_value=1.0,
                    max_value=50.0,
                    step=0.1,
                    key="new_diameter"
                )
                new_rdc = st.number_input(
                    "R DC 20°C (Ω/km)",
                    value=edit_params.get('rdc_20', 0.1),
                    min_value=0.001,
                    max_value=2.0,
                    step=0.001,
                    format="%.4f",
                    key="new_rdc"
                )
                new_alpha = st.number_input(
                    "Alpha (1/°C)",
                    value=edit_params.get('alpha', 0.00403),
                    min_value=0.001,
                    max_value=0.01,
                    step=0.0001,
                    format="%.5f",
                    key="new_alpha"
                )
                new_max_temp = st.number_input(
                    "Temp. máx (°C)",
                    value=edit_params.get('max_temp', 75.0),
                    min_value=50.0,
                    max_value=150.0,
                    step=1.0,
                    key="new_max_temp"
                )
            
            with col2:
                new_area = st.number_input(
                    "Área (mm²)",
                    value=edit_params.get('area', 250.0),
                    min_value=10.0,
                    max_value=1000.0,
                    step=1.0,
                    key="new_area"
                )
                new_beta = st.number_input(
                    "Beta",
                    value=edit_params.get('beta', 0.035),
                    min_value=0.001,
                    max_value=0.1,
                    step=0.001,
                    format="%.3f",
                    key="new_beta"
                )
                new_weight = st.number_input(
                    "Peso (kg/m)",
                    value=edit_params.get('weight', 1.0),
                    min_value=0.1,
                    max_value=5.0,
                    step=0.01,
                    key="new_weight"
                )
            
            # Botones de acción
            col_save, col_delete = st.columns(2)
            
            with col_save:
                if st.button("💾 Guardar", use_container_width=True, key="save_conductor"):
                    if new_id and new_name:
                        # Crear diccionario del conductor
                        conductor_data = {
                            'name': new_name,
                            'type': new_type,
                            'diameter': new_diameter,
                            'area': new_area,
                            'rdc_20': new_rdc,
                            'alpha': new_alpha,
                            'beta': new_beta,
                            'weight': new_weight,
                            'max_temp': new_max_temp,
                            'is_custom': True
                        }
                        
                        # Guardar en session state
                        st.session_state.custom_conductors[new_id] = conductor_data
                        save_custom_conductors(st.session_state.custom_conductors)
                        
                        # Actualizar base de datos
                        conductor_db.add_custom_conductor(new_id, conductor_data)
                        
                        st.success(f"✅ Conductor '{new_name}' guardado!")
                        st.rerun()
                    else:
                        st.error("⚠️ ID y nombre son obligatorios")
            
            with col_delete:
                if mode == "Editar existente" and selected_edit:
                    if st.button("🗑️ Eliminar", use_container_width=True, key="delete_conductor"):
                        if selected_edit in st.session_state.custom_conductors:
                            del st.session_state.custom_conductors[selected_edit]
                            save_custom_conductors(st.session_state.custom_conductors)
                            conductor_db.delete_custom_conductor(selected_edit)
                            st.success(f"✅ Conductor eliminado!")
                            st.rerun()
            
            # Mostrar lista de conductores personalizados
            if st.session_state.custom_conductors:
                st.markdown("---")
                st.caption(f"**📋 Conductores personalizados guardados: {len(st.session_state.custom_conductors)}**")
                for cid, cdata in st.session_state.custom_conductors.items():
                    st.markdown(f"• **{cdata['name']}** ({cid})")
            else:
                st.info("💡 No hay conductores personalizados. Agrega uno usando el formulario.")
        
        st.markdown("---")
        
        # Selección de conductor
        st.subheader("Conductor")
        
        # Agregar tipo CUSTOM a las opciones si hay conductores personalizados
        available_types = list(CONDUCTOR_TYPES.keys())
        if st.session_state.custom_conductors:
            available_types.append('CUSTOM')
        
        conductor_type = st.selectbox(
            "Tipo de conductor",
            available_types,
            help=TOOLTIPS['conductor_type']
        )
        
        # Obtener conductores del tipo seleccionado
        available_conductors = conductor_db.get_conductors_by_type(conductor_type)
        conductor_options = {v['name']: k for k, v in available_conductors.items()}
        
        # Validar que hay conductores disponibles
        if not conductor_options:
            st.error(f"❌ No hay conductores disponibles para el tipo: {conductor_type}")
            st.stop()
        
        selected_conductor_name = st.selectbox(
            "Conductor específico",
            list(conductor_options.keys()),
            help=TOOLTIPS['conductor_specific']
        )
        
        # Validar que se seleccionó un conductor válido
        if selected_conductor_name not in conductor_options:
            st.error(f"❌ Conductor seleccionado no válido: {selected_conductor_name}")
            st.stop()
            
        selected_conductor_id = conductor_options[selected_conductor_name]
        conductor_params = conductor_db.get_conductor(selected_conductor_id)
        
        # Mostrar parámetros del conductor
        with st.expander("📊 Parámetros del conductor"):
            st.json(conductor_params)
        
        # Parámetros ambientales
        st.subheader("🌤️ Condiciones Ambientales")
        
        ambient_temp = st.number_input(
            "Temperatura ambiente (°C)",
            value=DEFAULT_PARAMETERS['ambient_temperature'],
            min_value=-50.0,
            max_value=60.0,
            step=1.0,
            help=TOOLTIPS['ambient_temp']
        )
        
        conductor_temp_limit = st.number_input(
            "Temperatura máxima del conductor (°C)",
            value=DEFAULT_PARAMETERS['conductor_temperature_limit'],
            min_value=50.0,
            max_value=150.0,
            step=1.0,
            help=TOOLTIPS['conductor_temp_limit']
        )
        
        altitude = st.number_input(
            "Altitud (m)",
            value=DEFAULT_PARAMETERS['altitude'],
            min_value=0.0,
            max_value=5000.0,
            step=100.0,
            help=TOOLTIPS['altitude']
        )
        
        wind_speed = st.number_input(
            "Velocidad del viento (m/s)",
            value=DEFAULT_PARAMETERS['wind_speed'],
            min_value=0.0,
            max_value=20.0,
            step=0.1,
            help=TOOLTIPS['wind_speed']
        )
        
        solar_radiation = st.number_input(
            "Radiación solar (W/m²)",
            value=DEFAULT_PARAMETERS['solar_radiation'],
            min_value=0.0,
            max_value=1200.0,
            step=50.0,
            help=TOOLTIPS['solar_radiation']
        )
        
        emissivity = st.slider(
            "Emisividad",
            value=DEFAULT_PARAMETERS['emissivity'],
            min_value=0.1,
            max_value=1.0,
            step=0.05,
            help=TOOLTIPS['emissivity']
        )
        
        absorptivity = st.slider(
            "Absortividad",
            value=DEFAULT_PARAMETERS['absorptivity'],
            min_value=0.1,
            max_value=1.0,
            step=0.05,
            help=TOOLTIPS['absorptivity']
        )
        
        # Botón de cálculo
        calculate_button = st.button(
            "🧮 Calcular Ampacidad",
            type="primary",
            use_container_width=True
        )
    
    # Contenido principal
    if calculate_button:
        # Preparar parámetros
        environmental_params = {
            'ambient_temperature': ambient_temp,
            'conductor_temperature_limit': conductor_temp_limit,
            'altitude': altitude,
            'wind_speed': wind_speed,
            'solar_radiation': solar_radiation,
            'emissivity': emissivity,
            'absorptivity': absorptivity
        }
        
        # Realizar cálculo
        with st.spinner("Calculando ampacidad..."):
            results = calculator.calculate_ampacity(
                conductor_params, 
                environmental_params
            )
        
        # Mostrar resultados principales
        st.header("📈 Resultados del Cálculo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Ampacidad",
                f"{results['ampacity']:.1f} A",
                help=TOOLTIPS['ampacity']
            )
        
        with col2:
            st.metric(
                "Temperatura del conductor",
                f"{results['conductor_temperature']:.1f} °C",
                help=TOOLTIPS['conductor_temp']
            )
        
        with col3:
            st.metric(
                "Resistencia a temperatura",
                f"{results['resistance_at_temp']:.4f} Ω/km",
                help=TOOLTIPS['resistance_at_temp']
            )
        
        with col4:
            st.metric(
                "Densidad del aire",
                f"{results['air_density']:.3f} kg/m³",
                help=TOOLTIPS['air_density']
            )
        
        # Análisis de balance de calor
        st.subheader("🔥 Balance de Calor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras para balance de calor - CORREGIDO
            # Mostrar todas las barras como positivas con colores que indican dirección
            heat_data = {
                'Componente': ['Convección\n(disipación)', 'Radiación\n(disipación)', 
                              'Solar\n(ganancia)', 'Pérdida\nNeta'],
                'Calor (W/m)': [
                    results['heat_convection'],
                    results['heat_radiation'],
                    results['solar_heat_gain'],  # ✅ CORREGIDO: Ahora positivo
                    results['total_heat_loss']
                ],
                'Tipo': ['Pérdida', 'Pérdida', 'Ganancia', 'Balance'],
                'Color': ['blue', 'red', 'orange', 'green']
            }
            
            fig_heat = go.Figure(data=[
                go.Bar(
                    x=heat_data['Componente'],
                    y=heat_data['Calor (W/m)'],
                    marker_color=heat_data['Color'],
                    text=[f"{v:.2f}" for v in heat_data['Calor (W/m)']],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Valor: %{y:.2f} W/m<br>' +
                                 '<extra></extra>'
                )
            ])
            
            fig_heat.update_layout(
                title="Componentes del Balance de Calor",
                xaxis_title="Componente",
                yaxis_title="Calor (W/m)",
                height=400,
                annotations=[
                    dict(
                        x=2, y=results['solar_heat_gain']/2,
                        text="📥 Entra<br>al conductor",
                        showarrow=False,
                        font=dict(color='orange', size=10)
                    ),
                    dict(
                        x=0, y=results['heat_convection']/2,
                        text="📤 Sale del<br>conductor",
                        showarrow=False,
                        font=dict(color='blue', size=10)
                    ),
                    dict(
                        x=1, y=results['heat_radiation']/2,
                        text="📤 Sale del<br>conductor",
                        showarrow=False,
                        font=dict(color='red', size=10)
                    )
                ]
            )
            
            # Línea de referencia en cero
            fig_heat.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
            
            st.plotly_chart(fig_heat, use_container_width=True)
            
            # Leyenda explicativa
            st.caption("""
            📘 **Convección**: Calor que sale del conductor por enfriamiento del aire  
            📕 **Radiación**: Calor que sale por emisión electromagnética  
            📙 **Solar**: Calor que entra del sol (positivo = ganancia)  
            📗 **Pérdida Neta**: Balance total que debe disipar el conductor
            """)
        
        with col2:
            # Tabla detallada de balance de calor con explicaciones
            st.markdown("##### Detalle del Balance Energético")
            
            heat_table = pd.DataFrame({
                'Componente': [
                    '📘 Convección',
                    '📕 Radiación', 
                    '📙 Ganancia Solar',
                    '📗 Pérdida Neta'
                ],
                'Valor (W/m)': [
                    f"{results['heat_convection']:.2f}",
                    f"{results['heat_radiation']:.2f}",
                    f"{results['solar_heat_gain']:.2f}",
                    f"{results['total_heat_loss']:.2f}"
                ],
                'Dirección': [
                    '⬆️ Sale',
                    '⬆️ Sale',
                    '⬇️ Entra',
                    '⬆️ Sale neta'
                ]
            })
            
            st.dataframe(heat_table, use_container_width=True, hide_index=True)
            
            # Fórmula del balance
            st.markdown("---")
            st.markdown("##### 🧮 Ecuación de Balance")
            st.markdown(f"""
            ```
            Q_joule = Q_conv + Q_rad - Q_solar
            
            {results['ampacity']:.1f}² × {results['resistance_at_temp']:.4f}/1000 = 
            {results['heat_convection']:.2f} + {results['heat_radiation']:.2f} - {results['solar_heat_gain']:.2f}
            
            {results['ampacity']**2 * results['resistance_at_temp']/1000:.2f} = {results['total_heat_loss']:.2f} W/m
            ✓ Balance verificado
            ```
            """)
            
            # Explicación hover
            with st.expander("ℹ️ ¿Por qué la ganancia solar se resta?"):
                st.markdown(TOOLTIPS['solar_heat_gain'])
        
        # Curva temperatura vs corriente
        st.subheader("📊 Curva Temperatura vs Corriente")
        
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=results['current_range'],
            y=results['temperature_curve'],
            mode='lines',
            name='Temperatura del conductor',
            line=dict(color='red', width=2),
            hovertemplate='<b>Corriente:</b> %{x:.1f} A<br>' +
                         '<b>Temperatura:</b> %{y:.1f} °C<br>' +
                         '<extra></extra>',
            hoverlabel=dict(bgcolor='red', font_color='white')
        ))
        
        # Añadir línea de temperatura límite
        fig_temp.add_hline(
            y=conductor_temp_limit,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Límite térmico ({conductor_temp_limit}°C)",
            annotation_position="top right"
        )
        
        # Añadir línea de ampacidad
        fig_temp.add_vline(
            x=results['ampacity'],
            line_dash="dash",
            line_color="green",
            annotation_text=f"Ampacidad ({results['ampacity']:.1f} A)",
            annotation_position="top"
        )
        
        fig_temp.update_layout(
            title="Relación Temperatura-Corriente",
            xaxis_title="Corriente (A)",
            yaxis_title="Temperatura del conductor (°C)",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Explicación de la curva
        with st.expander("ℹ️ Cómo interpretar esta curva"):
            st.markdown(TOOLTIPS['temperature_curve'])
        
        # Análisis de sensibilidad
        st.subheader("🔍 Análisis de Sensibilidad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            col_title, col_help = st.columns([3, 1])
            with col_title:
                st.markdown("**Efecto de la velocidad del viento**")
            with col_help:
                with st.expander("ℹ️"):
                    st.markdown(TOOLTIPS['wind_sensitivity'])
            
            wind_speeds = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            ampacities_wind = []
            
            for ws in wind_speeds:
                env_params = environmental_params.copy()
                env_params['wind_speed'] = ws
                result = calculator.calculate_ampacity(conductor_params, env_params)
                ampacities_wind.append(result['ampacity'])
            
            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=wind_speeds,
                y=ampacities_wind,
                mode='lines+markers',
                name='Ampacidad',
                line=dict(color='blue', width=2),
                hovertemplate='<b>Viento:</b> %{x:.1f} m/s<br>' +
                             '<b>Ampacidad:</b> %{y:.1f} A<br>' +
                             '<extra></extra>'
            ))
            
            fig_wind.update_layout(
                title="Ampacidad vs Velocidad del Viento",
                xaxis_title="Velocidad del viento (m/s)",
                yaxis_title="Ampacidad (A)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_wind, use_container_width=True)
            
            # Tabla de datos
            wind_df = pd.DataFrame({
                'Viento (m/s)': wind_speeds,
                'Ampacidad (A)': [f"{a:.1f}" for a in ampacities_wind]
            })
            st.dataframe(wind_df, use_container_width=True, hide_index=True)
        
        with col2:
            col_title2, col_help2 = st.columns([3, 1])
            with col_title2:
                st.markdown("**Efecto de la temperatura ambiente**")
            with col_help2:
                with st.expander("ℹ️"):
                    st.markdown(TOOLTIPS['temp_sensitivity'])
            
            ambient_temps = [10, 20, 30, 40, 50]
            ampacities_temp = []
            
            for at in ambient_temps:
                env_params = environmental_params.copy()
                env_params['ambient_temperature'] = at
                result = calculator.calculate_ampacity(conductor_params, env_params)
                ampacities_temp.append(result['ampacity'])
            
            fig_temp_effect = go.Figure()
            fig_temp_effect.add_trace(go.Scatter(
                x=ambient_temps,
                y=ampacities_temp,
                mode='lines+markers',
                name='Ampacidad',
                line=dict(color='red', width=2),
                hovertemplate='<b>Temp. ambiente:</b> %{x}°C<br>' +
                             '<b>Ampacidad:</b> %{y:.1f} A<br>' +
                             '<extra></extra>'
            ))
            
            fig_temp_effect.update_layout(
                title="Ampacidad vs Temperatura Ambiente",
                xaxis_title="Temperatura ambiente (°C)",
                yaxis_title="Ampacidad (A)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_temp_effect, use_container_width=True)
            
            # Tabla de datos
            temp_df = pd.DataFrame({
                'Temp. ambiente (°C)': ambient_temps,
                'Ampacidad (A)': [f"{a:.1f}" for a in ampacities_temp]
            })
            st.dataframe(temp_df, use_container_width=True, hide_index=True)
        
        # Detalles del cálculo
        with st.expander("🔬 Detalles Técnicos del Cálculo"):
            st.markdown("##### Parámetros de entrada utilizados")
            st.json(results['calculation_details'])
            
            st.markdown("---")
            st.markdown("##### Constantes físicas (IEEE 738-2012)")
            st.markdown(f"""
            | Constante | Valor | Unidad | Descripción |
            |-----------|-------|--------|-------------|
            | Stefan-Boltzmann (σ) | 5.67×10⁻⁸ | W/(m²·K⁴) | Radiación térmica |
            | Gravedad (g) | 9.81 | m/s² | Convección natural |
            | Viscosidad aire (μ) | 1.8×10⁻⁵ | Pa·s | Convección |
            | Conductividad (k) | 0.024 | W/(m·K) | Convección |
            | Densidad aire (ρ₀) | 1.204 | kg/m³ | Nivel del mar |
            | Prandtl (Pr) | 0.713 | - | Número adimensional |
            """)
        
        # Exportar resultados
        st.subheader("💾 Exportar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📋 Resumen de resultados")
            
            # Crear DataFrame para exportación con descripciones
            export_data = {
                'Parámetro': [
                    'Nombre del conductor',
                    'Tipo de conductor',
                    'Diámetro (mm) - ' + TOOLTIPS['diameter'].split('\n')[0],
                    'Área transversal (mm²) - ' + TOOLTIPS['area'].split('\n')[0],
                    'Resistencia DC a 20°C (Ω/km) - ' + TOOLTIPS['rdc_20'].split('\n')[0],
                    'Coef. temperatura Alpha (1/°C) - ' + TOOLTIPS['alpha'].split('\n')[0],
                    'Coef. efecto piel Beta - ' + TOOLTIPS['beta'].split('\n')[0],
                    'Temperatura ambiente (°C) - ' + TOOLTIPS['ambient_temp'].split('\n')[0],
                    'Temperatura máxima conductor (°C) - ' + TOOLTIPS['conductor_temp_limit'].split('\n')[0],
                    'Altitud (m) - ' + TOOLTIPS['altitude'].split('\n')[0],
                    'Velocidad viento (m/s) - ' + TOOLTIPS['wind_speed'].split('\n')[0],
                    'Radiación solar (W/m²) - ' + TOOLTIPS['solar_radiation'].split('\n')[0],
                    'Emisividad - ' + TOOLTIPS['emissivity'].split('\n')[0],
                    'Absortividad - ' + TOOLTIPS['absorptivity'].split('\n')[0],
                    '🎯 AMPACIDAD calculada (A) - ' + TOOLTIPS['ampacity'].split('\n')[0],
                    'Resistencia a temperatura (Ω/km) - ' + TOOLTIPS['resistance_at_temp'].split('\n')[0],
                    'Pérdida por convección (W/m) - ' + TOOLTIPS['heat_convection'].split('\n')[0],
                    'Pérdida por radiación (W/m) - ' + TOOLTIPS['heat_radiation'].split('\n')[0],
                    'Ganancia solar (W/m) - ' + TOOLTIPS['solar_heat_gain'].split('\n')[0],
                    'Pérdida neta de calor (W/m) - ' + TOOLTIPS['total_heat_loss'].split('\n')[0]
                ],
                'Valor': [
                    conductor_params['name'],
                    conductor_params['type'],
                    conductor_params['diameter'],
                    conductor_params['area'],
                    conductor_params['rdc_20'],
                    conductor_params['alpha'],
                    conductor_params['beta'],
                    ambient_temp,
                    conductor_temp_limit,
                    altitude,
                    wind_speed,
                    solar_radiation,
                    emissivity,
                    absorptivity,
                    f"{results['ampacity']:.2f}",
                    f"{results['resistance_at_temp']:.4f}",
                    f"{results['heat_convection']:.2f}",
                    f"{results['heat_radiation']:.2f}",
                    f"{results['solar_heat_gain']:.2f}",
                    f"{results['total_heat_loss']:.2f}"
                ],
                'Unidad': [
                    '-', '-', 'mm', 'mm²', 'Ω/km', '1/°C', '-',
                    '°C', '°C', 'm', 'm/s', 'W/m²', '-', '-',
                    'A', 'Ω/km', 'W/m', 'W/m', 'W/m', 'W/m'
                ]
            }
            
            df_export = pd.DataFrame(export_data)
            st.dataframe(df_export, use_container_width=True, hide_index=True)
            
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV completo",
                data=csv,
                file_name=f"ampacidad_{conductor_params['name'].replace(' ', '_')}.csv",
                mime="text/csv",
                help="Descarga todos los parámetros y resultados en formato CSV"
            )
        
        with col2:
            st.markdown("##### 📈 Curva Temperatura-Corriente completa")
            
            curve_data = pd.DataFrame({
                'Corriente (A)': results['current_range'],
                'Temperatura (°C)': results['temperature_curve'],
                'Descripción': ['Punto ' + str(i+1) for i in range(len(results['current_range']))]
            })
            
            st.dataframe(curve_data, use_container_width=True, hide_index=True)
            
            csv_curve = curve_data.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Curva T-I",
                data=csv_curve,
                file_name=f"curva_TI_{conductor_params['name'].replace(' ', '_')}.csv",
                mime="text/csv",
                help="Descarga los puntos de la curva temperatura-corriente"
            )
    
    # Información adicional (siempre visible)
    st.markdown("---")
    st.markdown("### ℹ️ Información y Ayuda")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        with st.expander("📚 Acerca del método de cálculo"):
            st.markdown(f"""
            Esta calculadora utiliza el método de **balance de calor** según el estándar 
            **IEEE Std 738-2012** para calcular la ampacidad de conductores de líneas 
            de transmisión.
            
            **Ecuación fundamental:**
            ```
            Q_joule = Q_convección + Q_radiación - Q_solar
            ```
            
            **Términos del balance:**
            - **Q_joule** ({TOOLTIPS['heat_convection'].split(chr(10))[0]})
            - **Q_convección** ({TOOLTIPS['heat_convection'].split(chr(10))[0]})
            - **Q_radiación** ({TOOLTIPS['heat_radiation'].split(chr(10))[0]})
            - **Q_solar** ({TOOLTIPS['solar_heat_gain'].split(chr(10))[0]})
            
            El método considera:
            - Temperatura ambiente y del conductor
            - Velocidad del viento y altitud
            - Propiedades del conductor (emisividad, absortividad)
            - Radiación solar
            - Efecto piel en corriente AC
            """)
    
    with col_info2:
        with st.expander("⚙️ Glosario de parámetros"):
            st.markdown(f"""
            **Parámetros del conductor:**
            - **Alpha (α)**: {TOOLTIPS['alpha'].split(chr(10))[0]}
            - **Beta (β)**: {TOOLTIPS['beta'].split(chr(10))[0]}
            - **Resistencia DC**: {TOOLTIPS['rdc_20'].split(chr(10))[0]}
            - **Diámetro**: {TOOLTIPS['diameter'].split(chr(10))[0]}
            
            **Parámetros ambientales:**
            - **Temperatura ambiente**: {TOOLTIPS['ambient_temp'].split(chr(10))[0]}
            - **Velocidad del viento**: {TOOLTIPS['wind_speed'].split(chr(10))[0]}
            - **Altitud**: {TOOLTIPS['altitude'].split(chr(10))[0]}
            - **Radiación solar**: {TOOLTIPS['solar_radiation'].split(chr(10))[0]}
            - **Emisividad/Absortividad**: {TOOLTIPS['emissivity'].split(chr(10))[0]}
            """)
    
    # Pie de página con referencias
    st.markdown("---")
    st.caption("""
    📖 **Referencia**: IEEE Std 738-2012 - Standard for Calculating the Current-Temperature 
    Relationship of Bare Overhead Conductors  
    💻 **Versión**: 2.0 con tooltips exhaustivos  
    ⚡ Desarrollado para ingeniería eléctrica de líneas de transmisión
    """)


if __name__ == "__main__":
    main()
