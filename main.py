"""
Punto de entrada principal para la aplicación de calculadora de ampacidad
"""

import sys
import os
import argparse
from ampacity_calculator import AmpacityCalculator, ConductorDatabase
from validator import safe_calculate_ampacity, AmpacityValidator
from settings_manager import SettingsManager, ProfileManager
from report_generator import ReportGenerator
import json


def main():
    """Función principal para ejecución desde línea de comandos"""
    
    parser = argparse.ArgumentParser(description='Calculadora de Ampacidad de Líneas de Transmisión')
    parser.add_argument('--mode', choices=['web', 'cli', 'batch'], default='web',
                       help='Modo de ejecución: web (interfaz gráfica), cli (línea de comandos), batch (procesamiento por lotes)')
    parser.add_argument('--conductor', type=str, help='ID del conductor a usar')
    parser.add_argument('--config', type=str, help='Archivo de configuración JSON')
    parser.add_argument('--output', type=str, help='Archivo de salida para resultados')
    parser.add_argument('--profile', type=str, help='Perfil de configuración predefinido')
    parser.add_argument('--report', action='store_true', help='Generar reporte HTML')
    
    args = parser.parse_args()
    
    if args.mode == 'web':
        # Ejecutar aplicación web Streamlit
        import subprocess
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    
    elif args.mode == 'cli':
        # Modo línea de comandos
        run_cli_mode(args)
    
    elif args.mode == 'batch':
        # Modo procesamiento por lotes
        run_batch_mode(args)


def run_cli_mode(args):
    """Ejecutar en modo línea de comandos"""
    
    # Inicializar componentes
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    settings = SettingsManager()
    profiles = ProfileManager()
    
    # Cargar configuración
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
        environmental_params = config.get('environmental', {})
    elif args.profile:
        profiles.apply_profile(args.profile, settings)
        environmental_params = settings.get_all_settings()
    else:
        environmental_params = settings.get_all_settings()
    
    # Seleccionar conductor
    if args.conductor:
        conductor_params = db.get_conductor(args.conductor)
        if not conductor_params:
            print(f"Error: Conductor '{args.conductor}' no encontrado")
            print("Conductores disponibles:")
            for cond_id, cond in db.get_all_conductors().items():
                print(f"  {cond_id}: {cond['name']}")
            return
    else:
        # Mostrar lista de conductores disponibles
        print("Conductores disponibles:")
        conductors = db.get_all_conductors()
        for i, (cond_id, cond) in enumerate(conductors.items(), 1):
            print(f"{i}. {cond_id}: {cond['name']} ({cond['type']})")
        
        try:
            choice = int(input("Seleccione el número del conductor: ")) - 1
            conductor_id = list(conductors.keys())[choice]
            conductor_params = conductors[conductor_id]
        except (ValueError, IndexError):
            print("Selección inválida")
            return
    
    # Realizar cálculo
    try:
        results = safe_calculate_ampacity(calculator, conductor_params, environmental_params)
        
        # Mostrar resultados
        print(f"\n📊 Resultados para {conductor_params['name']}")
        print("=" * 50)
        print(f"Ampacidad: {results['ampacity']:.2f} A")
        print(f"Temperatura del conductor: {results['conductor_temperature']:.1f} °C")
        print(f"Resistencia a temperatura: {results['resistance_at_temp']:.4f} Ω/km")
        print(f"Pérdida total de calor: {results['total_heat_loss']:.2f} W/m")
        
        print(f"\n🔥 Balance de Calor:")
        print(f"  Convección: {results['heat_convection']:.2f} W/m")
        print(f"  Radiación: {results['heat_radiation']:.2f} W/m")
        print(f"  Solar: {results['solar_heat_gain']:.2f} W/m")
        
        # Guardar resultados
        if args.output:
            output_data = {
                'conductor': conductor_params,
                'environmental': environmental_params,
                'results': results
            }
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"\n💾 Resultados guardados en: {args.output}")
        
        # Generar reporte
        if args.report:
            generator = ReportGenerator()
            report_file = generator.generate_basic_report(
                results, conductor_params, environmental_params
            )
            print(f"📄 Reporte generado: {report_file}")
    
    except Exception as e:
        print(f"Error en el cálculo: {e}")


