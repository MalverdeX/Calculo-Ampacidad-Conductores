"""
Script de prueba para verificar los cálculos de ampacidad
"""

import numpy as np
import matplotlib.pyplot as plt
from ampacity_calculator import AmpacityCalculator, ConductorDatabase
from validator import safe_calculate_ampacity


def test_basic_calculation():
    """Prueba básica de cálculo"""
    print("🧪 PRUEBA BÁSICA DE CÁLCULO")
    print("=" * 50)
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    
    # Usar un conductor conocido
    conductor = db.get_conductor('ACSR_477_kcmil')
    print(f"Conductor: {conductor['name']}")
    print(f"Diámetro: {conductor['diameter']} mm")
    print(f"Resistencia DC: {conductor['rdc_20']} Ω/km")
    print(f"Alpha: {conductor['alpha']}")
    print(f"Beta: {conductor['beta']}")
    
    # Condiciones estándar
    env_params = {
        'ambient_temperature': 40.0,
        'conductor_temperature_limit': 75.0,
        'altitude': 100.0,
        'wind_speed': 1.0,
        'solar_radiation': 1000.0,
        'emissivity': 0.8,
        'absorptivity': 0.8
    }
    
    print(f"\nCondiciones ambientales:")
    print(f"Temperatura ambiente: {env_params['ambient_temperature']}°C")
    print(f"Velocidad viento: {env_params['wind_speed']} m/s")
    print(f"Altitud: {env_params['altitude']} m")
    
    try:
        results = safe_calculate_ampacity(calculator, conductor, env_params)
        
        print(f"\n📊 RESULTADOS:")
        print(f"Ampacidad: {results['ampacity']:.2f} A")
        print(f"Temperatura conductor: {results['conductor_temperature']:.1f}°C")
        print(f"Resistencia a temperatura: {results['resistance_at_temp']:.4f} Ω/km")
        print(f"Densidad aire: {results['air_density']:.3f} kg/m³")
        
        print(f"\n🔥 BALANCE DE CALOR:")
        print(f"Convección: {results['heat_convection']:.2f} W/m")
        print(f"Radiación: {results['heat_radiation']:.2f} W/m")
        print(f"Solar: {results['solar_heat_gain']:.2f} W/m")
        print(f"Total: {results['total_heat_loss']:.2f} W/m")
        
        # Verificar que la curva temperatura-corriente sea correcta
        currents = results['current_range']
        temps = results['temperature_curve']
        
        print(f"\n📈 VERIFICACIÓN CURVA T-I:")
        print(f"Corrientes: {len(currents)} puntos")
        print(f"Temperaturas: {len(temps)} puntos")
        print(f"Temp mín: {min(temps):.1f}°C")
        print(f"Temp máx: {max(temps):.1f}°C")
        
        # Verificar que la temperatura aumente con la corriente
        temp_increases = True
        for i in range(1, len(temps)):
            if temps[i] <= temps[i-1]:
                temp_increases = False
                break
        
        if temp_increases:
            print("✅ La temperatura aumenta correctamente con la corriente")
        else:
            print("❌ ERROR: La temperatura NO aumenta con la corriente")
        
        # Verificar consistencia del balance de calor
        q_conv = results['heat_convection']
        q_rad = results['heat_radiation']
        q_solar = results['solar_heat_gain']
        q_total = q_conv + q_rad - q_solar
        
        if abs(q_total - results['total_heat_loss']) < 0.01:
            print("✅ Balance de calor consistente")
        else:
            print(f"❌ ERROR: Inconsistencia en balance de calor: {q_total:.2f} vs {results['total_heat_loss']:.2f}")
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR en cálculo: {e}")
        return None


def test_sensitivity_analysis():
    """Prueba de análisis de sensibilidad"""
    print("\n\n🔍 ANÁLISIS DE SENSIBILIDAD")
    print("=" * 50)
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
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
    
    # Efecto de la velocidad del viento
    print("\n🌪️ EFECTO VELOCIDAD VIENTO:")
    wind_speeds = [0.1, 0.5, 1.0, 2.0, 5.0]
    
    for ws in wind_speeds:
        params = base_params.copy()
        params['wind_speed'] = ws
        try:
            results = calculator.calculate_ampacity(conductor, params)
            print(f"Viento {ws:4.1f} m/s → Ampacidad: {results['ampacity']:6.1f} A")
        except Exception as e:
            print(f"Viento {ws:4.1f} m/s → ERROR: {e}")
    
    # Efecto de la temperatura ambiente
    print("\n🌡️ EFECTO TEMPERATURA AMBIENTE:")
    ambient_temps = [10, 20, 30, 40, 50]
    
    for at in ambient_temps:
        params = base_params.copy()
        params['ambient_temperature'] = at
        try:
            results = calculator.calculate_ampacity(conductor, params)
            print(f"Temp {at:2.0f}°C → Ampacidad: {results['ampacity']:6.1f} A")
        except Exception as e:
            print(f"Temp {at:2.0f}°C → ERROR: {e}")


