"""
Módulo para gestión avanzada de conductores
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from ampacity_calculator import ConductorDatabase


class ConductorManager:
    """
    Gestor avanzado de conductores con funcionalidades de importación/exportación
    """
    
    def __init__(self):
        self.db = ConductorDatabase()
        self.data_file = "conductors_database.json"
    
    def load_from_file(self, filename: str = None) -> bool:
        """Cargar base de datos desde archivo JSON"""
        try:
            file_path = filename or self.data_file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for conductor_id, params in data.items():
                self.db.add_conductor(conductor_id, params)
            
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def save_to_file(self, filename: str = None) -> bool:
        """Guardar base de datos a archivo JSON"""
        try:
            file_path = filename or self.data_file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.db.get_all_conductors(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def import_from_excel(self, file_path: str, sheet_name: str = "Conductors") -> bool:
        """Importar conductores desde archivo Excel"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            required_columns = ['id', 'name', 'type', 'diameter', 'area', 
                              'rdc_20', 'alpha', 'beta', 'weight', 'max_temp']
            
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Missing required columns: {required_columns}")
            
            for _, row in df.iterrows():
                conductor_id = str(row['id'])
                params = {
                    'name': str(row['name']),
                    'type': str(row['type']),
                    'diameter': float(row['diameter']),
                    'area': float(row['area']),
                    'rdc_20': float(row['rdc_20']),
                    'alpha': float(row['alpha']),
                    'beta': float(row['beta']),
                    'weight': float(row['weight']),
                    'max_temp': float(row['max_temp'])
                }
                self.db.add_conductor(conductor_id, params)
            
            return True
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return False
    
    def export_to_excel(self, file_path: str) -> bool:
        """Exportar base de datos a archivo Excel"""
        try:
            conductors = self.db.get_all_conductors()
            
            data = []
            for conductor_id, params in conductors.items():
                row = params.copy()
                row['id'] = conductor_id
                data.append(row)
            
            df = pd.DataFrame(data)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Conductors', index=False)
                
                # Crear hoja de resumen
                summary_data = {
                    'Tipo': [],
                    'Cantidad': [],
                    'Diámetro Promedio (mm)': [],
                    'Área Promedio (mm²)': []
                }
                
                from collections import defaultdict
                type_stats = defaultdict(list)
                
                for params in conductors.values():
                    conductor_type = params['type']
                    type_stats[conductor_type].append(params)
                
                for conductor_type, params_list in type_stats.items():
                    summary_data['Tipo'].append(conductor_type)
                    summary_data['Cantidad'].append(len(params_list))
                    summary_data['Diámetro Promedio (mm)'].append(
                        sum(p['diameter'] for p in params_list) / len(params_list)
                    )
                    summary_data['Área Promedio (mm²)'].append(
                        sum(p['area'] for p in params_list) / len(params_list)
                    )
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
    
    def validate_conductor_params(self, params: Dict) -> List[str]:
        """Validar parámetros de conductor"""
        errors = []
        
        # Validar campos requeridos
        required_fields = ['name', 'type', 'diameter', 'area', 'rdc_20', 
                          'alpha', 'beta', 'weight', 'max_temp']
        
        for field in required_fields:
            if field not in params:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return errors
        
        # Validar rangos
        if params['diameter'] <= 0:
            errors.append("Diameter must be positive")
        
        if params['area'] <= 0:
            errors.append("Area must be positive")
        
        if params['rdc_20'] <= 0:
            errors.append("Resistance must be positive")
        
        if params['alpha'] <= 0:
            errors.append("Alpha coefficient must be positive")
        
        if params['beta'] < 0:
            errors.append("Beta coefficient must be non-negative")
        
        if params['weight'] <= 0:
            errors.append("Weight must be positive")
        
        if params['max_temp'] <= 0 or params['max_temp'] > 200:
            errors.append("Max temperature must be between 0 and 200°C")
        
        return errors
    
    def add_custom_conductor(self, conductor_id: str, params: Dict) -> bool:
        """Agregar conductor personalizado con validación"""
        errors = self.validate_conductor_params(params)
        if errors:
            print(f"Validation errors: {errors}")
            return False
        
        self.db.add_conductor(conductor_id, params)
        return True
    
    def get_conductor_comparison(self, conductor_ids: List[str]) -> pd.DataFrame:
        """Obtener tabla comparativa de conductores"""
        comparison_data = []
        
        for conductor_id in conductor_ids:
            params = self.db.get_conductor(conductor_id)
            if params:
                row = params.copy()
                row['id'] = conductor_id
                comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def search_conductors(self, **criteria) -> Dict:
        """Buscar conductores por criterios"""
        all_conductors = self.db.get_all_conductors()
        results = {}
        
        for conductor_id, params in all_conductors.items():
            match = True
            
            for key, value in criteria.items():
                if key not in params:
                    match = False
                    break
                
                if isinstance(value, (int, float)):
                    # Para valores numéricos, permitir rangos
                    if isinstance(value, tuple) and len(value) == 2:
                        if not (value[0] <= params[key] <= value[1]):
                            match = False
                            break
                    elif params[key] != value:
                        match = False
                        break
                elif isinstance(value, str):
                    # Para strings, búsqueda parcial (case insensitive)
                    if value.lower() not in str(params[key]).lower():
                        match = False
                        break
                else:
                    if params[key] != value:
                        match = False
                        break
            
            if match:
                results[conductor_id] = params
        
        return results


