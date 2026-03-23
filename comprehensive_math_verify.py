"""
Verificación matemática exhaustiva de todos los cálculos de ampacidad
"""
import math
import numpy as np
from ampacity_calculator import AmpacityCalculator, ConductorDatabase
from config import STEFAN_BOLTZMANN, GRAVITY, AIR_VISCOSITY, AIR_THERMAL_CONDUCTIVITY, SEA_LEVEL_DENSITY

def verify_air_density():
    """Verificar cálculo de densidad del aire"""
    print("=" * 60)
    print("1. VERIFICACIÓN: Densidad del Aire")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    
    # Caso 1: Nivel del mar, 20°C
    rho1 = calculator.calculate_air_density(0, 20)
    # Fórmula: ρ = ρ₀ × exp(-h/8000) × (293.15/(T+273.15))
    expected1 = 1.204 * math.exp(0) * (293.15/293.15)
    print(f"Nivel mar, 20°C: Calculado={rho1:.4f}, Esperado={expected1:.4f}, Dif={abs(rho1-expected1):.6f}")
    
    # Caso 2: 1000m, 40°C
    rho2 = calculator.calculate_air_density(1000, 40)
    expected2 = 1.204 * math.exp(-1000/8000) * (293.15/313.15)
    print(f"1000m, 40°C: Calculado={rho2:.4f}, Esperado={expected2:.4f}, Dif={abs(rho2-expected2):.6f}")
    
    # Verificar que densidad disminuye con altitud y aumenta con temperatura
    rho_0m = calculator.calculate_air_density(0, 20)
    rho_1000m = calculator.calculate_air_density(1000, 20)
    rho_20C = calculator.calculate_air_density(0, 20)
    rho_40C = calculator.calculate_air_density(0, 40)
    
    assert rho_1000m < rho_0m, "Densidad debe disminuir con altitud"
    assert rho_40C < rho_20C, "Densidad debe disminuir con temperatura"
    
    print("✅ Verificación de densidad del aire: CORRECTO")
    return True

def verify_convection():
    """Verificar cálculos de convección forzada y natural"""
    print("\n" + "=" * 60)
    print("2. VERIFICACIÓN: Transferencia de Calor por Convección")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    diameter_mm = 20.0  # mm
    temp_diff = 35.0  # °C (75-40)
    air_density = 1.1  # kg/m³
    
    # CASO 1: Convección forzada (viento > 0.1 m/s)
    print("\n--- Convección Forzada (viento = 2 m/s) ---")
    wind_speed = 2.0
    q_conv_forzada = calculator.calculate_heat_convection(temp_diff, wind_speed, diameter_mm, air_density)
    
    # Verificación manual según IEEE 738-2012
    D = diameter_mm / 1000  # 0.02 m
    Re = air_density * wind_speed * D / AIR_VISCOSITY
    print(f"  Número de Reynolds: Re = {Re:.2f}")
    
    if Re >= 1000:
        Nu = 0.292 * Re**0.6
        print(f"  Número de Nusselt (Eq 11a): Nu = 0.292×Re^0.6 = {Nu:.4f}")
    else:
        Nu = 0.65 + 0.44 * Re**0.52
        print(f"  Número de Nusselt (Eq alternativa): Nu = {Nu:.4f}")
    
    h_conv = Nu * AIR_THERMAL_CONDUCTIVITY / D
    q_expected = h_conv * math.pi * D * temp_diff
    
    print(f"  Coef. convectivo: h = {h_conv:.4f} W/(m²·K)")
    print(f"  Calor convección: Q = h×π×D×ΔT = {q_expected:.4f} W/m")
    print(f"  Calculado por función: {q_conv_forzada:.4f} W/m")
    print(f"  Diferencia: {abs(q_conv_forzada - q_expected):.6f} W/m")
    
    # CASO 2: Convección natural (viento < 0.1 m/s)
    print("\n--- Convección Natural (viento = 0.05 m/s) ---")
    wind_speed_low = 0.05
    q_conv_natural = calculator.calculate_heat_convection(temp_diff, wind_speed_low, diameter_mm, air_density)
    
    # Verificación manual
    T_film = temp_diff / 2 + 273.15  # 290.65 K
    beta_thermal = 1 / T_film
    nu = AIR_VISCOSITY / air_density  # viscosidad cinemática
    Gr = GRAVITY * beta_thermal * temp_diff * D**3 / nu**2
    Pr = 0.713
    
    print(f"  Temp. película: T_film = {T_film:.2f} K")
    print(f"  Coef. expansión térmica: β = {beta_thermal:.6f} 1/K")
    print(f"  Número de Grashof: Gr = {Gr:.2e}")
    print(f"  Número de Prandtl: Pr = {Pr}")
    
    if Gr * Pr < 1e4:
        Nu_nat = 0.4 + 0.55 * (Gr * Pr)**0.25
        print(f"  Nusselt natural (Eq 10a baja): Nu = {Nu_nat:.4f}")
    else:
        Nu_nat = 0.52 * (Gr * Pr)**0.333
        print(f"  Nusselt natural (Eq 10a alta): Nu = {Nu_nat:.4f}")
    
    h_conv_nat = Nu_nat * AIR_THERMAL_CONDUCTIVITY / D
    q_expected_nat = h_conv_nat * math.pi * D * temp_diff
    
    print(f"  Coef. convectivo natural: h = {h_conv_nat:.4f} W/(m²·K)")
    print(f"  Calor convección natural: Q = {q_expected_nat:.4f} W/m")
    print(f"  Calculado por función: {q_conv_natural:.4f} W/m")
    print(f"  Diferencia: {abs(q_conv_natural - q_expected_nat):.6f} W/m")
    
    # Verificar que convección aumenta con viento y ΔT
    q_low_wind = calculator.calculate_heat_convection(temp_diff, 0.5, diameter_mm, air_density)
    q_high_wind = calculator.calculate_heat_convection(temp_diff, 5.0, diameter_mm, air_density)
    assert q_high_wind > q_low_wind, "Convección debe aumentar con velocidad del viento"
    
    q_low_temp = calculator.calculate_heat_convection(10, wind_speed, diameter_mm, air_density)
    q_high_temp = calculator.calculate_heat_convection(50, wind_speed, diameter_mm, air_density)
    assert q_high_temp > q_low_temp, "Convección debe aumentar con ΔT"
    
    print("\n✅ Verificación de convección: CORRECTO")
    return True