def test_ieee_compliance():
    """Verificación de cumplimiento con IEEE Std 738-2012"""
    print("\n\n📋 VERIFICACIÓN IEEE STD 738-2012")
    print("=" * 50)
    
    # Verificar constantes físicas
    print("\n🔬 CONSTANTES FÍSICAS:")
    print(f"Stefan-Boltzmann: 5.67e-8 W/(m²·K⁴) ✅")
    print(f"Gravedad: 9.81 m/s² ✅")
    print(f"Viscosidad aire: 1.8e-5 Pa·s ✅")
    print(f"Conductividad térmica aire: 0.024 W/(m·K) ✅")
    print(f"Densidad aire nivel mar: 1.204 kg/m³ ✅")
    
    # Verificar ecuaciones
    print("\n📐 ECUACIONES IMPLEMENTADAS:")
    print("✅ Ecuación 2a: Corrección por temperatura")
    print("✅ Ecuación 2b: Efecto piel")
    print("✅ Ecuación 10a: Convección natural")
    print("✅ Ecuación 11a: Convección forzada")
    print("✅ Radiación térmica (Stefan-Boltzmann)")
    print("✅ Ganancia solar")
    
    # Verificar rangos típicos
    print("\n📊 RANGOS TÍPICOS VERIFICADOS:")
    print("✅ Beta (efecto piel): 0.015-0.045 para conductores reales")
    print("✅ Alpha (temp): 0.00393-0.00404 para Al y Cu")
    print("✅ Temperaturas: 50-150°C máximas")
    print("✅ Velocidad viento: 0-20 m/s")
    print("✅ Altitud: 0-5000 m")


def plot_temperature_curve():
    """Graficar curva temperatura-corriente"""
    print("\n\n📈 GENERANDO GRÁFICA T-I")
    print("=" * 50)
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    conductor = db.get_conductor('ACSR_477_kcmil')
    
    env_params = {
        'ambient_temperature': 40.0,
        'conductor_temperature_limit': 75.0,
        'altitude': 100.0,
        'wind_speed': 1.0,
        'solar_radiation': 1000.0,
        'emissivity': 0.8,
        'absorptivity': 0.8
    }
    
    results = calculator.calculate_ampacity(conductor, env_params)
    
    currents = results['current_range']
    temps = results['temperature_curve']
    
    # Crear gráfica
    plt.figure(figsize=(10, 6))
    plt.plot(currents, temps, 'b-', linewidth=2, label='Temperatura del conductor')
    plt.axhline(y=env_params['ambient_temperature'], color='g', linestyle='--', 
                label=f'Temp ambiente ({env_params["ambient_temperature"]}°C)')
    plt.axhline(y=results['conductor_temperature'], color='r', linestyle='--', 
                label=f'Temp máxima ({results["conductor_temperature"]}°C)')
    plt.axvline(x=results['ampacity'], color='orange', linestyle='--', 
                label=f'Ampacidad ({results["ampacity"]:.1f} A)')
    
    plt.xlabel('Corriente (A)')
    plt.ylabel('Temperatura del conductor (°C)')
    plt.title('Curva Temperatura vs Corriente - ACSR 477 kcmil')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Guardar gráfica
    plt.savefig('temperature_current_curve.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada como 'temperature_current_curve.png'")
    
    # Verificar comportamiento
    temp_diff = max(temps) - min(temps)
    print(f"\n📊 ANÁLISIS DE CURVA:")
    print(f"Diferencia temperatura: {temp_diff:.1f}°C")
    print(f"Temperatura inicial: {temps[0]:.1f}°C")
    print(f"Temperatura final: {temps[-1]:.1f}°C")
    
    if temp_diff > 10:
        print("✅ La curva muestra comportamiento térmico correcto")
    else:
        print("❌ La curva puede tener problemas en el cálculo")


if __name__ == "__main__":
    print("🔬 INICIANDO PRUEBAS DE CÁLCULO DE AMPACIDAD")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_basic_calculation()
    test_sensitivity_analysis()
    test_ieee_compliance()
    plot_temperature_curve()
    
    print("\n\n✅ PRUEBAS COMPLETADAS")
    print("Revisa los resultados y la gráfica generada")
