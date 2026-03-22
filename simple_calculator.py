"""
Calculadora simple de ampacidad (sin Streamlit)
"""

import math
import sys

class AmpacityCalculator:
    def __init__(self):
        self.stefan_boltzmann = 5.67e-8
    
    def calculate_air_density(self, altitude, temp_celsius):
        sea_level_density = 1.204
        altitude_factor = math.exp(-altitude / 8000)
        temp_factor = 293.15 / (temp_celsius + 273.15)
        return sea_level_density * altitude_factor * temp_factor
    
    def calculate_heat_convection(self, temp_diff, wind_speed, conductor_diameter, air_density):
        if wind_speed > 0.1:
            Re = air_density * wind_speed * conductor_diameter / 1.8e-5
            Nu = 0.65 + 0.35 * Re**0.52
        else:
            Gr = 9.81 * temp_diff * (conductor_diameter/1000)**3 / ((temp_diff + 273.15) * (1.8e-5/air_density)**2)
            Nu = 0.48 * Gr**0.25
        
        k_air = 0.024
        h_conv = Nu * k_air / (conductor_diameter / 1000)
        return h_conv * math.pi * (conductor_diameter / 1000) * temp_diff
    
    def calculate_heat_radiation(self, conductor_temp, ambient_temp, emissivity, conductor_diameter):
        T_conductor = conductor_temp + 273.15
        T_ambient = ambient_temp + 273.15
        q_rad = self.stefan_boltzmann * emissivity * math.pi * (conductor_diameter / 1000) * (T_conductor**4 - T_ambient**4)
        return q_rad
    
    def calculate_solar_heat_gain(self, solar_radiation, absorption_coefficient, conductor_diameter):
        return solar_radiation * absorption_coefficient * conductor_diameter / 1000
    
    def calculate_resistance_at_temperature(self, resistance_20c, temp, material):
        temp_coefficients = {'ACSR': 0.00393, 'AAC': 0.00393, 'AAAC': 0.00393, 'CU': 0.00393}
        alpha = temp_coefficients.get(material, 0.00393)
        return resistance_20c * (1 + alpha * (temp - 20))
    
    def calculate_ampacity(self, params):
        max_temp = params['max_conductor_temp']
        ambient_temp = params['ambient_temp']
        temp_diff = max_temp - ambient_temp
        
        air_density = self.calculate_air_density(params['altitude'], ambient_temp)
        
        q_conv = self.calculate_heat_convection(
            temp_diff, params['wind_speed'], params['conductor_diameter'], air_density
        )
        
        q_rad = self.calculate_heat_radiation(
            max_temp, ambient_temp, params['emissivity'], params['conductor_diameter']
        )
        
        q_solar = self.calculate_solar_heat_gain(
            params['solar_radiation'], params['absorption_coefficient'], params['conductor_diameter']
        )
        
        resistance = self.calculate_resistance_at_temperature(
            params['conductor_resistance'], max_temp, params['conductor_material']
        )
        
        heat_loss = q_conv + q_rad - q_solar
        
        if heat_loss <= 0:
            return 0
        
        ampacity = math.sqrt(heat_loss / resistance)
        return ampacity

def main():
    print("=" * 60)
    print("🔌 CALCULADORA DE AMPACIDAD DE LÍNEAS DE TRANSMISIÓN")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    
    # Parámetros por defecto
    params = {
        'conductor_diameter': 28.6,
        'conductor_resistance': 0.09,
        'conductor_material': 'ACSR',
        'ambient_temp': 25.0,
        'wind_speed': 1.0,
        'solar_radiation': 900.0,
        'emissivity': 0.5,
        'absorption_coefficient': 0.5,
        'max_conductor_temp': 75.0,
        'altitude': 0.0
    }
    
    print("\n📋 Parámetros actuales:")
    print(f"• Diámetro del conductor: {params['conductor_diameter']} mm")
    print(f"• Resistencia: {params['conductor_resistance']} Ω/km")
    print(f"• Material: {params['conductor_material']}")
    print(f"• Temperatura ambiente: {params['ambient_temp']}°C")
    print(f"• Velocidad del viento: {params['wind_speed']} m/s")
    print(f"• Radiación solar: {params['solar_radiation']} W/m²")
    print(f"• Temperatura máxima del conductor: {params['max_conductor_temp']}°C")
    print(f"• Altitud: {params['altitude']} m")
    
    ampacity = calculator.calculate_ampacity(params)
    
    print("\n📊 RESULTADOS:")
    print(f"• Ampacidad máxima: {ampacity:.1f} A")
    
    # Calcular potencia para 230 kV
    voltage = 230  # kV
    power = ampacity * voltage * math.sqrt(3) / 1000  # MW
    print(f"• Potencia máxima (230 kV): {power:.1f} MW")
    
    # Análisis de sensibilidad
    print("\n📈 ANÁLISIS DE SENSIBILIDAD:")
    
    # Efecto de temperatura ambiente
    print("\n1. Efecto de la temperatura ambiente:")
    for temp in [10, 20, 30, 40]:
        params_temp = params.copy()
        params_temp['ambient_temp'] = temp
        amp = calculator.calculate_ampacity(params_temp)
        print(f"   • {temp}°C: {amp:.1f} A")
    
    # Efecto de velocidad del viento
    print("\n2. Efecto de la velocidad del viento:")
    for wind in [0.5, 1.0, 2.0, 5.0]:
        params_wind = params.copy()
        params_wind['wind_speed'] = wind
        amp = calculator.calculate_ampacity(params_wind)
        print(f"   • {wind} m/s: {amp:.1f} A")
    
    # Balance térmico detallado
    print("\n🔍 BALANCE TÉRMICO DETALLADO:")
    temp_diff = params['max_conductor_temp'] - params['ambient_temp']
    air_density = calculator.calculate_air_density(params['altitude'], params['ambient_temp'])
    
    q_conv = calculator.calculate_heat_convection(
        temp_diff, params['wind_speed'], params['conductor_diameter'], air_density
    )
    
    q_rad = calculator.calculate_heat_radiation(
        params['max_conductor_temp'], params['ambient_temp'], 
        params['emissivity'], params['conductor_diameter']
    )
    
    q_solar = calculator.calculate_solar_heat_gain(
        params['solar_radiation'], params['absorption_coefficient'], params['conductor_diameter']
    )
    
    resistance = calculator.calculate_resistance_at_temperature(
        params['conductor_resistance'], params['max_conductor_temp'], params['conductor_material']
    )
    
    heat_loss = q_conv + q_rad - q_solar
    
    print(f"• Pérdida por convección: {q_conv:.2f} W/m")
    print(f"• Pérdida por radiación: {q_rad:.2f} W/m")
    print(f"• Ganancia solar: {q_solar:.2f} W/m")
    print(f"• Pérdida neta: {heat_loss:.2f} W/m")
    print(f"• Resistencia a {params['max_conductor_temp']}°C: {resistance:.6f} Ω/km")
    
    print("\n" + "=" * 60)
    print("✅ Cálculo completado")
    print("=" * 60)

if __name__ == "__main__":
    main()
