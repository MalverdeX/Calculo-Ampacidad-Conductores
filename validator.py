"""
Módulo de validación y manejo de errores
"""

import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Niveles de severidad de validación"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Resultado de una validación"""
    is_valid: bool
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    suggested_value: Optional[Any] = None


class ValidationException(Exception):
    """Excepción personalizada para errores de validación"""
    def __init__(self, message: str, validation_results: List[ValidationResult] = None):
        super().__init__(message)
        self.validation_results = validation_results or []


class AmpacityValidator:
    """
    Validador especializado para parámetros de cálculo de ampacidad
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ampacity_validation.log'),
                logging.StreamHandler()
            ]
        )
    
    def validate_conductor_parameters(self, params: Dict) -> List[ValidationResult]:
        """Validar parámetros del conductor"""
        results = []
        
        # Validar campos requeridos
        required_fields = ['name', 'type', 'diameter', 'area', 'rdc_20', 
                          'alpha', 'beta', 'weight', 'max_temp']
        
        for field in required_fields:
            if field not in params:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Campo requerido faltante: {field}",
                    field=field
                ))
        
        if not all(r.is_valid for r in results if r.field in required_fields):
            return results
        
        # Validar nombre
        if not params['name'] or not isinstance(params['name'], str):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="El nombre del conductor debe ser un texto no vacío",
                field="name"
            ))
        
        # Validar tipo
        valid_types = ['ACSR', 'AAC', 'AAAC', 'ACAR', 'CU']
        if params['type'] not in valid_types:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Tipo de conductor inválido. Valores válidos: {valid_types}",
                field="type",
                suggested_value="ACSR"
            ))
        
        # Validar diámetro
        diameter = params['diameter']
        if not isinstance(diameter, (int, float)) or diameter <= 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="El diámetro debe ser un número positivo",
                field="diameter",
                suggested_value=10.0
            ))
        elif diameter > 50:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="El diámetro es muy grande para un conductor típico",
                field="diameter"
            ))
        
        # Validar área
        area = params['area']
        if not isinstance(area, (int, float)) or area <= 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="El área debe ser un número positivo",
                field="area",
                suggested_value=50.0
            ))
        
        # Validar relación área-diámetro
        if isinstance(diameter, (int, float)) and isinstance(area, (int, float)):
            theoretical_area = 3.14159 * (diameter/2)**2
            if area > theoretical_area * 1.5:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="El área parece inconsistente con el diámetro",
                    field="area"
                ))
        
        # Validar resistencia
        rdc_20 = params['rdc_20']
        if not isinstance(rdc_20, (int, float)) or rdc_20 <= 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La resistencia debe ser un número positivo",
                field="rdc_20",
                suggested_value=0.1
            ))
        elif rdc_20 > 10:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="La resistencia es muy alta para un conductor típico",
                field="rdc_20"
            ))
        
        # Validar alpha
        alpha = params['alpha']
        if not isinstance(alpha, (int, float)) or alpha <= 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Alpha debe ser un número positivo",
                field="alpha",
                suggested_value=0.004
            ))
        elif alpha > 0.01:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="Alpha parece muy alto para materiales comunes",
                field="alpha",
                suggested_value=0.004
            ))
        
        # Validar beta
        beta = params['beta']
        if not isinstance(beta, (int, float)) or beta < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Beta debe ser un número no negativo",
                field="beta",
                suggested_value=0.0001
            ))
        elif beta > 0.01:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="Beta es muy alto, revisar unidades",
                field="beta"
            ))
        
        # Validar peso
        weight = params['weight']
        if not isinstance(weight, (int, float)) or weight <= 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="El peso debe ser un número positivo",
                field="weight",
                suggested_value=0.5
            ))
        
        # Validar temperatura máxima
        max_temp = params['max_temp']
        if not isinstance(max_temp, (int, float)) or max_temp <= 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La temperatura máxima debe ser un número positivo",
                field="max_temp",
                suggested_value=75.0
            ))
        elif max_temp > 200:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="La temperatura máxima es muy alta para conductores estándar",
                field="max_temp",
                suggested_value=75.0
            ))
        elif max_temp < 50:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="Temperatura máxima baja, puede limitar la capacidad",
                field="max_temp"
            ))
        
        return results
    
    def validate_environmental_parameters(self, params: Dict) -> List[ValidationResult]:
        """Validar parámetros ambientales"""
        results = []
        
        # Validar temperatura ambiente
        ambient_temp = params.get('ambient_temperature')
        if ambient_temp is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Temperatura ambiente es requerida",
                field="ambient_temperature",
                suggested_value=40.0
            ))
        elif not isinstance(ambient_temp, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Temperatura ambiente debe ser un número",
                field="ambient_temperature"
            ))
        elif ambient_temp < -50 or ambient_temp > 60:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="Temperatura ambiente fuera de rangos típicos (-50°C a 60°C)",
                field="ambient_temperature"
            ))
        
        # Validar temperatura máxima del conductor
        conductor_temp_limit = params.get('conductor_temperature_limit')
        if conductor_temp_limit is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Temperatura máxima del conductor es requerida",
                field="conductor_temperature_limit",
                suggested_value=75.0
            ))
        elif not isinstance(conductor_temp_limit, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Temperatura máxima del conductor debe ser un número",
                field="conductor_temperature_limit"
            ))
        elif conductor_temp_limit <= 0 or conductor_temp_limit > 200:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Temperatura máxima del conductor debe estar entre 0°C y 200°C",
                field="conductor_temperature_limit",
                suggested_value=75.0
            ))
        
        # Validar diferencia de temperaturas
        if (isinstance(ambient_temp, (int, float)) and 
            isinstance(conductor_temp_limit, (int, float))):
            if conductor_temp_limit <= ambient_temp:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="La temperatura máxima del conductor debe ser mayor que la temperatura ambiente",
                    field="conductor_temperature_limit"
                ))
            elif conductor_temp_limit - ambient_temp < 10:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message="La diferencia de temperaturas es muy pequeña, puede limitar la capacidad",
                    field="conductor_temperature_limit"
                ))
        
        # Validar altitud
        altitude = params.get('altitude')
        if altitude is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Altitud es requerida",
                field="altitude",
                suggested_value=0.0
            ))
        elif not isinstance(altitude, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Altitud debe ser un número",
                field="altitude"
            ))
        elif altitude < 0 or altitude > 5000:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="Altitud fuera de rangos típicos (0m a 5000m)",
                field="altitude"
            ))
        
        # Validar velocidad del viento
        wind_speed = params.get('wind_speed')
        if wind_speed is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Velocidad del viento es requerida",
                field="wind_speed",
                suggested_value=0.61
            ))
        elif not isinstance(wind_speed, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Velocidad del viento debe ser un número",
                field="wind_speed"
            ))
        elif wind_speed < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La velocidad del viento no puede ser negativa",
                field="wind_speed",
                suggested_value=0.0
            ))
        elif wind_speed > 30:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="Velocidad del viento muy alta, condiciones extremas",
                field="wind_speed"
            ))
        
        # Validar radiación solar
        solar_radiation = params.get('solar_radiation')
        if solar_radiation is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Radiación solar es requerida",
                field="solar_radiation",
                suggested_value=1000.0
            ))
        elif not isinstance(solar_radiation, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Radiación solar debe ser un número",
                field="solar_radiation"
            ))
        elif solar_radiation < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La radiación solar no puede ser negativa",
                field="solar_radiation",
                suggested_value=0.0
            ))
        elif solar_radiation > 1400:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="Radiación solar muy alta, condiciones extremas",
                field="solar_radiation"
            ))
        
        # Validar emisividad
        emissivity = params.get('emissivity')
        if emissivity is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Emisividad es requerida",
                field="emissivity",
                suggested_value=0.8
            ))
        elif not isinstance(emissivity, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Emisividad debe ser un número",
                field="emissivity"
            ))
        elif emissivity < 0 or emissivity > 1:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La emisividad debe estar entre 0 y 1",
                field="emissivity",
                suggested_value=0.8
            ))
        
        # Validar absortividad
        absorptivity = params.get('absorptivity')
        if absorptivity is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Absortividad es requerida",
                field="absorptivity",
                suggested_value=0.8
            ))
        elif not isinstance(absorptivity, (int, float)):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Absortividad debe ser un número",
                field="absorptivity"
            ))
        elif absorptivity < 0 or absorptivity > 1:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La absortividad debe estar entre 0 y 1",
                field="absorptivity",
                suggested_value=0.8
            ))
        
        return results
    
    def validate_calculation_results(self, results: Dict) -> List[ValidationResult]:
        """Validar resultados del cálculo"""
        validation_results = []
        
        # Validar ampacidad
        ampacity = results.get('ampacity')
        if ampacity is None:
            validation_results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="No se pudo calcular la ampacidad",
                field="ampacity"
            ))
        elif not isinstance(ampacity, (int, float)):
            validation_results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La ampacidad debe ser un número",
                field="ampacity"
            ))
        elif ampacity <= 0:
            validation_results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="La ampacidad debe ser positiva",
                field="ampacity"
            ))
        elif ampacity > 5000:
            validation_results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="Ampacidad muy alta, verificar parámetros",
                field="ampacity"
            ))
        
        # Validar temperaturas
        conductor_temp = results.get('conductor_temperature')
        ambient_temp = results.get('ambient_temperature')
        
        if conductor_temp is not None and ambient_temp is not None:
            if conductor_temp <= ambient_temp:
                validation_results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="La temperatura del conductor debe ser mayor que la ambiente",
                    field="conductor_temperature"
                ))
        
        # Validar balance de calor
        heat_convection = results.get('heat_convection')
        heat_radiation = results.get('heat_radiation')
        solar_heat_gain = results.get('solar_heat_gain')
        total_heat_loss = results.get('total_heat_loss')
        
        if all(x is not None for x in [heat_convection, heat_radiation, solar_heat_gain, total_heat_loss]):
            calculated_loss = heat_convection + heat_radiation - solar_heat_gain
            if abs(calculated_loss - total_heat_loss) > 0.1:
                validation_results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="Inconsistencia en el balance de calor",
                    field="total_heat_loss"
                ))
        
        # Validar resistencia
        resistance = results.get('resistance_at_temp')
        if resistance is not None:
            if resistance <= 0:
                validation_results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="La resistencia debe ser positiva",
                    field="resistance_at_temp"
                ))
            elif resistance > 10:
                validation_results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message="Resistencia muy alta",
                    field="resistance_at_temp"
                ))
        
        return validation_results
    
    def comprehensive_validation(self, conductor_params: Dict, 
                              environmental_params: Dict,
                              calculation_results: Dict = None) -> Tuple[bool, List[ValidationResult]]:
        """Validación completa de todos los parámetros"""
        all_results = []
        
        # Validar conductor
        conductor_results = self.validate_conductor_parameters(conductor_params)
        all_results.extend(conductor_results)
        
        # Validar parámetros ambientales
        env_results = self.validate_environmental_parameters(environmental_params)
        all_results.extend(env_results)
        
        # Validar resultados del cálculo (si se proporcionan)
        if calculation_results:
            calc_results = self.validate_calculation_results(calculation_results)
            all_results.extend(calc_results)
        
        # Determinar si la validación es exitosa
        has_errors = any(r.level == ValidationLevel.ERROR for r in all_results)
        has_critical = any(r.level == ValidationLevel.CRITICAL for r in all_results)
        
        is_valid = not (has_errors or has_critical)
        
        # Registrar resultados
        for result in all_results:
            if result.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
                self.logger.error(f"Validation error: {result.message}")
            elif result.level == ValidationLevel.WARNING:
                self.logger.warning(f"Validation warning: {result.message}")
            else:
                self.logger.info(f"Validation info: {result.message}")
        
        return is_valid, all_results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict:
        """Obtener resumen de validación"""
        summary = {
            'total': len(results),
            'valid': 0,
            'warnings': 0,
            'errors': 0,
            'critical': 0,
            'messages_by_level': {
                'info': [],
                'warning': [],
                'error': [],
                'critical': []
            }
        }
        
        for result in results:
            if result.is_valid:
                summary['valid'] += 1
            
            level = result.level.value
            summary[level + 's'] += 1
            summary['messages_by_level'][level].append({
                'message': result.message,
                'field': result.field,
                'suggested_value': result.suggested_value
            })
        
        return summary


def safe_calculate_ampacity(calculator, conductor_params, environmental_params):
    """
    Función wrapper para cálculo seguro con manejo de excepciones
    """
    validator = AmpacityValidator()
    
    try:
        # Validar parámetros antes del cálculo
        is_valid, validation_results = validator.comprehensive_validation(
            conductor_params, environmental_params
        )
        
        if not is_valid:
            error_messages = [r.message for r in validation_results 
                            if r.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]]
            raise ValidationException(
                f"Parámetros inválidos: {'; '.join(error_messages)}",
                validation_results
            )
        
        # Realizar cálculo
        results = calculator.calculate_ampacity(conductor_params, environmental_params)
        
        # Validar resultados
        calc_validation = validator.validate_calculation_results(results)
        validation_results.extend(calc_validation)
        
        # Agregar resultados de validación a los resultados del cálculo
        results['validation_results'] = validation_results
        results['validation_summary'] = validator.get_validation_summary(validation_results)
        
        return results
        
    except ValidationException:
        raise
    except Exception as e:
        # Capturar errores inesperados
        error_msg = f"Error en cálculo de ampacidad: {str(e)}"
        validator.logger.error(f"{error_msg}\n{traceback.format_exc()}")
        
        raise ValidationException(error_msg)


if __name__ == "__main__":
    # Ejemplo de uso
    validator = AmpacityValidator()
    
    # Datos de prueba
    test_conductor = {
        'name': 'Test Conductor',
        'type': 'ACSR',
        'diameter': 20.0,
        'area': 200.0,
        'rdc_20': 0.15,
        'alpha': 0.004,
        'beta': 0.0001,
        'weight': 1.0,
        'max_temp': 75.0
    }
    
    test_environment = {
        'ambient_temperature': 40.0,
        'conductor_temperature_limit': 75.0,
        'altitude': 100.0,
        'wind_speed': 1.0,
        'solar_radiation': 1000.0,
        'emissivity': 0.8,
        'absorptivity': 0.8
    }
    
    # Validar
    is_valid, results = validator.comprehensive_validation(
        test_conductor, test_environment
    )
    
    print(f"Validación exitosa: {is_valid}")
    print("Resultados:")
    for result in results:
        print(f"  [{result.level.value.upper()}] {result.field}: {result.message}")
    
    # Resumen
    summary = validator.get_validation_summary(results)
    print(f"\nResumen: {summary}")