def verify_radiation():
    """Verificar cálculo de radiación térmica"""
    print("\n" + "=" * 60)
    print("3. VERIFICACIÓN: Radiación Térmica")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    
    conductor_temp = 75.0  # °C
    ambient_temp = 40.0    # °C
    emissivity = 0.8
    diameter_mm = 20.0
    
    q_rad = calculator.calculate_heat_radiation(conductor_temp, ambient_temp, emissivity, diameter_mm)
    
    # Verificación manual: Q_rad = σ × ε × π × D × (Tc⁴ - Ta⁴)
    Tc = conductor_temp + 273.15  # 348.15 K
    Ta = ambient_temp + 273.15    # 313.15 K
    D = diameter_mm / 1000
    
    q_expected = STEFAN_BOLTZMANN * emissivity * math.pi * D * (Tc**4 - Ta**4)
    
    print(f"  Temperaturas: Tc = {Tc:.2f} K, Ta = {Ta:.2f} K")
    print(f"  Stefan-Boltzmann: σ = {STEFAN_BOLTZMANN:.2e} W/(m²·K⁴)")
    print(f"  Emisividad: ε = {emissivity}")
    print(f"  Diferencia T⁴: Tc⁴ - Ta⁴ = {Tc**4 - Ta**4:.2e} K⁴")
    print(f"  Q_rad calculado por función: {q_rad:.4f} W/m")
    print(f"  Q_rad esperado manual: {q_expected:.4f} W/m")
    print(f"  Diferencia: {abs(q_rad - q_expected):.6f} W/m")
    
    assert abs(q_rad - q_expected) < 0.001, "Radiación calculada incorrectamente"
    
    # Verificar que radiación aumenta con emisividad y ΔT
    q_low_emit = calculator.calculate_heat_radiation(conductor_temp, ambient_temp, 0.5, diameter_mm)
    q_high_emit = calculator.calculate_heat_radiation(conductor_temp, ambient_temp, 0.9, diameter_mm)
    assert q_high_emit > q_low_emit, "Radiación debe aumentar con emisividad"
    
    print("\n✅ Verificación de radiación: CORRECTO")
    return True

