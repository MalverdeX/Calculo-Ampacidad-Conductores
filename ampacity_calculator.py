"""
Módulo principal de cálculo de ampacidad para líneas de transmisión
"""

import math
import numpy as np
from typing import Dict, Tuple, Optional
from config import (
    STEFAN_BOLTZMANN, GRAVITY, AIR_VISCOSITY, AIR_THERMAL_CONDUCTIVITY,
    SEA_LEVEL_DENSITY, DEFAULT_PARAMETERS
)


class AmpacityCalculator:
    """
    Calculadora de ampacidad basada en el método de balance de calor
    IEEE Std 738-2012
    """
    
    def __init__(self):
        self.stefan_boltzmann = STEFAN_BOLTZMANN
        self.gravity = GRAVITY
        self.air_viscosity = AIR_VISCOSITY
        self.air_thermal_conductivity = AIR_THERMAL_CONDUCTIVITY
        self.sea_level_density = SEA_LEVEL_DENSITY
    
    def calculate_air_density(self, altitude: float, temp_celsius: float) -> float:
        """
        Calcular densidad del aire a una altitud y temperatura dadas
        
        Args:
            altitude: Altitud en metros sobre el nivel del mar
            temp_celsius: Temperatura ambiente en grados Celsius
            
        Returns:
            Densidad del aire en kg/m³
        """
        altitude_factor = math.exp(-altitude / 8000)
        temp_factor = 293.15 / (temp_celsius + 273.15)
        return self.sea_level_density * altitude_factor * temp_factor
    
    def calculate_heat_convection(self, temp_diff: float, wind_speed: float, 
                                conductor_diameter: float, air_density: float) -> float:
        """
        Calcular transferencia de calor por convección
        según IEEE Std 738-2012
        
        Args:
            temp_diff: Diferencia de temperatura (conductor - ambiente) en °C
            wind_speed: Velocidad del viento en m/s
            conductor_diameter: Diámetro del conductor en mm
            air_density: Densidad del aire en kg/m³
            
        Returns:
            Calor por convección en W/m
        """
        diameter_m = conductor_diameter / 1000
        
        if wind_speed > 0.1:
            # Convección forzada - IEEE 738-2012 Ecuación 11a
            Re = air_density * wind_speed * diameter_m / self.air_viscosity
            if Re < 1000:
                Nu = 0.65 + 0.44 * Re**0.52
            else:
                Nu = 0.292 * Re**0.6
        else:
            # Convección natural - IEEE 738-2012 Ecuación 10a
            T_film = temp_diff / 2 + 273.15  # Temperatura de la película
            beta_thermal = 1 / T_film  # Coeficiente de expansión térmica
            Gr = (self.gravity * beta_thermal * temp_diff * diameter_m**3) / (
                (self.air_viscosity / air_density)**2
            )
            Pr = 0.713  # Número de Prandtl para aire
            
            if Gr * Pr < 1e4:
                Nu = 0.4 + 0.55 * (Gr * Pr)**0.25
            else:
                Nu = 0.52 * (Gr * Pr)**0.333
        
        h_conv = Nu * self.air_thermal_conductivity / diameter_m
        return h_conv * math.pi * diameter_m * temp_diff
    
    def calculate_heat_radiation(self, conductor_temp: float, ambient_temp: float,
                               emissivity: float, conductor_diameter: float) -> float:
        """
        Calcular transferencia de calor por radiación
        
        Args:
            conductor_temp: Temperatura del conductor en °C
            ambient_temp: Temperatura ambiente en °C
            emissivity: Emisividad del conductor (0-1)
            conductor_diameter: Diámetro del conductor en mm
            
        Returns:
            Calor por radiación en W/m
        """
        T_conductor = conductor_temp + 273.15
        T_ambient = ambient_temp + 273.15
        diameter_m = conductor_diameter / 1000
        
        q_rad = (self.stefan_boltzmann * emissivity * math.pi * diameter_m * 
                (T_conductor**4 - T_ambient**4))
        return q_rad
    
    def calculate_solar_heat_gain(self, solar_radiation: float, absorptivity: float,
                                conductor_diameter: float, angle_of_sun: float = 90.0) -> float:
        """
        Calcular ganancia de calor por radiación solar
        según IEEE Std 738-2012
        
        Args:
            solar_radiation: Radiación solar en W/m²
            absorptivity: Absortividad del conductor (0-1)
            conductor_diameter: Diámetro del conductor en mm
            angle_of_sun: Ángulo del sol en grados
            
        Returns:
            Calor solar en W/m
        """
        diameter_m = conductor_diameter / 1000
        
        # Factor de proyección según IEEE 738-2012
        angle_rad = math.radians(angle_of_sun)
        projection_factor = math.sin(angle_rad)
        
        q_solar = solar_radiation * absorptivity * diameter_m * projection_factor
        return q_solar
    
    def calculate_resistance(self, rdc_20: float, alpha: float, beta: float,
                           conductor_temp: float, current: float) -> float:
        """
        Calcular resistencia del conductor a temperatura y corriente dadas
        según IEEE Std 738-2012 Ecuación 2
        
        Args:
            rdc_20: Resistencia DC a 20°C en Ω/km
            alpha: Coeficiente de temperatura de resistencia
            beta: Coeficiente de efecto piel
            conductor_temp: Temperatura del conductor en °C
            current: Corriente en A
            
        Returns:
            Resistencia en Ω/km
        """
        # Corrección por temperatura - IEEE 738-2012 Ecuación 2a
        r_temp = rdc_20 * (1 + alpha * (conductor_temp - 20))
        
        # Efecto piel - IEEE 738-2012 Ecuación 2b
        # El factor beta depende de la frecuencia y del conductor
        # Para 60 Hz, valores típicos están entre 0.01 y 0.1
        if current > 0:
            # Factor de efecto piel más realista
            f_skin = 1 + beta * (current / 1000)**2
        else:
            f_skin = 1.0
        
        return r_temp * f_skin
    
    def calculate_joule_heating(self, resistance: float, current: float) -> float:
        """
        Calcular calentamiento por efecto Joule
        
        Args:
            resistance: Resistencia en Ω/km
            current: Corriente en A
            
        Returns:
            Calor por Joule en W/m
        """
        return resistance * current**2 / 1000
    
    def calculate_ampacity(self, conductor_params: Dict, environmental_params: Dict,
                          target_conductor_temp: Optional[float] = None) -> Dict:
        """
        Calcular ampacidad usando método iterativo de balance de calor
        
        Args:
            conductor_params: Parámetros del conductor
            environmental_params: Parámetros ambientales
            target_conductor_temp: Temperatura objetivo del conductor (opcional)
            
        Returns:
            Diccionario con resultados del cálculo
        """
        # Parámetros del conductor
        diameter = conductor_params['diameter']
        rdc_20 = conductor_params['rdc_20']
        alpha = conductor_params['alpha']
        beta = conductor_params['beta']
        
        # Parámetros ambientales
        ambient_temp = environmental_params.get('ambient_temperature', 
                                               DEFAULT_PARAMETERS['ambient_temperature'])
        altitude = environmental_params.get('altitude', 
                                          DEFAULT_PARAMETERS['altitude'])
        wind_speed = environmental_params.get('wind_speed', 
                                            DEFAULT_PARAMETERS['wind_speed'])
        solar_radiation = environmental_params.get('solar_radiation', 
                                                  DEFAULT_PARAMETERS['solar_radiation'])
        emissivity = environmental_params.get('emissivity', 
                                            DEFAULT_PARAMETERS['emissivity'])
        absorptivity = environmental_params.get('absorptivity', 
                                              DEFAULT_PARAMETERS['absorptivity'])
        
        if target_conductor_temp is None:
            target_conductor_temp = environmental_params.get('conductor_temperature_limit',
                                                           DEFAULT_PARAMETERS['conductor_temperature_limit'])
        
        # Calcular densidad del aire
        air_density = self.calculate_air_density(altitude, ambient_temp)
        
        # Calcular pérdidas de calor (dependen de la temperatura del conductor)
        temp_diff = target_conductor_temp - ambient_temp
        q_convection = self.calculate_heat_convection(temp_diff, wind_speed, 
                                                     diameter, air_density)
        q_radiation = self.calculate_heat_radiation(target_conductor_temp, ambient_temp,
                                                   emissivity, diameter)
        q_solar = self.calculate_solar_heat_gain(solar_radiation, absorptivity, 
                                                diameter)
        
        # Calor total que disipa el conductor
        total_heat_loss = q_convection + q_radiation - q_solar
        
        # Calcular resistencia a temperatura de operación
        resistance = self.calculate_resistance(rdc_20, alpha, beta, 
                                             target_conductor_temp, 1000)
        
        # Calcular ampacidad (corriente máxima)
        if resistance > 0:
            ampacity = math.sqrt(total_heat_loss / resistance * 1000)
        else:
            ampacity = 0
        
        # Calcular temperatura para diferentes corrientes
        current_range = np.linspace(0, ampacity * 1.2, 50)
        temp_curve = []
        
        for current in current_range:
            if current == 0:
                temp_curve.append(ambient_temp)
                continue
                
            # Método directo: resolver balance de calor iterativamente
            # Q_joule(I,T) = Q_convección(T) + Q_radiación(T) - Q_solar
            
            # Temperatura inicial estimada
            temp_estimate = ambient_temp + (current / ampacity) * (target_conductor_temp - ambient_temp)
            temp = max(temp_estimate, ambient_temp + 1)
            
            for iteration in range(100):  # Máximo 100 iteraciones
                # Calcular todos los términos a esta temperatura
                temp_diff = temp - ambient_temp
                
                # Términos de pérdida de calor
                q_conv = self.calculate_heat_convection(temp_diff, wind_speed, 
                                                      diameter, air_density)
                q_rad = self.calculate_heat_radiation(temp, ambient_temp, 
                                                    emissivity, diameter)
                total_cooling = q_conv + q_rad - q_solar
                
                # Término de ganancia de calor
                r = self.calculate_resistance(rdc_20, alpha, beta, temp, current)
                q_joule = self.calculate_joule_heating(r, current)
                
                # Error en el balance de calor
                error = q_joule - total_cooling
                
                # Si el error es pequeño, convergió
                if abs(error) < 0.1:
                    break
                
                # Ajustar temperatura usando método de Newton simplificado
                # Si q_joule > total_cooling, subir temperatura
                # Si q_joule < total_cooling, bajar temperatura
                
                if total_cooling > 0:
                    # Derivada aproximada del balance de calor
                    dQ_dT = (self.calculate_heat_convection(temp_diff + 0.1, wind_speed, 
                                                       diameter, air_density) - q_conv) / 0.1
                    dQ_dT += (self.calculate_heat_radiation(temp + 0.1, ambient_temp, 
                                                      emissivity, diameter) - q_rad) / 0.1
                    
                    # Derivada del calor Joule
                    dR_dT = rdc_20 * alpha / 1000  # Ω/(km·°C)
                    dQj_dT = current**2 * dR_dT / 1000  # W/(m·°C)
                    
                    # Derivada del error
                    dError_dT = dQj_dT - dQ_dT
                    
                    if abs(dError_dT) > 0.001:
                        # Paso de Newton
                        temp_step = error / dError_dT
                        # Limitar paso para evitar oscilaciones
                        temp_step = max(min(temp_step, 5), -5)
                        temp_new = temp - temp_step
                    else:
                        # Si la derivada es muy pequeña, usar paso fijo
                        if error > 0:
                            temp_new = temp + 0.5
                        else:
                            temp_new = temp - 0.5
                else:
                    # Si no hay disipación, subir temperatura
                    temp_new = temp + 1.0
                
                # Limitar temperatura
                temp = max(min(temp_new, target_conductor_temp * 2), ambient_temp)
            
            temp_curve.append(temp)
        
        return {
            'ampacity': ampacity,
            'conductor_temperature': target_conductor_temp,
            'ambient_temperature': ambient_temp,
            'heat_convection': q_convection,
            'heat_radiation': q_radiation,
            'solar_heat_gain': q_solar,
            'total_heat_loss': total_heat_loss,
            'resistance_at_temp': resistance,
            'air_density': air_density,
            'current_range': current_range.tolist(),
            'temperature_curve': temp_curve,
            'calculation_details': {
                'wind_speed': wind_speed,
                'altitude': altitude,
                'solar_radiation': solar_radiation,
                'emissivity': emissivity,
                'absorptivity': absorptivity
            }
        }


