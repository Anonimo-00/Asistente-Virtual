import json
import os
import time
import threading
import shutil
from datetime import datetime
import logging
from typing import Any, Optional
from utils.theme_events import theme_events

logger = logging.getLogger(__name__)

# Estado global con valores por defecto
_global_state = {
    "is_active": False,
    "wifi_status": False,
    "theme_mode": "dark",
    "last_activity": time.time(),
    "last_backup_time": 0,
    "app_settings": {
        "theme": {
            "mode": "dark",
            "auto_switch": False,
            "switch_time": {
                "light": "07:00",
                "dark": "19:00"
            }
        }
    },
    "user_preferences": {
        "theme": "dark",
        "font_size": 16,
        "voice_enabled": False
    }
}

# Intervalos de guardado personalizados por variable
_save_intervals = {
    "wifi_status": 1,        # cada 1 segundo
    "theme_mode": 300,       # cada 5 minutos
    "is_active": 60,         # cada 1 minuto
    "last_activity": 60,     # cada 1 minuto
    "app_settings": 300,     # cada 5 minutos
    "user_preferences": 60   # cada 1 minuto
}

_last_saved = {key: 0 for key in _global_state.keys()}
_backup_count = 5
_backup_interval = 3600  # 1 hora
_cache_dir = "cache"
_data_dir = "data"
_temp_dir = os.path.join(_cache_dir, "temp")  # Mover temp dentro de cache
_vars_file = os.path.join(_data_dir, "global_vars.json")
_backup_dir = os.path.join(_cache_dir, "global_vars")

def get_global_var(key: str, default: Any = None) -> Any:
    """Obtiene una variable global con valor por defecto"""
    return _global_state.get(key, default)

def set_global_var(key: str, value: Any) -> bool:
    """Establece una variable global y guarda si es necesario"""
    try:
        if key in _global_state:
            _global_state[key] = value
            check_and_save(key)
            return True
        return False
    except Exception as e:
        logger.error(f"Error estableciendo variable global {key}: {e}")
        return False

def update_user_preferences(preferences: dict) -> bool:
    """Actualiza las preferencias del usuario"""
    try:
        _global_state["user_preferences"].update(preferences)
        check_and_save("user_preferences")
        return True
    except Exception as e:
        logger.error(f"Error actualizando preferencias: {e}")
        return False

