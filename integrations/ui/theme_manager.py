import json
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import flet as ft
import logging
from global_vars import update_theme, get_global_var
from utils.theme_events import theme_events

logger = logging.getLogger(__name__)

@dataclass
class ThemeColors:
    bg_primary: str
    bg_secondary: str 
    accent: str
    text_primary: str
    text_secondary: str
    surface: str
    card_bg: str
    error: str
    success: str
    divider: str
    shadow: str
    input_bg: str
    input_text: str
    button_bg: str
    button_text: str
    hover: str
    settings_bg: str
    settings_text: str
    settings_border: str
    # Nuevos colores para estilo Google Assistant
    assistant_bubble: str
    user_bubble: str
    bubble_shadow: str
    icon_button: str
    icon_button_hover: str
    mic_active: str
    card_border: str

class ThemeManager:
    _instance = None
    _settings_file = os.path.join("config", "settings.json")
    
    def __init__(self):
        self.themes: Dict[str, ThemeColors] = {}
        self.current_theme = theme_events.current_theme
        self._load_themes()
        self._sync_settings()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = ThemeManager()
        return cls._instance

    def _load_themes(self):
        """Carga los temas desde settings.json"""
        try:
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                themes_config = settings['ui']['themes']
                
                for theme_name, colors in themes_config.items():
                    self.themes[theme_name] = ThemeColors(**colors)
        except Exception as e:
            print(f"Error cargando temas: {e}")
            # Usar temas por defecto si falla la carga
            self._load_default_themes()

    def _sync_settings(self):
        """Sincroniza la configuración del tema con settings.json"""
        try:
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.ui_settings = settings.get('ui', {})
                
            # Sincronizar tema actual
            if self.current_theme != self.ui_settings.get('theme_mode'):
                self.current_theme = self.ui_settings['theme_mode']
                update_theme(self.current_theme)
                
        except Exception as e:
            logger.error(f"Error sincronizando configuración: {e}")

    def toggle_theme(self, page: Optional[ft.Page] = None) -> str:
        try:
            new_mode = "light" if self.current_theme == "dark" else "dark"
            self.current_theme = new_mode
            
            # Notificar cambio de tema
            theme_events.notify_theme_change(new_mode)
            
            # Aplicar cambios si hay una página
            if page:
                self.apply_theme(page)
                
            return new_mode
        except Exception as e:
            logger.error(f"Error cambiando tema: {e}")
            return self.current_theme

    def _update_settings_file(self, theme_mode: str):
        """Actualiza el modo de tema en settings.json"""
        try:
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            settings['ui']['theme_mode'] = theme_mode
            
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error actualizando settings.json: {e}")

    def apply_theme(self, page: ft.Page, theme_mode: Optional[str] = None):
        """Aplica el tema seleccionado a la página"""
        if theme_mode:
            self.current_theme = theme_mode
            
        theme = self.themes.get(self.current_theme, self.themes["dark"])
        
        # Material 3 Theme
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=theme.accent,
                secondary=theme.text_secondary,
                surface=theme.surface,
                background=theme.bg_primary,
                error=theme.error,
                surface_tint=theme.accent,
                outline=theme.divider,
                shadow=theme.shadow,
            ),
            visual_density=ft.ThemeVisualDensity.COMFORTABLE,
            use_material3=True,
        )
        
        # Aplicar estilos específicos
        page.bgcolor = theme.bg_primary
        page.fonts = {
            "Roboto": "/fonts/Roboto-Regular.ttf",
            "Google Sans": "/fonts/GoogleSans-Regular.ttf",
        }
        
        # Actualizar controles
        self._update_controls(page, theme)
        page.update()

    def _update_controls(self, page: ft.Page, theme: ThemeColors):
        """Actualiza los estilos de los controles"""
        # Actualizar estilos de controles comunes
        for control in page.controls:
            if isinstance(control, ft.TextField):
                control.bgcolor = theme.input_bg
                control.color = theme.input_text
            elif isinstance(control, ft.ElevatedButton):
                control.bgcolor = theme.button_bg
                control.color = theme.button_text
            elif isinstance(control, ft.Card):
                control.bgcolor = theme.card_bg
                control.shadow = theme.card_shadow  # Aplicar sombra a las tarjetas
                control.hover_color = theme.card_hover  # Aplicar color de hover a las tarjetas

                
        # Forzar actualización de controles
        page.update()

    def get_colors(self, theme_mode: str = "dark") -> ThemeColors:
        """Obtiene los colores del tema seleccionado"""
        return self.themes.get(theme_mode, self.themes["dark"])

    def _load_default_themes(self):
        """Carga temas por defecto si falla la carga desde archivo"""
        self.themes = {
            "dark": ThemeColors(
                bg_primary="#121212",
                bg_secondary="#1E1E1E",
                accent="#8ab4f8",
                text_primary="#FFFFFF",
                text_secondary="#B3B3B3",
                surface="#2D2D2D",
                card_bg="rgba(32, 33, 36, 0.95)",
                error="#CF6679",
                success="#03DAC6",
                divider="#3C4043",
                shadow="rgba(0, 0, 0, 0.3)",
                input_bg="#2D2D2D",
                input_text="#FFFFFF",
                button_bg="#3C4043",
                button_text="#FFFFFF",
                hover="rgba(255, 255, 255, 0.1)",
                settings_bg="#2D2D2D",
                settings_text="#FFFFFF",
                settings_border="#3C4043",
                # Nuevos colores para estilo Google Assistant
                assistant_bubble="#3C4043",
                user_bubble="#8ab4f8",
                bubble_shadow="rgba(0, 0, 0, 0.2)",
                icon_button="#8ab4f8",
                icon_button_hover="#a5c7ff",
                mic_active="#EA4335",
                card_border="rgba(255, 255, 255, 0.1)",
                # Nuevos colores para el diseño basado en tarjetas
                card_shadow="rgba(0, 0, 0, 0.15)",
                card_hover="rgba(255, 255, 255, 0.05)"
            ),

            "light": ThemeColors(
                bg_primary="#FFFFFF",
                bg_secondary="#F8F9FA",
                accent="#1A73E8",
                text_primary="#202124",
                text_secondary="#5F6368",
                surface="#FFFFFF",
                card_bg="rgba(255, 255, 255, 0.98)",
                error="#B00020",
                success="#0F9D58",
                divider="#E0E0E0",
                shadow="rgba(0, 0, 0, 0.1)",
                input_bg="#F8F9FA",
                input_text="#202124", 
                button_bg="#F1F3F4",
                button_text="#202124",
                hover="rgba(0, 0, 0, 0.05)",
                settings_bg="#FFFFFF",
                settings_text="#202124",
                settings_border="#E0E0E0",
                # Nuevos colores
                assistant_bubble="#F8F9FA",
                user_bubble="#E8F0FE",
                bubble_shadow="rgba(0, 0, 0, 0.1)",
                icon_button="#1A73E8",
                icon_button_hover="#1557B0",
                mic_active="#EA4335",
                card_border="rgba(0, 0, 0, 0.12)"
            )
        }
