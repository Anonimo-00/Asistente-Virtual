import logging
import json
import os
import time
from typing import Callable, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ThemeState:
    mode: str = "dark"
    last_update: float = 0

class ThemeEventManager:
    _instance = None
    _listeners: List[Callable] = []
    _state: ThemeState = None

    def __init__(self):
        self._state = ThemeState()
        self._load_initial_theme()

    def _load_initial_theme(self):
        try:
            settings_path = os.path.join("config", "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    theme_mode = settings.get('ui', {}).get('theme_mode', 'dark').lower()
                    self._state.mode = theme_mode
                    self._state.last_update = time.time()
                logger.info(f"Tema inicial cargado: {self._state.mode}")
            else:
                logger.warning("Archivo settings.json no encontrado, usando tema por defecto")
        except Exception as e:
            logger.error(f"Error cargando tema inicial: {e}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ThemeEventManager()
        return cls._instance

    def notify_theme_change(self, theme: str) -> bool:
        """Notifica el cambio de tema a todos los listeners"""
        try:
            # Validación y normalización
            if not isinstance(theme, str):
                logger.error(f"Tipo de tema inválido: {type(theme)}")
                return False
                
            theme = theme.lower()
            if theme not in ['light', 'dark']:
                logger.error(f"Valor de tema inválido: {theme}")
                return False

            # Actualizar estado interno
            self._state.mode = theme
            self._state.last_update = time.time()
            
            # Notificar a los listeners
            listener_count = len(self._listeners)
            success_count = 0
            
            for listener in self._listeners:
                try:
                    listener(theme)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error en listener de tema: {e}")

            if success_count < listener_count:
                logger.warning(f"Algunos listeners fallaron: {success_count}/{listener_count}")
            else:
                logger.info(f"Todos los listeners notificados: {success_count}")

            return True

        except Exception as e:
            logger.error(f"Error en notify_theme_change: {e}")
            return False

    @property
    def current_theme(self) -> str:
        """Obtiene el tema actual de forma segura"""
        if not self._state:
            self._state = ThemeState()
        return self._state.mode

    def add_listener(self, callback: Callable):
        if callback and callable(callback) and callback not in self._listeners:
            self._listeners.append(callback)
            logger.debug(f"Listener añadido. Total: {len(self._listeners)}")

    def remove_listener(self, callback: Callable):
        if callback in self._listeners:
            self._listeners.remove(callback)
            logger.debug(f"Listener eliminado. Total: {len(self._listeners)}")

# Asegurar que la instancia se crea de inmediato
theme_events = ThemeEventManager.get_instance()