def run_batch_mode(args):
    """Ejecutar en modo procesamiento por lotes"""
    
    if not args.config:
        print("Error: Modo batch requiere archivo de configuración (--config)")
        return
    
    # Cargar configuración batch
    with open(args.config, 'r') as f:
        batch_config = json.load(f)
    
    calculator = AmpacityCalculator()
    db = ConductorDatabase()
    generator = ReportGenerator()
    
    results_list = []
    
    # Procesar cada caso
    for i, case in enumerate(batch_config.get('cases', [])):
        conductor_id = case.get('conductor')
        env_params = case.get('environmental', {})
        
        conductor_params = db.get_conductor(conductor_id)
        if not conductor_params:
            print(f"Advertencia: Conductor '{conductor_id}' no encontrado, omitiendo caso {i+1}")
            continue
        
        try:
            results = safe_calculate_ampacity(calculator, conductor_params, env_params)
            
            # Agregar información del caso
            case_results = {
                'case_id': case.get('id', f'case_{i+1}'),
                'conductor': conductor_params,
                'environmental': env_params,
                'results': results
            }
            results_list.append(case_results)
            
            print(f"✅ Caso {i+1}: {conductor_params['name']} - Ampacidad: {results['ampacity']:.2f} A")
        
        except Exception as e:
            print(f"❌ Error en caso {i+1}: {e}")
    
    # Generar reporte comparativo
    if results_list:
        comparison_data = []
        for case_result in results_list:
            comparison_data.append({
                'name': case_result['conductor']['name'],
                'type': case_result['conductor']['type'],
                'diameter': case_result['conductor']['diameter'],
                'area': case_result['conductor']['area'],
                'ampacity': case_result['results']['ampacity'],
                'resistance_at_temp': case_result['results']['resistance_at_temp'],
                'total_heat_loss': case_result['results']['total_heat_loss']
            })
        
        report_file = generator.generate_comparison_report(comparison_data)
        print(f"\n📊 Reporte comparativo generado: {report_file}")
        
        # Guardar resultados completos
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results_list, f, indent=2, default=str)
            print(f"💾 Resultados completos guardados en: {args.output}")


def show_help():
    """Mostrar ayuda y ejemplos de uso"""
    help_text = """
Calculadora de Ampacidad - Guía de Uso

MODOS DE EJECUCIÓN:

1. Modo Web (recomendado):
   python main.py --mode web
   o simplemente: streamlit run app.py

2. Modo Línea de Comandos:
   python main.py --mode cli --conductor ACSR_477_kcmil --report

3. Modo Batch:
   python main.py --mode batch --config batch_config.json --output results.json

EJEMPLOS:

# Cálculo simple con conductor específico
python main.py --mode cli --conductor ACSR_477_kcmil

# Usando perfil predefinido
python main.py --mode cli --conductor ACSR_477_kcmil --profile tropical

# Con archivo de configuración personalizado
python main.py --mode cli --config my_config.json --output results.json --report

# Procesamiento por lotes
python main.py --mode batch --config batch_cases.json --report

PERFILES DISPONIBLES:
- tropical: Condiciones tropicales (alta temperatura y humedad)
- desert: Condiciones de desierto (muy alta temperatura)
- mountain: Condiciones de montaña (alta altitud)
- winter: Condiciones invernales (baja temperatura)
- coastal: Condiciones costeras (alta humedad)

FORMATO ARCHIVO CONFIGURACIÓN:
{
  "environmental": {
    "ambient_temperature": 40.0,
    "conductor_temperature_limit": 75.0,
    "altitude": 100.0,
    "wind_speed": 1.0,
    "solar_radiation": 1000.0,
    "emissivity": 0.8,
    "absorptivity": 0.8
  }
}

FORMATO ARCHIVO BATCH:
{
  "cases": [
    {
      "id": "case_1",
      "conductor": "ACSR_477_kcmil",
      "environmental": {
        "ambient_temperature": 40.0,
        "wind_speed": 1.0
      }
    },
    {
      "id": "case_2", 
      "conductor": "AAC_4/0_AW",
      "environmental": {
        "ambient_temperature": 30.0,
        "wind_speed": 2.0
      }
    }
  ]
}
"""
    print(help_text)


if __name__ == "__main__":
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        show_help()
    else:
        main()
