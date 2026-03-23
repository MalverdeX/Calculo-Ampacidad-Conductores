"""
Módulo para gestión de configuración y parámetros modificables
"""

import json
import os
from typing import Dict, Any, Optional
from config import DEFAULT_PARAMETERS


class SettingsManager:
    """
    Gestor de configuración para parámetros modificables del sistema
    """
    
    def __init__(self, settings_file: str = "user_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Combinar con valores por defecto
                return {**DEFAULT_PARAMETERS, **settings}
            except Exception as e:
                print(f"Error loading settings: {e}")
                return DEFAULT_PARAMETERS.copy()
        else:
            return DEFAULT_PARAMETERS.copy()
    
    def save_settings(self) -> bool:
        """Guardar configuración actual a archivo"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Obtener valor de un parámetro"""
        return self.settings.get(key, default)
    
    def set_parameter(self, key: str, value: Any) -> None:
        """Establecer valor de un parámetro"""
        self.settings[key] = value
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Actualizar múltiples parámetros"""
        self.settings.update(params)
    
    def reset_to_defaults(self) -> None:
        """Restablecer configuración a valores por defecto"""
        self.settings = DEFAULT_PARAMETERS.copy()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Obtener toda la configuración"""
        return self.settings.copy()
    
    def validate_parameter(self, key: str, value: Any) -> bool:
        """Validar valor de parámetro"""
        validation_rules = {
            'ambient_temperature': (-50, 60),
            'conductor_temperature_limit': (50, 150),
            'altitude': (0, 5000),
            'wind_speed': (0, 20),
            'solar_radiation': (0, 1200),
            'emissivity': (0.1, 1.0),
            'absorptivity': (0.1, 1.0),
            'angle_of_sun': (0, 90)
        }
        
        if key in validation_rules:
            min_val, max_val = validation_rules[key]
            return min_val <= value <= max_val
        
        return True
    
    def set_validated_parameter(self, key: str, value: Any) -> bool:
        """Establecer parámetro con validación"""
        if self.validate_parameter(key, value):
            self.set_parameter(key, value)
            return True
        return False


class ProfileManager:
    """
    Gestor de perfiles de configuración predefinidos
    """
    
    def __init__(self, profiles_file: str = "config_profiles.json"):
        self.profiles_file = profiles_file
        self.profiles = self.load_profiles()
    
    def load_profiles(self) -> Dict[str, Dict]:
        """Cargar perfiles desde archivo"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
        
        # Perfiles por defecto
        return {
            'tropical': {
                'name': 'Condiciones Tropicales',
                'description': 'Alta temperatura y humedad',
                'ambient_temperature': 45.0,
                'conductor_temperature_limit': 75.0,
                'altitude': 100.0,
                'wind_speed': 0.3,
                'solar_radiation': 1100.0,
                'emissivity': 0.8,
                'absorptivity': 0.9
            },
            'desert': {
                'name': 'Condiciones de Desierto',
                'description': 'Muy alta temperatura y radiación solar',
                'ambient_temperature': 50.0,
                'conductor_temperature_limit': 80.0,
                'altitude': 500.0,
                'wind_speed': 1.0,
                'solar_radiation': 1200.0,
                'emissivity': 0.7,
                'absorptivity': 0.8
            },
            'mountain': {
                'name': 'Condiciones de Montaña',
                'description': 'Alta altitud, baja temperatura',
                'ambient_temperature': 15.0,
                'conductor_temperature_limit': 70.0,
                'altitude': 3000.0,
                'wind_speed': 2.0,
                'solar_radiation': 900.0,
                'emissivity': 0.85,
                'absorptivity': 0.75
            },
            'winter': {
                'name': 'Condiciones Invernales',
                'description': 'Baja temperatura, posible nieve',
                'ambient_temperature': -5.0,
                'conductor_temperature_limit': 60.0,
                'altitude': 200.0,
                'wind_speed': 3.0,
                'solar_radiation': 400.0,
                'emissivity': 0.9,
                'absorptivity': 0.7
            },
            'coastal': {
                'name': 'Condiciones Costeras',
                'description': 'Alta humedad, vientos moderados',
                'ambient_temperature': 30.0,
                'conductor_temperature_limit': 75.0,
                'altitude': 50.0,
                'wind_speed': 1.5,
                'solar_radiation': 800.0,
                'emissivity': 0.8,
                'absorptivity': 0.85
            }
        }
    
    def save_profiles(self) -> bool:
        """Guardar perfiles a archivo"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving profiles: {e}")
            return False
    
    def get_profile(self, profile_id: str) -> Optional[Dict]:
        """Obtener perfil específico"""
        return self.profiles.get(profile_id)
    
    def get_all_profiles(self) -> Dict[str, Dict]:
        """Obtener todos los perfiles"""
        return self.profiles.copy()
    
    def add_profile(self, profile_id: str, profile_data: Dict) -> bool:
        """Agregar nuevo perfil"""
        if 'name' not in profile_data or 'description' not in profile_data:
            return False
        
        self.profiles[profile_id] = profile_data
        return self.save_profiles()
    
    def update_profile(self, profile_id: str, profile_data: Dict) -> bool:
        """Actualizar perfil existente"""
        if profile_id not in self.profiles:
            return False
        
        self.profiles[profile_id].update(profile_data)
        return self.save_profiles()
    
    def delete_profile(self, profile_id: str) -> bool:
        """Eliminar perfil"""
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            return self.save_profiles()
        return False
    
    def apply_profile(self, profile_id: str, settings_manager: SettingsManager) -> bool:
        """Aplicar perfil a configuración actual"""
        profile = self.get_profile(profile_id)
        if profile:
            # Extraer solo los parámetros de configuración
            config_params = {k: v for k, v in profile.items() 
                           if k not in ['name', 'description']}
            settings_manager.update_parameters(config_params)
            return True
        return False


