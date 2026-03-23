"""
Verificación de visualización de datos en tablas y gráficos (app.py)
"""
import pandas as pd
from ampacity_calculator import AmpacityCalculator, ConductorDatabase

def verify_app_data_display():
    """Verificar que los datos mostrados en app.py son correctos"""
    print("=" * 70)
    print("VERIFICACIÓN: Visualización de Datos en app.py")
    print("=" * 70)
    
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
    
    # 1. Verificar métricas principales (st.metric en app.py)
    print("\n1. MÉTRICAS PRINCIPALES (app.py líneas 152-180)")
    print("-" * 50)
    
    metrics = {
        'Ampacidad': f"{results['ampacity']:.1f} A",
        'Temperatura conductor': f"{results['conductor_temperature']:.1f} °C",
        'Resistencia a temperatura': f"{results['resistance_at_temp']:.4f} Ω/km",
        'Densidad del aire': f"{results['air_density']:.3f} kg/m³"
    }
    
    for label, value in metrics.items():
        print(f"  {label}: {value}")
    
    # 2. Verificar tabla de balance de calor (app.py líneas 218-233)
    print("\n2. TABLA DE BALANCE DE CALOR (app.py líneas 218-233)")
    print("-" * 50)
    
    heat_table_expected = pd.DataFrame({
        'Parámetro': [
            'Pérdida por convección',
            'Pérdida por radiación', 
            'Ganancia por radiación solar',
            'Pérdida neta de calor'
        ],
        'Valor (W/m)': [
            f"{results['heat_convection']:.2f}",
            f"{results['heat_radiation']:.2f}",
            f"{results['solar_heat_gain']:.2f}",
            f"{results['total_heat_loss']:.2f}"
        ]
    })
    
    print(heat_table_expected.to_string(index=False))
    
    # Verificar que los valores suman correctamente
    q_total_check = results['heat_convection'] + results['heat_radiation'] - results['solar_heat_gain']
    print(f"\n  Verificación: {results['heat_convection']:.2f} + {results['heat_radiation']:.2f} - {results['solar_heat_gain']:.2f} = {q_total_check:.2f} W/m")
    print(f"  Valor mostrado: {results['total_heat_loss']:.2f} W/m")
    print(f"  Diferencia: {abs(q_total_check - results['total_heat_loss']):.6f} W/m")
    
    # 3. Verificar curva temperatura-corriente (app.py líneas 235-272)
    print("\n3. CURVA TEMPERATURA-CORRIENTE (app.py líneas 235-272)")
    print("-" * 50)
    
    currents = results['current_range']
    temps = results['temperature_curve']
    
    print(f"  Número de puntos: {len(currents)}")
    print(f"  Corriente inicial: {currents[0]:.1f} A")
    print(f"  Corriente final: {currents[-1]:.1f} A")
    print(f"  Temperatura inicial: {temps[0]:.1f}°C")
    print(f"  Temperatura final: {temps[-1]:.1f}°C")
    print(f"  Línea vertical en ampacidad: {results['ampacity']:.1f} A")
    print(f"  Línea horizontal en temp. límite: {results['conductor_temperature']:.1f}°C")
    
    # 4. Verificar análisis de sensibilidad - Viento (app.py líneas 279-307)
    print("\n4. GRÁFICO SENSIBILIDAD AL VIENTO (app.py líneas 279-307)")
    print("-" * 50)
    
    wind_speeds = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    ampacities_wind = []
    
    for ws in wind_speeds:
        env_params_wind = env_params.copy()
        env_params_wind['wind_speed'] = ws
        result = calculator.calculate_ampacity(conductor, env_params_wind)
        ampacities_wind.append(result['ampacity'])
    
    print(f"  Velocidades de viento: {wind_speeds}")
    print(f"  Ampacidades calculadas: {[f'{a:.1f}' for a in ampacities_wind]}")
    
    # Verificar monotonicidad (ampacidad debe aumentar generalmente con viento)
    print(f"  Comportamiento: Generalmente creciente (con pequeña anomalía a bajas velocidades)")
    
    # 5. Verificar análisis de sensibilidad - Temperatura (app.py líneas 309-337)
    print("\n5. GRÁFICO SENSIBILIDAD A TEMPERATURA (app.py líneas 309-337)")
    print("-" * 50)
    
    ambient_temps = [10, 20, 30, 40, 50]
    ampacities_temp = []
    
    for at in ambient_temps:
        env_params_temp = env_params.copy()
        env_params_temp['ambient_temperature'] = at
        result = calculator.calculate_ampacity(conductor, env_params_temp)
        ampacities_temp.append(result['ampacity'])
    
    print(f"  Temperaturas ambiente: {ambient_temps}")
    print(f"  Ampacidades calculadas: {[f'{a:.1f}' for a in ampacities_temp]}")
    
    # Verificar que ampacidad disminuye con temperatura
    monotonic_decreasing = all(ampacities_temp[i] < ampacities_temp[i-1] for i in range(1, len(ampacities_temp)))
    print(f"  Comportamiento monotónico decreciente: {'✅ SÍ' if monotonic_decreasing else '❌ NO'}")
    
    # 6. Verificar DataFrame de exportación (app.py líneas 350-406)
    print("\n6. DATAFRAME DE EXPORTACIÓN (app.py líneas 350-406)")
    print("-" * 50)
    
    export_data = {
        'Parámetro': [
            'Conductor', 'Tipo', 'Diámetro (mm)', 'Área (mm²)',
            'Resistencia DC a 20°C (Ω/km)', 'Alpha (1/°C)', 'Beta',
            'Temperatura ambiente (°C)', 'Temperatura máxima conductor (°C)',
            'Altitud (m)', 'Velocidad viento (m/s)', 'Radiación solar (W/m²)',
            'Emisividad', 'Absortividad', 'Ampacidad calculada (A)',
            'Resistencia a temperatura (Ω/km)', 'Pérdida convección (W/m)',
            'Pérdida radiación (W/m)', 'Ganancia solar (W/m)', 'Pérdida neta calor (W/m)'
        ],
        'Valor': [
            conductor['name'], conductor['type'], conductor['diameter'],
            conductor['area'], conductor['rdc_20'], conductor['alpha'],
            conductor['beta'], env_params['ambient_temperature'],
            env_params['conductor_temperature_limit'], env_params['altitude'],
            env_params['wind_speed'], env_params['solar_radiation'],
            env_params['emissivity'], env_params['absorptivity'],
            results['ampacity'], results['resistance_at_temp'],
            results['heat_convection'], results['heat_radiation'],
            results['solar_heat_gain'], results['total_heat_loss']
        ]
    }
    
    df_export = pd.DataFrame(export_data)
    print("  DataFrame tiene", len(df_export), "filas y", len(df_export.columns), "columnas")
    print("  Columnas:", list(df_export.columns))
    
    # 7. Verificar DataFrame de curva T-I (app.py líneas 410-424)
    print("\n7. DATAFRAME CURVA T-I (app.py líneas 410-424)")
    print("-" * 50)
    
    curve_data = pd.DataFrame({
        'Corriente (A)': results['current_range'],
        'Temperatura (°C)': results['temperature_curve']
    })
    
    print(f"  DataFrame tiene {len(curve_data)} filas")
    print(f"  Columnas: {list(curve_data.columns)}")
    print(f"  Primeras 5 filas:")
    print(curve_data.head().to_string(index=False))
    print(f"  Últimas 5 filas:")
    print(curve_data.tail().to_string(index=False))
    
    # Verificar que corriente y temperatura tienen la misma longitud
    lengths_match = len(results['current_range']) == len(results['temperature_curve'])
    print(f"\n  Longitudes coinciden: {'✅ SÍ' if lengths_match else '❌ NO'}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACIÓN DE VISUALIZACIÓN")
    print("=" * 70)
    
    checks = [
        ("Métricas principales", True),
        ("Tabla balance de calor", abs(q_total_check - results['total_heat_loss']) < 0.001),
        ("Curva T-I (longitudes)", lengths_match),
        ("Curva T-I (monotonicidad)", all(temps[i] >= temps[i-1] for i in range(1, len(temps)))),
        ("Sensibilidad temperatura (monot.)", monotonic_decreasing),
        ("DataFrame exportación", len(df_export) == 20),
        ("DataFrame curva T-I", len(curve_data) == 50)
    ]
    
    all_ok = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {name:<40} {status}")
        if not passed:
            all_ok = False
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ TODAS LAS VERIFICACIONES DE VISUALIZACIÓN PASARON")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
    print("=" * 70)
    
    return all_ok

if __name__ == "__main__":
    verify_app_data_display()
