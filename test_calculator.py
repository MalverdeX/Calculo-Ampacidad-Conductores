"""
Pruebas unitarias para el calculador de ampacidad
"""

import unittest
import math
from main import AmpacityCalculator, LineParameters, EnvironmentalConditions

class TestAmpacityCalculator(unittest.TestCase):
    
    def setUp(self):
        self.calculator = AmpacityCalculator()
        
        # Parámetros de prueba típicos
        self.line_params = LineParameters(
            conductor_diameter=28.6,  # mm
            conductor_resistance=0.09,  # Ω/km
            conductor_material='ACSR',
            ambient_temperature=25.0,
            wind_speed=1.0,
            solar_radiation=900.0,
            emissivity=0.5,
            absorption_coefficient=0.5,
            max_conductor_temp=75.0
        )
        
        self.env_conditions = EnvironmentalConditions(
            ambient_temp=25.0,
            wind_speed=1.0,
            wind_angle=90.0,
            solar_radiation=900.0,
            altitude=0.0,
            atmospheric_pressure=101.3
        )
    
    def test_air_density_calculation(self):
        """Prueba de cálculo de densidad del aire"""
        # A nivel del mar, 20°C
        density = self.calculator.calculate_air_density(0, 20)
        self.assertAlmostEqual(density, 1.204, places=2)
        
        # A mayor altitud, menor densidad
        density_high_alt = self.calculator.calculate_air_density(2000, 20)
        self.assertLess(density_high_alt, density)
    
    def test_heat_convection(self):
        """Prueba de cálculo de convección"""
        temp_diff = 50.0  # °C
        wind_speed = 1.0  # m/s
        diameter = 28.6  # mm
        air_density = 1.2  # kg/m³
        
        q_conv = self.calculator.calculate_heat_convection(
            temp_diff, wind_speed, diameter, air_density
        )
        
        # La convección debe ser positiva
        self.assertGreater(q_conv, 0)
        
        # Mayor velocidad del viento = más convección
        q_conv_high_wind = self.calculator.calculate_heat_convection(
            temp_diff, 5.0, diameter, air_density
        )
        self.assertGreater(q_conv_high_wind, q_conv)
    
    def test_heat_radiation(self):
        """Prueba de cálculo de radiación"""
        conductor_temp = 75.0
        ambient_temp = 25.0
        emissivity = 0.5
        diameter = 28.6
        
        q_rad = self.calculator.calculate_heat_radiation(
            conductor_temp, ambient_temp, emissivity, diameter
        )
        
        # La radiación debe ser positiva
        self.assertGreater(q_rad, 0)
        
        # Mayor diferencia de temperatura = más radiación
        q_rad_high_diff = self.calculator.calculate_heat_radiation(
            100.0, ambient_temp, emissivity, diameter
        )
        self.assertGreater(q_rad_high_diff, q_rad)
    
    def test_solar_heat_gain(self):
        """Prueba de cálculo de ganancia solar"""
        solar_radiation = 900.0
        absorption = 0.5
        diameter = 28.6
        
        q_solar = self.calculator.calculate_solar_heat_gain(
            solar_radiation, absorption, diameter
        )
        
        # La ganancia solar debe ser positiva
        self.assertGreater(q_solar, 0)
        
        # Mayor radiación = más ganancia
        q_solar_high = self.calculator.calculate_solar_heat_gain(
            1000.0, absorption, diameter
        )
        self.assertGreater(q_solar_high, q_solar)
    
    def test_resistance_at_temperature(self):
        """Prueba de cálculo de resistencia a temperatura"""
        resistance_20c = 0.09
        temp = 75.0
        material = 'ACSR'
        
        resistance = self.calculator.calculate_resistance_at_temperature(
            resistance_20c, temp, material
        )
        
        # La resistencia debe aumentar con la temperatura
        self.assertGreater(resistance, resistance_20c)
    
    def test_ampacity_calculation(self):
        """Prueba principal de cálculo de ampacidad"""
        ampacity = self.calculator.calculate_ampacity(
            self.line_params, self.env_conditions
        )
        
        # La ampacidad debe ser positiva y razonable
        self.assertGreater(ampacity, 0)
        self.assertLess(ampacity, 5000)  # Límite superior razonable
        
        # Mayor temperatura ambiente = menor ampacidad
        hot_conditions = EnvironmentalConditions(
            ambient_temp=40.0,
            wind_speed=1.0,
            wind_angle=90.0,
            solar_radiation=900.0,
            altitude=0.0,
            atmospheric_pressure=101.3
        )
        
        ampacity_hot = self.calculator.calculate_ampacity(
            self.line_params, hot_conditions
        )
        
        self.assertLess(ampacity_hot, ampacity)
        
        # Mayor velocidad del viento = mayor ampacidad
        windy_conditions = EnvironmentalConditions(
            ambient_temp=25.0,
            wind_speed=5.0,
            wind_angle=90.0,
            solar_radiation=900.0,
            altitude=0.0,
            atmospheric_pressure=101.3
        )
        
        ampacity_windy = self.calculator.calculate_ampacity(
            self.line_params, windy_conditions
        )
        
        self.assertGreater(ampacity_windy, ampacity)