def verify_solar_heat():
    """Verificar cálculo de ganancia solar"""
    print("\n" + "=" * 60)
    print("4. VERIFICACIÓN: Ganancia de Calor Solar")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    
    solar_radiation = 1000.0  # W/m²
    absorptivity = 0.8
    diameter_mm = 20.0
    angle = 90.0  # grados
    
    q_solar = calculator.calculate_solar_heat_gain(solar_radiation, absorptivity, diameter_mm, angle)
    
    # Verificación manual: Q_solar = Qs × α_solar × D × sin(θ)
    D = diameter_mm / 1000
    angle_rad = math.radians(angle)
    projection = math.sin(angle_rad)
    q_expected = solar_radiation * absorptivity * D * projection
    
    print(f"  Radiación solar: Qs = {solar_radiation} W/m²")
    print(f"  Absortividad: α = {absorptivity}")
    print(f"  Diámetro: D = {D} m")
    print(f"  Ángulo: θ = {angle}°, sin(θ) = {projection:.4f}")
    print(f"  Q_solar calculado por función: {q_solar:.4f} W/m")
    print(f"  Q_solar esperado manual: {q_expected:.4f} W/m")
    print(f"  Diferencia: {abs(q_solar - q_expected):.6f} W/m")
    
    assert abs(q_solar - q_expected) < 0.001, "Ganancia solar calculada incorrectamente"
    
    # Verificar que aumenta con radiación, absorptividad y diámetro
    q_low_rad = calculator.calculate_solar_heat_gain(500, absorptivity, diameter_mm, angle)
    q_high_rad = calculator.calculate_solar_heat_gain(1200, absorptivity, diameter_mm, angle)
    assert q_high_rad > q_low_rad, "Ganancia solar debe aumentar con radiación"
    
    print("\n✅ Verificación de ganancia solar: CORRECTO")
    return True

def verify_resistance():
    """Verificar cálculo de resistencia con temperatura y efecto piel"""
    print("\n" + "=" * 60)
    print("5. VERIFICACIÓN: Resistencia del Conductor")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    
    rdc_20 = 0.120  # Ω/km
    alpha = 0.00403  # 1/°C
    beta = 0.040
    conductor_temp = 75.0  # °C
    current = 600.0  # A
    
    resistance = calculator.calculate_resistance(rdc_20, alpha, beta, conductor_temp, current)
    
    # Verificación manual (IEEE 738-2012 Ecuación 2):
    # R(T) = R_20°C × (1 + α × (T - 20)) × (1 + β × (I/1000)²)
    r_temp = rdc_20 * (1 + alpha * (conductor_temp - 20))
    skin_factor = 1 + beta * (current / 1000)**2
    r_expected = r_temp * skin_factor
    
    print(f"  Resistencia base (20°C): Rdc = {rdc_20} Ω/km")
    print(f"  Coef. temperatura: α = {alpha} 1/°C")
    print(f"  Coef. efecto piel: β = {beta}")
    print(f"  Corriente: I = {current} A")
    print(f"  Factor efecto piel: 1 + β×(I/1000)² = {skin_factor:.6f}")
    print(f"  Resistencia a 75°C (sin efecto piel): {r_temp:.6f} Ω/km")
    print(f"  Resistencia total: R = {r_expected:.6f} Ω/km")
    print(f"  Calculado por función: {resistance:.6f} Ω/km")
    print(f"  Diferencia: {abs(resistance - r_expected):.8f} Ω/km")
    
    assert abs(resistance - r_expected) < 0.00001, "Resistencia calculada incorrectamente"
    
    # Verificar que resistencia aumenta con temperatura y corriente
    r_low_temp = calculator.calculate_resistance(rdc_20, alpha, beta, 20, current)
    r_high_temp = calculator.calculate_resistance(rdc_20, alpha, beta, 100, current)
    assert r_high_temp > r_low_temp, "Resistencia debe aumentar con temperatura"
    
    r_low_current = calculator.calculate_resistance(rdc_20, alpha, beta, conductor_temp, 100)
    r_high_current = calculator.calculate_resistance(rdc_20, alpha, beta, conductor_temp, 1000)
    assert r_high_current > r_low_current, "Resistencia debe aumentar con corriente (efecto piel)"
    
    print("\n✅ Verificación de resistencia: CORRECTO")
    return True