class ConductorCustomizer:
    """
    Gestor para personalización de parámetros de conductores
    """
    
    def __init__(self, custom_file: str = "custom_conductors.json"):
        self.custom_file = custom_file
        self.custom_conductors = self.load_custom_conductors()
    
    def load_custom_conductors(self) -> Dict:
        """Cargar conductores personalizados"""
        if os.path.exists(self.custom_file):
            try:
                with open(self.custom_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading custom conductors: {e}")
        return {}
    
    def save_custom_conductors(self) -> bool:
        """Guardar conductores personalizados"""
        try:
            with open(self.custom_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_conductors, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving custom conductors: {e}")
            return False
    
    def add_custom_conductor(self, conductor_id: str, params: Dict) -> bool:
        """Agregar conductor personalizado"""
        # Validar parámetros requeridos
        required_fields = ['name', 'type', 'diameter', 'area', 'rdc_20', 
                          'alpha', 'beta', 'weight', 'max_temp']
        
        for field in required_fields:
            if field not in params:
                return False
        
        self.custom_conductors[conductor_id] = params
        return self.save_custom_conductors()
    
    def update_custom_conductor(self, conductor_id: str, params: Dict) -> bool:
        """Actualizar conductor personalizado"""
        if conductor_id in self.custom_conductors:
            self.custom_conductors[conductor_id].update(params)
            return self.save_custom_conductors()
        return False
    
    def delete_custom_conductor(self, conductor_id: str) -> bool:
        """Eliminar conductor personalizado"""
        if conductor_id in self.custom_conductors:
            del self.custom_conductors[conductor_id]
            return self.save_custom_conductors()
        return False
    
    def get_custom_conductor(self, conductor_id: str) -> Optional[Dict]:
        """Obtener conductor personalizado"""
        return self.custom_conductors.get(conductor_id)
    
    def get_all_custom_conductors(self) -> Dict:
        """Obtener todos los conductores personalizados"""
        return self.custom_conductors.copy()


if __name__ == "__main__":
    # Ejemplo de uso
    settings = SettingsManager()
    profiles = ProfileManager()
    customizer = ConductorCustomizer()
    
    print("Configuración actual:")
    print(json.dumps(settings.get_all_settings(), indent=2))
    
    print("\nPerfiles disponibles:")
    for profile_id, profile in profiles.get_all_profiles().items():
        print(f"- {profile_id}: {profile['name']}")
    
    print("\nConductores personalizados:")
    print(json.dumps(customizer.get_all_custom_conductors(), indent=2))
