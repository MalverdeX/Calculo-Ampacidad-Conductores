"""
Módulo para generación de reportes y visualización de resultados
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import os


class ReportGenerator:
    """
    Generador de reportes para análisis de ampacidad
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Asegurar que el directorio de salida exista"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_basic_report(self, results: Dict, conductor_params: Dict, 
                            environmental_params: Dict, filename: str = None) -> str:
        """Generar reporte básico en formato HTML"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ampacity_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte de Ampacidad - {conductor_params['name']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 20px;
                }}
                .section {{
                    margin: 20px 0;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    background-color: #f8f9fa;
                }}
                .metric {{
                    display: inline-block;
                    margin: 10px;
                    padding: 15px;
                    background-color: #e3f2fd;
                    border-radius: 5px;
                    text-align: center;
                    min-width: 150px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1976d2;
                }}
                .metric-label {{
                    font-size: 12px;
                    color: #666;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #ffc107;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ Reporte de Ampacidad</h1>
                    <h2>{conductor_params['name']}</h2>
                    <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h3>📊 Resultados Principales</h3>
                    <div class="metric">
                        <div class="metric-value">{results['ampacity']:.1f} A</div>
                        <div class="metric-label">Ampacidad</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{results['conductor_temperature']:.1f} °C</div>
                        <div class="metric-label">Temperatura del Conductor</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{results['resistance_at_temp']:.4f} Ω/km</div>
                        <div class="metric-label">Resistencia a Temperatura</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{results['total_heat_loss']:.2f} W/m</div>
                        <div class="metric-label">Pérdida Neta de Calor</div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🔋 Parámetros del Conductor</h3>
                    <table>
                        <tr><th>Parámetro</th><th>Valor</th></tr>
                        <tr><td>Nombre</td><td>{conductor_params['name']}</td></tr>
                        <tr><td>Tipo</td><td>{conductor_params['type']}</td></tr>
                        <tr><td>Diámetro</td><td>{conductor_params['diameter']} mm</td></tr>
                        <tr><td>Área</td><td>{conductor_params['area']} mm²</td></tr>
                        <tr><td>Resistencia DC a 20°C</td><td>{conductor_params['rdc_20']} Ω/km</td></tr>
                        <tr><td>Alpha (α)</td><td>{conductor_params['alpha']}</td></tr>
                        <tr><td>Beta (β)</td><td>{conductor_params['beta']}</td></tr>
                        <tr><td>Peso</td><td>{conductor_params['weight']} kg/m</td></tr>
                        <tr><td>Temperatura Máxima</td><td>{conductor_params['max_temp']} °C</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <h3>🌤️ Condiciones Ambientales</h3>
                    <table>
                        <tr><th>Parámetro</th><th>Valor</th></tr>
                        <tr><td>Temperatura Ambiente</td><td>{environmental_params.get('ambient_temperature', 'N/A')} °C</td></tr>
                        <tr><td>Temperatura Máxima Conductor</td><td>{environmental_params.get('conductor_temperature_limit', 'N/A')} °C</td></tr>
                        <tr><td>Altitud</td><td>{environmental_params.get('altitude', 'N/A')} m</td></tr>
                        <tr><td>Velocidad del Viento</td><td>{environmental_params.get('wind_speed', 'N/A')} m/s</td></tr>
                        <tr><td>Radiación Solar</td><td>{environmental_params.get('solar_radiation', 'N/A')} W/m²</td></tr>
                        <tr><td>Emisividad</td><td>{environmental_params.get('emissivity', 'N/A')}</td></tr>
                        <tr><td>Absortividad</td><td>{environmental_params.get('absorptivity', 'N/A')}</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <h3>🔥 Balance de Calor</h3>
                    <table>
                        <tr><th>Componente</th><th>Valor</th></tr>
                        <tr><td>Pérdida por Convección</td><td>{results['heat_convection']:.2f} W/m</td></tr>
                        <tr><td>Pérdida por Radiación</td><td>{results['heat_radiation']:.2f} W/m</td></tr>
                        <tr><td>Ganancia Solar</td><td>{results['solar_heat_gain']:.2f} W/m</td></tr>
                        <tr><td>Pérdida Neta Total</td><td>{results['total_heat_loss']:.2f} W/m</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <h3>📈 Análisis</h3>
                    <div class="highlight">
                        <strong>Observaciones:</strong>
                        <ul>
                            <li>La ampacidad calculada es de {results['ampacity']:.1f} A bajo las condiciones especificadas.</li>
                            <li>La disipación de calor por convección representa {results['heat_convection']/results['total_heat_loss']*100:.1f}% del total.</li>
                            <li>La disipación por radiación representa {results['heat_radiation']/results['total_heat_loss']*100:.1f}% del total.</li>
                            <li>La ganancia solar reduce la capacidad en {results['solar_heat_gain']/results['total_heat_loss']*100:.1f}%.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_comparison_report(self, comparison_data: List[Dict], 
                                 filename: str = None) -> str:
        """Generar reporte comparativo de múltiples conductores"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Crear DataFrame para análisis
        df = pd.DataFrame(comparison_data)
        
        # Generar gráficos comparativos
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Ampacidad', 'Resistencia a Temperatura', 
                          'Diámetro vs Ampacidad', 'Pérdidas de Calor'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Gráfico 1: Ampacidad
        fig.add_trace(
            go.Bar(x=df['name'], y=df['ampacity'], name='Ampacidad (A)',
                   marker_color='blue'),
            row=1, col=1
        )
        
        # Gráfico 2: Resistencia
        fig.add_trace(
            go.Bar(x=df['name'], y=df['resistance_at_temp'], 
                   name='Resistencia (Ω/km)', marker_color='red'),
            row=1, col=2
        )
        
        # Gráfico 3: Diámetro vs Ampacidad
        fig.add_trace(
            go.Scatter(x=df['diameter'], y=df['ampacity'], mode='markers+lines',
                      name='Diámetro vs Ampacidad', marker_color='green'),
            row=2, col=1
        )
        
        # Gráfico 4: Pérdidas de calor
        fig.add_trace(
            go.Bar(x=df['name'], y=df['total_heat_loss'], 
                   name='Pérdidas (W/m)', marker_color='orange'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Análisis Comparativo de Conductores",
            showlegend=False,
            height=800
        )
        
        # Guardar gráfico
        graph_file = filepath.replace('.html', '_graph.html')
        fig.write_html(graph_file)
        
        # Generar HTML del reporte
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte Comparativo de Conductores</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                .best {{
                    background-color: #d4edda;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Reporte Comparativo de Conductores</h1>
                    <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                
                <h2>🏆 Mejores Opciones</h2>
                <ul>
                    <li><strong>Mayor Ampacidad:</strong> {df.loc[df['ampacity'].idxmax(), 'name']} ({df['ampacity'].max():.1f} A)</li>
                    <li><strong>Menor Resistencia:</strong> {df.loc[df['resistance_at_temp'].idxmin(), 'name']} ({df['resistance_at_temp'].min():.4f} Ω/km)</li>
                    <li><strong>Mejor Disipación:</strong> {df.loc[df['total_heat_loss'].idxmax(), 'name']} ({df['total_heat_loss'].max():.2f} W/m)</li>
                </ul>
                
                <h2>📋 Tabla Comparativa</h2>
                {df.to_html(index=False, classes='table', escape=False)}
                
                <h2>📈 Gráficos Comparativos</h2>
                <iframe src="{os.path.basename(graph_file)}" width="100%" height="800px"></iframe>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_sensitivity_analysis(self, sensitivity_data: Dict, 
                                    filename: str = None) -> str:
        """Generar reporte de análisis de sensibilidad"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sensitivity_analysis_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Crear gráficos de sensibilidad
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Efecto Velocidad Viento', 'Efecto Temperatura Ambiente',
                          'Efecto Altitud', 'Efecto Radiación Solar')
        )
        
        # Velocidad del viento
        if 'wind_speed' in sensitivity_data:
            wind_data = sensitivity_data['wind_speed']
            fig.add_trace(
                go.Scatter(x=wind_data['values'], y=wind_data['ampacities'],
                          mode='lines+markers', name='Velocidad Viento'),
                row=1, col=1
            )
        
        # Temperatura ambiente
        if 'ambient_temperature' in sensitivity_data:
            temp_data = sensitivity_data['ambient_temperature']
            fig.add_trace(
                go.Scatter(x=temp_data['values'], y=temp_data['ampacities'],
                          mode='lines+markers', name='Temperatura Ambiente'),
                row=1, col=2
            )
        
        # Altitud
        if 'altitude' in sensitivity_data:
            alt_data = sensitivity_data['altitude']
            fig.add_trace(
                go.Scatter(x=alt_data['values'], y=alt_data['ampacities'],
                          mode='lines+markers', name='Altitud'),
                row=2, col=1
            )
        
        # Radiación solar
        if 'solar_radiation' in sensitivity_data:
            solar_data = sensitivity_data['solar_radiation']
            fig.add_trace(
                go.Scatter(x=solar_data['values'], y=solar_data['ampacities'],
                          mode='lines+markers', name='Radiación Solar'),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Análisis de Sensibilidad",
            height=800
        )
        
        # Guardar gráfico
        graph_file = filepath.replace('.html', '_sensitivity.html')
        fig.write_html(graph_file)
        
        # Generar HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Análisis de Sensibilidad</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 20px;
                }}
                .insight {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Análisis de Sensibilidad</h1>
                    <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                
                <div class="insight">
                    <h3>🔍 Conclusiones del Análisis</h3>
                    <p>El análisis muestra cómo diferentes parámetros ambientales afectan la ampacidad del conductor.</p>
                </div>
                
                <iframe src="{os.path.basename(graph_file)}" width="100%" height="800px"></iframe>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def export_to_excel(self, results: Dict, conductor_params: Dict, 
                       environmental_params: Dict, filename: str = None) -> str:
        """Exportar resultados a Excel"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ampacity_results_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Hoja de resultados principales
            main_data = {
                'Parámetro': [
                    'Conductor', 'Tipo', 'Diámetro (mm)', 'Área (mm²)',
                    'Resistencia DC a 20°C (Ω/km)', 'Alpha (1/°C)', 'Beta',
                    'Temperatura Ambiente (°C)', 'Temperatura Máxima (°C)',
                    'Altitud (m)', 'Velocidad Viento (m/s)', 'Radiación Solar (W/m²)',
                    'Emisividad', 'Absortividad', 'Ampacidad (A)', 
                    'Resistencia a Temperatura (Ω/km)', 'Pérdida Convección (W/m)',
                    'Pérdida Radiación (W/m)', 'Ganancia Solar (W/m)',
                    'Pérdida Neta (W/m)'
                ],
                'Valor': [
                    conductor_params['name'], conductor_params['type'],
                    conductor_params['diameter'], conductor_params['area'],
                    conductor_params['rdc_20'], conductor_params['alpha'],
                    conductor_params['beta'],
                    environmental_params.get('ambient_temperature', ''),
                    environmental_params.get('conductor_temperature_limit', ''),
                    environmental_params.get('altitude', ''),
                    environmental_params.get('wind_speed', ''),
                    environmental_params.get('solar_radiation', ''),
                    environmental_params.get('emissivity', ''),
                    environmental_params.get('absorptivity', ''),
                    results['ampacity'], results['resistance_at_temp'],
                    results['heat_convection'], results['heat_radiation'],
                    results['solar_heat_gain'], results['total_heat_loss']
                ]
            }
            
            df_main = pd.DataFrame(main_data)
            df_main.to_excel(writer, sheet_name='Resultados Principales', index=False)
            
            # Hoja de curva temperatura-corriente
            if 'current_range' in results and 'temperature_curve' in results:
                curve_data = pd.DataFrame({
                    'Corriente (A)': results['current_range'],
                    'Temperatura (°C)': results['temperature_curve']
                })
                curve_data.to_excel(writer, sheet_name='Curva T-I', index=False)
            
            # Hoja de detalles del cálculo
            if 'calculation_details' in results:
                details_data = pd.DataFrame(list(results['calculation_details'].items()),
                                          columns=['Parámetro', 'Valor'])
                details_data.to_excel(writer, sheet_name='Detalles Cálculo', index=False)
        
        return filepath


if __name__ == "__main__":
    # Ejemplo de uso
    generator = ReportGenerator()
    
    # Datos de ejemplo
    sample_results = {
        'ampacity': 450.5,
        'conductor_temperature': 75.0,
        'resistance_at_temp': 0.185,
        'heat_convection': 25.3,
        'heat_radiation': 18.7,
        'solar_heat_gain': 8.2,
        'total_heat_loss': 35.8,
        'current_range': list(range(0, 500, 10)),
        'temperature_curve': [25 + i*0.1 for i in range(50)]
    }
    
    sample_conductor = {
        'name': 'ACSR 477 kcmil',
        'type': 'ACSR',
        'diameter': 21.79,
        'area': 241.7,
        'rdc_20': 0.120,
        'alpha': 0.00403,
        'beta': 0.00015,
        'weight': 1.099,
        'max_temp': 75.0
    }
    
    sample_env = {
        'ambient_temperature': 40.0,
        'conductor_temperature_limit': 75.0,
        'altitude': 100.0,
        'wind_speed': 1.0,
        'solar_radiation': 1000.0,
        'emissivity': 0.8,
        'absorptivity': 0.8
    }
    
    # Generar reportes
    report_file = generator.generate_basic_report(sample_results, sample_conductor, sample_env)
    excel_file = generator.export_to_excel(sample_results, sample_conductor, sample_env)
    
    print(f"Reporte HTML generado: {report_file}")
    print(f"Reporte Excel generado: {excel_file}")