def create_sample_excel_template(file_path: str):
    """Crear plantilla Excel para importación de conductores"""
    sample_data = {
        'id': ['ACSR_1/0_AW', 'ACSR_4/0_AW', 'AAC_1/0_AW'],
        'name': ['ACSR 1/0 AW', 'ACSR 4/0 AW', 'AAC 1/0 AW'],
        'type': ['ACSR', 'ACSR', 'AAC'],
        'diameter': [11.68, 15.21, 10.41],
        'area': [53.5, 107.2, 53.5],
        'rdc_20': [0.540, 0.270, 0.538],
        'alpha': [0.00403, 0.00403, 0.00404],
        'beta': [0.0001, 0.0001, 0.00005],
        'weight': [0.326, 0.540, 0.145],
        'max_temp': [75.0, 75.0, 70.0]
    }
    
    df = pd.DataFrame(sample_data)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Conductors', index=False)
        
        # Crear hoja de instrucciones
        instructions = pd.DataFrame({
            'Campo': [
                'id', 'name', 'type', 'diameter', 'area', 'rdc_20',
                'alpha', 'beta', 'weight', 'max_temp'
            ],
            'Descripción': [
                'Identificador único del conductor',
                'Nombre descriptivo del conductor',
                'Tipo de conductor (ACSR, AAC, AAAC, ACAR, CU)',
                'Diámetro exterior en milímetros',
                'Área transversal en milímetros cuadrados',
                'Resistencia DC a 20°C en Ω/km',
                'Coeficiente de temperatura de resistencia (1/°C)',
                'Coeficiente de efecto piel para corriente AC',
                'Peso por metro en kg/m',
                'Temperatura máxima de operación en °C'
            ],
            'Formato': [
                'Texto sin espacios',
                'Texto',
                'Texto',
                'Número decimal',
                'Número decimal',
                'Número decimal',
                'Número decimal',
                'Número decimal',
                'Número decimal',
                'Número decimal'
            ]
        })
        
        instructions.to_excel(writer, sheet_name='Instrucciones', index=False)


if __name__ == "__main__":
    # Ejemplo de uso
    manager = ConductorManager()
    
    # Crear plantilla Excel
    create_sample_excel_template("conductor_template.xlsx")
    print("Plantilla Excel creada: conductor_template.xlsx")
    
    # Guardar base de datos actual
    manager.save_to_file()
    print("Base de datos guardada en: conductors_database.json")