class TestParameterValidation(unittest.TestCase):
    """Pruebas de validación de parámetros"""
    
    def test_line_parameters_creation(self):
        """Prueba de creación de parámetros de línea"""
        params = LineParameters(
            conductor_diameter=28.6,
            conductor_resistance=0.09,
            conductor_material='ACSR',
            ambient_temperature=25.0,
            wind_speed=1.0,
            solar_radiation=900.0,
            emissivity=0.5,
            absorption_coefficient=0.5,
            max_conductor_temp=75.0
        )
        
        self.assertEqual(params.conductor_diameter, 28.6)
        self.assertEqual(params.conductor_material, 'ACSR')
        self.assertEqual(params.max_conductor_temp, 75.0)
    
    def test_environmental_conditions_creation(self):
        """Prueba de creación de condiciones ambientales"""
        conditions = EnvironmentalConditions(
            ambient_temp=25.0,
            wind_speed=1.0,
            wind_angle=90.0,
            solar_radiation=900.0,
            altitude=0.0,
            atmospheric_pressure=101.3
        )
        
        self.assertEqual(conditions.ambient_temp, 25.0)
        self.assertEqual(conditions.wind_speed, 1.0)
        self.assertEqual(conditions.altitude, 0.0)

def run_comprehensive_test():
    """Ejecutar pruebas exhaustivas con datos de ejemplo"""
    calculator = AmpacityCalculator()
    
    # Caso de prueba 1: Condiciones estándar
    line_params = LineParameters(
        conductor_diameter=28.6,
        conductor_resistance=0.09,
        conductor_material='ACSR',
        ambient_temperature=25.0,
        wind_speed=1.0,
        solar_radiation=900.0,
        emissivity=0.5,
        absorption_coefficient=0.5,
        max_conductor_temp=75.0
    )
    
    env_conditions = EnvironmentalConditions(
        ambient_temp=25.0,
        wind_speed=1.0,
        wind_angle=90.0,
        solar_radiation=900.0,
        altitude=0.0,
        atmospheric_pressure=101.3
    )
    
    ampacity = calculator.calculate_ampacity(line_params, env_conditions)
    print(f"Caso estándar - Ampacidad: {ampacity:.1f} A")
    
    # Caso de prueba 2: Condiciones adversas
    adverse_conditions = EnvironmentalConditions(
        ambient_temp=40.0,
        wind_speed=0.5,
        wind_angle=90.0,
        solar_radiation=1000.0,
        altitude=1000.0,
        atmospheric_pressure=90.0
    )
    
    ampacity_adverse = calculator.calculate_ampacity(line_params, adverse_conditions)
    print(f"Condiciones adversas - Ampacidad: {ampacity_adverse:.1f} A")
    print(f"Reducción: {(1 - ampacity_adverse/ampacity)*100:.1f}%")
    
    # Caso de prueba 3: Condiciones favorables
    favorable_conditions = EnvironmentalConditions(
        ambient_temp=10.0,
        wind_speed=5.0,
        wind_angle=90.0,
        solar_radiation=500.0,
        altitude=0.0,
        atmospheric_pressure=101.3
    )
    
    ampacity_favorable = calculator.calculate_ampacity(line_params, favorable_conditions)
    print(f"Condiciones favorables - Ampacidad: {ampacity_favorable:.1f} A")
    print(f"Aumento: {(ampacity_favorable/ampacity - 1)*100:.1f}%")

if __name__ == '__main__':
    print("Ejecutando pruebas unitarias...")
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*50)
    print("Ejecutando pruebas exhaustivas...")
    run_comprehensive_test()