def ensure_directories():
    """Asegura que existan los directorios necesarios"""
    directories = [
        _cache_dir,
        _temp_dir,  # Usar la constante _temp_dir
        os.path.join(_cache_dir, "global_vars"),
        os.path.join(_cache_dir, "web_cache"),
        os.path.join(_cache_dir, "web_cache/images"),
        os.path.join(_cache_dir, "web_cache/responses"),
        os.path.join(_cache_dir, "skills"),
        _data_dir,
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def create_backup():
    """Crea un backup del estado global"""
    try:
        ensure_directories()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(_backup_dir, f"vars_{timestamp}.json")
        
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(_global_state, f, indent=4)
            
        # Limpiar backups antiguos
        cleanup_old_backups()
        return True
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return False

def cleanup_old_backups():
    """Limpia backups antiguos manteniendo solo los más recientes"""
    try:
        backups = sorted([f for f in os.listdir(_backup_dir) if f.startswith("vars_")])
        if len(backups) > _backup_count:
            for old_backup in backups[:-_backup_count]:
                os.remove(os.path.join(_backup_dir, old_backup))
    except Exception as e:
        logger.error(f"Error limpiando backups: {e}")

def save_state():
    """Guarda el estado global en disco"""
    try:
        ensure_directories()
        temp_file = os.path.join(_temp_dir, "global_vars.tmp")
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(_global_state, f, indent=4)
            
        # Reemplazar archivo de forma segura
        shutil.move(temp_file, _vars_file)
        return True
    except Exception as e:
        logger.error(f"Error guardando estado: {e}")
        return False

def load_state() -> bool:
    """Carga el estado global desde disco"""
    try:
        if os.path.exists(_vars_file):
            with open(_vars_file, "r", encoding="utf-8") as f:
                loaded_state = json.load(f)
                # Asegurar que el tema esté definido
                if "theme_mode" not in loaded_state:
                    loaded_state["theme_mode"] = "dark"
                _global_state.update(loaded_state)
                
                # Sincronizar preferencias
                _global_state["user_preferences"]["theme"] = _global_state["theme_mode"]
            return True
        return False
    except Exception as e:
        logger.error(f"Error cargando estado: {e}")
        return False

def check_and_save(key: Optional[str] = None):
    """Verifica y guarda el estado si es necesario"""
    current_time = time.time()
    
    if key and key in _save_intervals:
        if current_time - _last_saved[key] >= _save_intervals[key]:
            _last_saved[key] = current_time
            save_state()
            return
    
    # Verificar todas las variables
    save_needed = False
    for k, interval in _save_intervals.items():
        if current_time - _last_saved[k] >= interval:
            _last_saved[k] = current_time
            save_needed = True
            
    if save_needed:
        save_state()
    
    # Verificar backup
    if current_time - get_global_var("last_backup_time", 0) >= _backup_interval:
        if create_backup():
            set_global_var("last_backup_time", current_time)

def start_auto_save():
    """Inicia el guardado automático en segundo plano"""
    def auto_save_thread():
        while get_global_var("is_active"):
            try:
                check_and_save()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error en auto save: {e}")
                time.sleep(5)
    
    threading.Thread(target=auto_save_thread, daemon=True).start()

def update_global_state(new_state: dict) -> bool:
    """Actualiza múltiples variables globales a la vez"""
    try:
        for key, value in new_state.items():
            if key in _global_state:
                _global_state[key] = value
                _last_saved[key] = 0  # Forzar guardado en próxima verificación
        check_and_save()
        return True
    except Exception as e:
        logger.error(f"Error actualizando estado global: {e}")
        return False

def update_theme(mode: str) -> bool:
    """Actualiza el tema y sus configuraciones relacionadas"""
    try:
        # Validaciones iniciales
        if not isinstance(mode, str):
            logger.error(f"Tipo de tema inválido: {type(mode)}")
            return False

        # Normalizar valor del tema
        mode = mode.lower()
        if mode not in ["light", "dark"]:
            logger.error(f"Modo de tema inválido: {mode}")
            return False

        # Validar si hay cambio real
        current_theme = _global_state["theme_mode"].lower()
        if current_theme == mode:
            logger.debug(f"El tema ya está en modo: {mode}")
            return True

        logger.info(f"Actualizando tema de {current_theme} a {mode}")
        
        # Actualizar estado global de forma atómica
        updates = {
            "theme_mode": mode,
            "app_settings": {
                **_global_state["app_settings"],
                "theme": {
                    **_global_state["app_settings"].get("theme", {}),
                    "mode": mode
                }
            },
            "user_preferences": {
                **_global_state["user_preferences"],
                "theme": mode
            }
        }
        
        # Aplicar actualizaciones
        _global_state.update(updates)
        
        # Forzar guardado inmediato
        _last_saved["theme_mode"] = 0
        check_and_save("theme_mode")
        
        # Notificar cambio de tema
        if not theme_events:
            logger.warning("theme_events no está inicializado")
            return True
            
        success = theme_events.notify_theme_change(mode)
        if not success:
            logger.warning("Notificación de cambio de tema no exitosa")
            # Continuamos aunque la notificación falle
            
        logger.info(f"Tema actualizado exitosamente a: {mode}")
        return True
        
    except KeyError as e:
        logger.error(f"Error de acceso a clave en estado global: {e}")
        return False
    except AttributeError as e:
        logger.error(f"Error de acceso a atributo: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado actualizando tema: {str(e)}")
        return False

# Inicialización
ensure_directories()
load_state()

