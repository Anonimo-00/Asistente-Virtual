import flet as ft
from typing import Callable
import yaml

class SearchSettingsView(ft.View):  # Cambiado de ft.UserControl a ft.View
    def __init__(self, save_callback: Callable = None):
        super().__init__()
        self.save_callback = save_callback
        self._load_config()

    def _load_config(self):
        try:
            with open('config/credentials.yml', 'r') as f:
                self.config = yaml.safe_load(f)
                self.search_config = self.config.get('search', {})
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config = {}
            self.search_config = {}

    def build(self):
        # Engine selector
        self.engine_dropdown = ft.Dropdown(
            label="Motor de búsqueda",
            value=self.search_config.get('engines', {}).get('current', 'google'),
            options=[
                ft.dropdown.Option("google", "Google"),
                ft.dropdown.Option("bing", "Bing"),
                ft.dropdown.Option("duckduckgo", "DuckDuckGo"),
            ],
            width=200,
        )

        # User agent configuration
        self.agent_type = ft.Dropdown(
            label="Tipo de Agente",
            value=self.search_config.get('user_agents', {}).get('current', 'chrome'),
            options=[
                ft.dropdown.Option("chrome", "Chrome"),
                ft.dropdown.Option("firefox", "Firefox"),
                ft.dropdown.Option("edge", "Edge"),
                ft.dropdown.Option("mobile", "Mobile"),
            ],
            width=200,
        )

        self.agent_input = ft.TextField(
            label="User Agent personalizado",
            multiline=True,
            width=400,
            height=100,
        )

        self.rotate_agents = ft.Checkbox(
            label="Rotar User Agents automáticamente",
            value=self.search_config.get('user_agents', {}).get('rotate', True),
        )

        self.rotation_interval = ft.TextField(
            label="Intervalo de rotación (búsquedas)",
            value=str(self.search_config.get('user_agents', {}).get('interval', 10)),
            width=200,
        )

        save_button = ft.ElevatedButton(
            text="Guardar cambios",
            on_click=self._save_config
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Configuración de Búsqueda", size=20, weight=ft.FontWeight.BOLD),
                self.engine_dropdown,
                ft.Divider(),
                ft.Text("Configuración de User Agent", size=16),
                self.agent_type,
                self.agent_input,
                self.rotate_agents,
                self.rotation_interval,
                save_button,
            ]),
            padding=20
        )

    def _save_config(self, e):
        try:
            # Actualizar configuración
            if 'search' not in self.config:
                self.config['search'] = {}
            
            self.config['search']['engines']['current'] = self.engine_dropdown.value
            
            if 'user_agents' not in self.config['search']:
                self.config['search']['user_agents'] = {}
            
            ua_config = self.config['search']['user_agents']
            ua_config['current'] = self.agent_type.value
            ua_config['rotate'] = self.rotate_agents.value
            ua_config['interval'] = int(self.rotation_interval.value)
            
            # Agregar nuevo user agent si se especificó
            if self.agent_input.value:
                if self.agent_type.value not in ua_config['agents']:
                    ua_config['agents'][self.agent_type.value] = []
                ua_config['agents'][self.agent_type.value].append(self.agent_input.value)

            # Guardar en archivo
            with open('config/credentials.yml', 'w') as f:
                yaml.safe_dump(self.config, f)

            if self.save_callback:
                self.save_callback()
                
            # Mostrar mensaje de éxito
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Configuración guardada")))
            
        except Exception as e:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error guardando configuración: {e}")))
