"""
Paquete de utilidades del asistente virtual.
Proporciona funciones helper comunes.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

def load_config(config_path: str) -> Dict[str, Any]:
    """Carga un archivo de configuración JSON."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error cargando configuración: {e}")
        return {}

def setup_logging(log_path: str = None) -> None:
    """Configura el sistema de logging."""
    config = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': logging.INFO
            }
        },
        'root': {
            'level': logging.INFO,
            'handlers': ['console']
        }
    }
    
    logging.config.dictConfig(config)