class ConductorDatabase:
    """
    Base de datos de conductores con sus parámetros eléctricos y físicos
    """
    
    def __init__(self):
        self.conductors = {
            # ACSR - Aluminum Conductor Steel Reinforced
            'ACSR_1/0_AW': {
                'name': 'ACSR 1/0 AW',
                'type': 'ACSR',
                'diameter': 11.68,  # mm
                'area': 53.5,  # mm²
                'rdc_20': 0.540,  # Ω/km
                'alpha': 0.00403,  # 1/°C
                'beta': 0.025,  # Factor de efecto piel a 60 Hz
                'weight': 0.326,  # kg/m
                'max_temp': 75.0  # °C
            },
            'ACSR_4/0_AW': {
                'name': 'ACSR 4/0 AW',
                'type': 'ACSR',
                'diameter': 15.21,
                'area': 107.2,
                'rdc_20': 0.270,
                'alpha': 0.00403,
                'beta': 0.030,
                'weight': 0.540,
                'max_temp': 75.0
            },
            'ACSR_336.4_kcmil': {
                'name': 'ACSR 336.4 kcmil',
                'type': 'ACSR',
                'diameter': 18.29,
                'area': 170.5,
                'rdc_20': 0.170,
                'alpha': 0.00403,
                'beta': 0.035,
                'weight': 0.815,
                'max_temp': 75.0
            },
            'ACSR_477_kcmil': {
                'name': 'ACSR 477 kcmil',
                'type': 'ACSR',
                'diameter': 21.79,
                'area': 241.7,
                'rdc_20': 0.120,
                'alpha': 0.00403,
                'beta': 0.040,
                'weight': 1.099,
                'max_temp': 75.0
            },
            'ACSR_795_kcmil': {
                'name': 'ACSR 795 kcmil',
                'type': 'ACSR',
                'diameter': 28.14,
                'area': 402.9,
                'rdc_20': 0.072,
                'alpha': 0.00403,
                'beta': 0.045,
                'weight': 1.632,
                'max_temp': 75.0
            },
            
            # AAC - All Aluminum Conductor
            'AAC_1/0_AW': {
                'name': 'AAC 1/0 AW',
                'type': 'AAC',
                'diameter': 10.41,
                'area': 53.5,
                'rdc_20': 0.538,
                'alpha': 0.00404,
                'beta': 0.015,
                'weight': 0.145,
                'max_temp': 70.0
            },
            'AAC_4/0_AW': {
                'name': 'AAC 4/0 AW',
                'type': 'AAC',
                'diameter': 13.41,
                'area': 107.2,
                'rdc_20': 0.269,
                'alpha': 0.00404,
                'beta': 0.020,
                'weight': 0.290,
                'max_temp': 70.0
            },
            
            # Copper conductors
            'CU_1/0_AW': {
                'name': 'Copper 1/0 AW',
                'type': 'CU',
                'diameter': 8.25,
                'area': 53.5,
                'rdc_20': 0.322,
                'alpha': 0.00393,
                'beta': 0.018,
                'weight': 0.476,
                'max_temp': 80.0
            },
            'CU_4/0_AW': {
                'name': 'Copper 4/0 AW',
                'type': 'CU',
                'diameter': 11.68,
                'area': 107.2,
                'rdc_20': 0.161,
                'alpha': 0.00393,
                'beta': 0.025,
                'weight': 0.953,
                'max_temp': 80.0
            }
        }
    
    def get_conductor(self, conductor_id: str) -> Optional[Dict]:
        """Obtener parámetros de un conductor por ID"""
        return self.conductors.get(conductor_id)
    
    def get_all_conductors(self) -> Dict:
        """Obtener todos los conductores disponibles"""
        return self.conductors
    
    def get_conductors_by_type(self, conductor_type: str) -> Dict:
        """Obtener conductores por tipo"""
        return {k: v for k, v in self.conductors.items() 
                if v['type'] == conductor_type}
    
    def add_conductor(self, conductor_id: str, params: Dict) -> None:
        """Agregar un nuevo conductor a la base de datos"""
        self.conductors[conductor_id] = params
    
    def update_conductor(self, conductor_id: str, params: Dict) -> bool:
        """Actualizar parámetros de un conductor existente"""
        if conductor_id in self.conductors:
            self.conductors[conductor_id].update(params)
            return True
        return False
    
    def delete_conductor(self, conductor_id: str) -> bool:
        """Eliminar un conductor de la base de datos"""
        if conductor_id in self.conductors:
            del self.conductors[conductor_id]
            return True
        return False
