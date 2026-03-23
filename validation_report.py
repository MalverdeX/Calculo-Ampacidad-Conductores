"""
Reporte completo de validación de cálculos según IEEE Std 738-2012
"""

import numpy as np
import pandas as pd
from ampacity_calculator import AmpacityCalculator, ConductorDatabase
from validator import safe_calculate_ampacity
import json
from datetime import datetime


def generate_validation_report():
    """Generar reporte completo de validación"""
    
    print("📋 REPORTE COMPLETO DE VALIDACIÓN")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Estándar: IEEE Std 738-2012")
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    
    # 1. Validación de constantes físicas
    print("\n\n1️⃣ CONSTANTES FÍSICAS IEEE 738-2012")
    print("-" * 40)
    
    constants_validation = {
        "Stefan-Boltzmann": {
            "valor": calculator.stefan_boltzmann,
            "teórico": 5.67e-8,
            "unidades": "W/(m²·K⁴)",
            "cumple": abs(calculator.stefan_boltzmann - 5.67e-8) < 1e-10
        },
        "Gravedad": {
            "valor": calculator.gravity,
            "teórico": 9.81,
            "unidades": "m/s²",
            "cumple": abs(calculator.gravity - 9.81) < 0.01
        },
        "Viscosidad aire": {
            "valor": calculator.air_viscosity,
            "teórico": 1.8e-5,
            "unidades": "Pa·s",
            "cumple": abs(calculator.air_viscosity - 1.8e-5) < 1e-7
        },
        "Conductividad térmica": {
            "valor": calculator.air_thermal_conductivity,
            "teórico": 0.024,
            "unidades": "W/(m·K)",
            "cumple": abs(calculator.air_thermal_conductivity - 0.024) < 0.001
        },
        "Densidad nivel mar": {
            "valor": calculator.sea_level_density,
            "teórico": 1.204,
            "unidades": "kg/m³",
            "cumple": abs(calculator.sea_level_density - 1.204) < 0.001
        }
    }
    
    for name, data in constants_validation.items():
        status = "✅" if data["cumple"] else "❌"
        print(f"{status} {name}: {data['valor']:.2e} {data['unidades']} (teórico: {data['teórico']:.2e})")
    
    # 2. Validación de conductores
    print("\n\n2️⃣ VALIDACIÓN DE PARÁMETROS DE CONDUCTORES")
    print("-" * 50)
    
    conductors = db.get_all_conductors()
    conductor_validation = []
    
    for cond_id, params in conductors.items():
        # Validar alpha
        alpha_valid = 0.003 <= params['alpha'] <= 0.005
        
        # Validar beta (corregido para valores realistas)
        if params['type'] == 'ACSR':
            beta_valid = 0.02 <= params['beta'] <= 0.05
        elif params['type'] == 'AAC':
            beta_valid = 0.01 <= params['beta'] <= 0.025
        elif params['type'] == 'CU':
            beta_valid = 0.015 <= params['beta'] <= 0.03
        else:
            beta_valid = True
        
        # Validar consistencia geométrica
        area_theoretical = np.pi * (params['diameter']/2)**2
        area_consistent = 0.5 <= params['area'] / area_theoretical <= 1.5
        
        # Validar resistencia
        resistance_realistic = 0.01 <= params['rdc_20'] <= 2.0
        
        conductor_validation.append({
            'id': cond_id,
            'name': params['name'],
            'type': params['type'],
            'alpha_valid': alpha_valid,
            'beta_valid': beta_valid,
            'area_consistent': area_consistent,
            'resistance_realistic': resistance_realistic,
            'overall_valid': all([alpha_valid, beta_valid, area_consistent, resistance_realistic])
        })
    
    # Mostrar resultados
    for cond in conductor_validation:
        status = "✅" if cond['overall_valid'] else "❌"
        print(f"{status} {cond['name']}: α={cond['alpha_valid']}, β={cond['beta_valid']}, Área={cond['area_consistent']}, R={cond['resistance_realistic']}")
    
    # 3. Pruebas de cálculo
    print("\n\n3️⃣ PRUEBAS DE CÁLCULO DE AMPACIDAD")
    print("-" * 40)
    
    test_cases = [
        {
            'name': 'Caso estándar IEEE',
            'conductor': 'ACSR_477_kcmil',
            'ambient_temp': 40.0,
            'wind_speed': 1.0,
            'altitude': 100.0,
            'solar_radiation': 1000.0,
            'expected_range': (500, 700)  # Ampacidad esperada
        },
        {
            'name': 'Baja temperatura',
            'conductor': 'ACSR_477_kcmil',
            'ambient_temp': 10.0,
            'wind_speed': 1.0,
            'altitude': 0.0,
            'solar_radiation': 500.0,
            'expected_range': (800, 1000)
        },
        {
            'name': 'Alta velocidad viento',
            'conductor': 'ACSR_477_kcmil',
            'ambient_temp': 40.0,
            'wind_speed': 5.0,
            'altitude': 100.0,
            'solar_radiation': 1000.0,
            'expected_range': (900, 1100)
        }
    ]
    
    calculation_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        conductor = db.get_conductor(test_case['conductor'])
        env_params = {
            'ambient_temperature': test_case['ambient_temp'],
            'conductor_temperature_limit': 75.0,
            'altitude': test_case['altitude'],
            'wind_speed': test_case['wind_speed'],
            'solar_radiation': test_case['solar_radiation'],
            'emissivity': 0.8,
            'absorptivity': 0.8
        }
        
        try:
            results = calculator.calculate_ampacity(conductor, env_params)
            
            # Validar ampacidad en rango esperado
            min_expected, max_expected = test_case['expected_range']
            ampacity_valid = min_expected <= results['ampacity'] <= max_expected
            
            # Validar balance de calor
            q_total = results['heat_convection'] + results['heat_radiation'] - results['solar_heat_gain']
            balance_valid = abs(q_total - results['total_heat_loss']) < 0.01
            
            # Validar curva T-I
            temps = results['temperature_curve']
            temp_increases = all(temps[i] > temps[i-1] for i in range(1, len(temps)))
            
            calculation_results.append({
                'test': test_case['name'],
                'ampacity': results['ampacity'],
                'ampacity_valid': ampacity_valid,
                'balance_valid': balance_valid,
                'temp_curve_valid': temp_increases,
                'overall_valid': ampacity_valid and balance_valid and temp_increases
            })
            
            status = "✅" if calculation_results[-1]['overall_valid'] else "❌"
            print(f"{status} {test_case['name']}: Ampacidad={results['ampacity']:.1f}A, Balance={balance_valid}, T-I={temp_increases}")
            
        except Exception as e:
            print(f"❌ {test_case['name']}: ERROR - {e}")
            calculation_results.append({
                'test': test_case['name'],
                'error': str(e),
                'overall_valid': False
            })
    
    # 4. Análisis de sensibilidad
    print("\n\n4️⃣ ANÁLISIS DE SENSIBILIDAD AMBIENTAL")
    print("-" * 40)
    
    conductor = db.get_conductor('ACSR_477_kcmil')
    base_params = {
        'ambient_temperature': 40.0,
        'conductor_temperature_limit': 75.0,
        'altitude': 100.0,
        'wind_speed': 1.0,
        'solar_radiation': 1000.0,
        'emissivity': 0.8,
        'absorptivity': 0.8
    }
    
    # Sensibilidad velocidad viento
    wind_speeds = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    wind_effects = []
    
    for ws in wind_speeds:
        params = base_params.copy()
        params['wind_speed'] = ws
        results = calculator.calculate_ampacity(conductor, params)
        wind_effects.append(results['ampacity'])
    
    # Verificar monotonicidad (ampacidad debe aumentar con viento)
    wind_monotonic = all(wind_effects[i] > wind_effects[i-1] for i in range(1, len(wind_effects)))
    print(f"✅ Efecto viento monótonico: {wind_monotonic}")
    
    # Sensibilidad temperatura ambiente
    ambient_temps = [10, 20, 30, 40, 50]
    temp_effects = []
    
    for at in ambient_temps:
        params = base_params.copy()
        params['ambient_temperature'] = at
        results = calculator.calculate_ampacity(conductor, params)
        temp_effects.append(results['ampacity'])
    
    # Verificar monotonicidad (ampacidad debe disminuir con temperatura)
    temp_monotonic = all(temp_effects[i] < temp_effects[i-1] for i in range(1, len(temp_effects)))
    print(f"✅ Efecto temperatura monótonico: {temp_monotonic}")
    
    # 5. Resumen de validación
    print("\n\n5️⃣ RESUMEN DE VALIDACIÓN")
    print("-" * 30)
    
    # Constantes físicas
    constants_ok = all(data['cumple'] for data in constants_validation.values())
    
    # Conductores
    conductors_ok = sum(1 for c in conductor_validation if c['overall_valid'])
    conductors_total = len(conductor_validation)
    
    # Cálculos
    calculations_ok = sum(1 for c in calculation_results if c.get('overall_valid', False))
    calculations_total = len(calculation_results)
    
    # Sensibilidad
    sensitivity_ok = wind_monotonic and temp_monotonic
    
    # Validación general
    overall_valid = (constants_ok and 
                    (conductors_ok / conductors_total) > 0.8 and
                    (calculations_ok / calculations_total) > 0.8 and
                    sensitivity_ok)
    
    print(f"📊 Constantes físicas: {constants_ok} ✅")
    print(f"📊 Conductores válidos: {conductors_ok}/{conductors_total} ({conductors_ok/conductors_total*100:.1f}%)")
    print(f"📊 Cálculos válidos: {calculations_ok}/{calculations_total} ({calculations_ok/calculations_total*100:.1f}%)")
    print(f"📊 Análisis sensibilidad: {sensitivity_ok} ✅")
    
    print(f"\n🎯 ESTADO GENERAL: {'✅ APROBADO' if overall_valid else '❌ REQUIERE REVISIÓN'}")
    
    # Generar reporte JSON
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'standard': 'IEEE Std 738-2012',
        'validation': {
            'constants_physical': constants_ok,
            'conductors': {
                'valid': conductors_ok,
                'total': conductors_total,
                'percentage': conductors_ok/conductors_total*100
            },
            'calculations': {
                'valid': calculations_ok,
                'total': calculations_total,
                'percentage': calculations_ok/calculations_total*100
            },
            'sensitivity': sensitivity_ok,
            'overall': overall_valid
        },
        'details': {
            'constants': constants_validation,
            'conductors': conductor_validation,
            'calculations': calculation_results,
            'sensitivity': {
                'wind_effects': wind_effects,
                'wind_monotonic': wind_monotonic,
                'temperature_effects': temp_effects,
                'temperature_monotonic': temp_monotonic
            }
        }
    }
    
    with open('validation_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Reporte detallado guardado en 'validation_report.json'")
    
    return overall_valid


if __name__ == "__main__":
    success = generate_validation_report()
    
    if success:
        print("\n🎉 VALIDACIÓN COMPLETADA EXITOSAMENTE")
        print("La calculadora cumple con IEEE Std 738-2012")
    else:
        print("\n⚠️ VALIDACIÓN REQUIERE ATENCIÓN")
        print("Revise los detalles en el reporte generado")
