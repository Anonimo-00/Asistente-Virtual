import os
import json
import yaml
from typing import Dict, Any, Union

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Carga la configuración desde archivos JSON/YAML"""
    if not config_path:
        config_path = os.path.join("config", "settings.json")
    
    try:
        ext = os.path.splitext(config_path)[1].lower()
        with open(config_path, 'r', encoding='utf-8') as f:
            if ext == '.json':
                return json.load(f)
            elif ext in ['.yml', '.yaml']:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return {}

def safe_get(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Obtiene un valor anidado de un diccionario de forma segura"""
    try:
        for key in path.split('.'):
            obj = obj[key]
        return obj
    except (KeyError, TypeError):
        return default

def ensure_dir(path: str) -> bool:
    """Asegura que un directorio existe"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False

def load_credentials() -> Dict[str, Any]:
    """Carga credenciales desde archivo YAML"""
    cred_path = os.path.join("config", "credentials.yml")
    return load_config(cred_path)