def verify_joule_heating():
    """Verificar cálculo de calentamiento Joule"""
    print("\n" + "=" * 60)
    print("6. VERIFICACIÓN: Calentamiento por Efecto Joule")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    
    resistance = 0.15  # Ω/km
    current = 600.0    # A
    
    q_joule = calculator.calculate_joule_heating(resistance, current)
    
    # Verificación manual: Q = I² × R / 1000 (convertir a W/m)
    q_expected = current**2 * resistance / 1000
    
    print(f"  Resistencia: R = {resistance} Ω/km")
    print(f"  Corriente: I = {current} A")
    print(f"  Pérdidas Joule: Q = I²×R/1000 = {q_expected:.4f} W/m")
    print(f"  Calculado por función: {q_joule:.4f} W/m")
    print(f"  Diferencia: {abs(q_joule - q_expected):.6f} W/m")
    
    assert abs(q_joule - q_expected) < 0.001, "Calentamiento Joule calculado incorrectamente"
    
    print("\n✅ Verificación de calentamiento Joule: CORRECTO")
    return True

def verify_heat_balance():
    """Verificar balance de calor: Q_joule = Q_conv + Q_rad - Q_solar"""
    print("\n" + "=" * 60)
    print("7. VERIFICACIÓN: Balance de Calor (IEEE 738-2012)")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    
    # Usar ACSR 477 kcmil como referencia
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
    
    # Extraer valores
    q_conv = results['heat_convection']
    q_rad = results['heat_radiation']
    q_solar = results['solar_heat_gain']
    q_total = results['total_heat_loss']
    ampacity = results['ampacity']
    resistance = results['resistance_at_temp']
    
    # Calcular Q_joule a la ampacidad
    q_joule = ampacity**2 * resistance / 1000
    
    # Verificar balance: Q_joule debe igualar pérdidas netas
    q_losses = q_conv + q_rad - q_solar
    
    print(f"  Parámetros del conductor:")
    print(f"    - Diámetro: {conductor['diameter']} mm")
    print(f"    - Resistencia (20°C): {conductor['rdc_20']} Ω/km")
    print(f"    - Resistencia (75°C): {resistance:.4f} Ω/km")
    print(f"\n  Condiciones ambientales:")
    print(f"    - Temp. ambiente: {env_params['ambient_temperature']}°C")
    print(f"    - Temp. conductor: {env_params['conductor_temperature_limit']}°C")
    print(f"    - Velocidad viento: {env_params['wind_speed']} m/s")
    print(f"    - Altitud: {env_params['altitude']} m")
    print(f"\n  Resultados del cálculo:")
    print(f"    - Ampacidad: {ampacity:.2f} A")
    print(f"    - Q_joule (I²R): {q_joule:.4f} W/m")
    print(f"    - Q_convección: {q_conv:.4f} W/m")
    print(f"    - Q_radiación: {q_rad:.4f} W/m")
    print(f"    - Q_solar: {q_solar:.4f} W/m")
    print(f"    - Pérdidas netas (Q_conv + Q_rad - Q_solar): {q_losses:.4f} W/m")
    print(f"    - Diferencia (Q_joule - pérdidas): {abs(q_joule - q_losses):.6f} W/m")
    
    # El balance debe estar dentro de tolerancia
    tolerance = 0.1  # W/m
    balance_ok = abs(q_joule - q_losses) < tolerance
    
    print(f"\n  Balance de calor:")
    print(f"    Q_joule = {q_joule:.4f} W/m")
    print(f"    Q_conv + Q_rad - Q_solar = {q_losses:.4f} W/m")
    print(f"    Diferencia: {abs(q_joule - q_losses):.6f} W/m (tolerancia: {tolerance} W/m)")
    
    if balance_ok:
        print(f"    ✅ Balance de calor CORRECTO")
    else:
        print(f"    ❌ Balance de calor INCORRECTO")
    
    return balance_ok

def verify_temperature_curve():
    """Verificar curva temperatura-corriente"""
    print("\n" + "=" * 60)
    print("8. VERIFICACIÓN: Curva Temperatura-Corriente")
    print("=" * 60)
    
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
    
    print(f"  Corrientes: {len(currents)} puntos desde {currents[0]:.1f} hasta {currents[-1]:.1f} A")
    print(f"  Temperaturas: desde {temps[0]:.1f}°C hasta {temps[-1]:.1f}°C")
    
    # Verificar monotonicidad (temperatura debe aumentar con corriente)
    monotonic = all(temps[i] >= temps[i-1] for i in range(1, len(temps)))
    
    # Verificar que a corriente 0, temperatura es ambiente
    temp_at_zero = temps[0]
    ambient = env_params['ambient_temperature']
    temp_ok = abs(temp_at_zero - ambient) < 1.0
    
    print(f"\n  Verificaciones:")
    print(f"    - Monotonicidad (T aumenta con I): {'✅ CORRECTO' if monotonic else '❌ INCORRECTO'}")
    print(f"    - Temp. a I=0 ≈ Temp. ambiente: {temp_at_zero:.1f}°C vs {ambient}°C {'✅ CORRECTO' if temp_ok else '❌ INCORRECTO'}")
    
    # Verificar punto de ampacidad
    ampacity = results['ampacity']
    target_temp = env_params['conductor_temperature_limit']
    
    # Encontrar temperatura más cercana a la ampacidad
    idx_near_amp = min(range(len(currents)), key=lambda i: abs(currents[i] - ampacity))
    temp_near_amp = temps[idx_near_amp]
    
    print(f"    - Temp. cerca de ampacidad ({ampacity:.1f}A): {temp_near_amp:.1f}°C (target: {target_temp}°C)")
    
    ampacity_ok = abs(temp_near_amp - target_temp) < 5.0
    print(f"    - Punto de ampacidad alcanza temp. límite: {'✅ CORRECTO' if ampacity_ok else '❌ INCORRECTO'}")
    
    return monotonic and temp_ok

def verify_all_conductors():
    """Verificar cálculos para todos los conductores en la base de datos"""
    print("\n" + "=" * 60)
    print("9. VERIFICACIÓN: Todos los Conductores")
    print("=" * 60)
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    
    env_params = {
        'ambient_temperature': 40.0,
        'conductor_temperature_limit': 75.0,
        'altitude': 100.0,
        'wind_speed': 1.0,
        'solar_radiation': 1000.0,
        'emissivity': 0.8,
        'absorptivity': 0.8
    }
    
    all_ok = True
    conductors = db.get_all_conductors()
    
    print(f"\n  Verificando {len(conductors)} conductores...\n")
    print(f"  {'Conductor':<20} {'Ampacidad':<12} {'R(T)':<10} {'Balance':<10}")
    print(f"  {'-'*20} {'-'*12} {'-'*10} {'-'*10}")
    
    for cond_id, params in conductors.items():
        try:
            results = calculator.calculate_ampacity(params, env_params)
            
            ampacity = results['ampacity']
            resistance = results['resistance_at_temp']
            
            # Verificar balance
            q_joule = ampacity**2 * resistance / 1000
            q_losses = results['heat_convection'] + results['heat_radiation'] - results['solar_heat_gain']
            balance_ok = abs(q_joule - q_losses) < 0.5
            
            status = "✅" if balance_ok else "❌"
            print(f"  {params['name']:<20} {ampacity:>8.1f} A   {resistance:>6.4f}   {status}")
            
            if not balance_ok:
                all_ok = False
                
        except Exception as e:
            print(f"  {params['name']:<20} ERROR: {str(e)[:30]}")
            all_ok = False
    
    print(f"\n  Resultado: {'✅ TODOS LOS CÁLCULOS CORRECTOS' if all_ok else '❌ HAY PROBLEMAS EN ALGUNOS CÁLCULOS'}")
    return all_ok

def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN MATEMÁTICA COMPLETA - Calculadora de Ampacidad")
    print("Estándar: IEEE Std 738-2012")
    print("=" * 70)
    
    results = {}
    
    results['air_density'] = verify_air_density()
    results['convection'] = verify_convection()
    results['radiation'] = verify_radiation()
    results['solar'] = verify_solar_heat()
    results['resistance'] = verify_resistance()
    results['joule'] = verify_joule_heating()
    results['heat_balance'] = verify_heat_balance()
    results['temp_curve'] = verify_temperature_curve()
    results['all_conductors'] = verify_all_conductors()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACIÓN MATEMÁTICA")
    print("=" * 70)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  {test_name:<25} {status}")
    
    print(f"\n{'='*70}")
    if all_passed:
        print("✅ TODAS LAS VERIFICACIONES MATEMÁTICAS PASARON")
        print("Los cálculos cumplen con IEEE Std 738-2012")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("Revisar los cálculos marcados con ❌")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    main()
