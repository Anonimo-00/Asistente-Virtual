import flet as ft
import logging
import time
from services.nlp.nlp_service import NLPService
from utils.state_manager import StateManager
from utils.user_manager import UserManager
from typing import Optional, Dict
from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3
import threading
import queue
import urllib.request
from global_vars import get_global_var
from .config_window import ConfigWindow  # Cambiar esta línea - importación correcta
from .settings_view import SearchSettingsView  # Moved after flet imports

logger = logging.getLogger(__name__)

class UITheme(BaseModel):
    bg_primary: str
    bg_secondary: str
    accent: str
    text_primary: str
    text_secondary: str
    surface: str
    error: str
    success: str

class UISpacing(BaseModel):
    chat_padding: int = 20
    message_spacing: int = 12
    input_padding: int = 16

class UIBorderRadius(BaseModel):
    message: int = 20
    input: int = 24
    button: int = 12

class UIConfig(BaseModel):
    max_width: int = 1200
    min_width: int = 400
    message_width_ratio: float = 0.85
    theme_mode: str = "dark"
    enable_voice: bool = True
    voice_lang: str = "es"
    font_size: int = 16
    accent_color: str = "blue"
    message_spacing: int = 10
    spacing: UISpacing = UISpacing()
    border_radius: UIBorderRadius = UIBorderRadius()
    themes: Dict[str, UITheme] = {
        "dark": UITheme(
            bg_primary="#ffffff",
            bg_secondary="#f8f9fa",
            accent="#4285f4",
            text_primary="#202124",
            text_secondary="#5f6368",
            surface="#e8eaed",
            error="#d93025",
            success="#188038"
        ),
        "light": UITheme(
            bg_primary="#ffffff",
            bg_secondary="#f8f9fa",
            accent="#1a73e8",
            text_primary="#202124",
            text_secondary="#5f6368",
            surface="#e8eaed",
            error="#d93025",
            success="#188038"
        )

    }

class FleetApp:
    def __init__(self, nlp_service):
        self.nlp_service = nlp_service
        self.state = StateManager()
        self.page = None
        self.config = UIConfig()
        self.chat_history = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            auto_scroll=True
        )
        self.input_field = ft.TextField(
            label="Mensaje",
            expand=True,
            shift_enter=True,
            on_submit=self.send_message,
            border_radius=20,
            filled=True,
            bgcolor=ft.colors.WHITE10,
        )
        self.mic_button = ft.IconButton(
            ft.icons.MIC,
            on_click=self.toggle_voice_input,
            icon_color=ft.colors.BLUE_400,
            tooltip="Iniciar entrada de voz"
        )


        self.send_button = ft.IconButton(
            ft.icons.SEND_ROUNDED,
            on_click=self.send_message,
            icon_color=ft.colors.BLUE_400
        )
        self.voice_queue = queue.Queue()
        self.voice_thread = None
        self.settings_visible = False
        self.check_internet_connection()
        if UIConfig().enable_voice:
            self.init_voice_components()
            self.start_voice_processor()
        self.check_connection_timer = None
        self.chat_container = None
        self.last_wifi_status = None
        self.connection_check_active = True
        self.connection_thread = None
        self.config_window = None  # Mover esta línea aquí
        self.settings_button = ft.IconButton(
            icon=ft.icons.SETTINGS,
            on_click=self.toggle_settings,
            icon_color=ft.colors.BLUE_400,
            tooltip="Configuración"
        )
        self.connection_icon_online = ft.Icon(
            ft.icons.CLOUD_DONE,
            color=ft.colors.GREEN_400,
            visible=self.is_online
        )
        self.connection_icon_offline = ft.Icon(
            ft.icons.CLOUD_OFF,
            color=ft.colors.RED_400,
            visible=not self.is_online
        )
        self.search_settings = SearchSettingsView(save_callback=self._on_settings_saved)

    def check_internet_connection(self):
        self.is_online = get_global_var("wifi_status")

    def start_connection_checker(self):
        def check_periodically():
            while self.connection_check_active and hasattr(self, 'page'):
                try:
                    self.check_internet_connection()
                    self.update_connection_status()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error en connection checker: {e}")
                    time.sleep(1)

        self.connection_thread = threading.Thread(target=check_periodically, daemon=True)
        self.connection_thread.start()

    def update_connection_status(self):
        if not hasattr(self, 'connection_icon_online') or not self.page:
            return
            
        try:
            current_status = get_global_var("wifi_status")
            if current_status != self.last_wifi_status:
                self.connection_icon_online.visible = current_status
                self.connection_icon_offline.visible = not current_status
                self.last_wifi_status = current_status
                self.page.update()
                logger.info(f"Estado de conexión actualizado: {'Conectado' if current_status else 'Desconectado'}")
        except Exception as e:
            logger.error(f"Error actualizando estado de conexión: {e}")

    def init_voice_components(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', 'spanish')
        self.voice_active = True
        
        self.mic_button = ft.IconButton(
            ft.icons.MIC,
            on_click=self.toggle_voice_input,
            icon_color=ft.colors.BLUE_400
        )

    def start_voice_processor(self):
        def process_voice_queue():
            while self.voice_active:
                try:
                    message = self.voice_queue.get()
                    if message:
                        self.engine.say(message)
                        self.engine.runAndWait()
                    self.voice_queue.task_done()
                except Exception as e:
                    logger.error(f"Error procesando mensaje de voz: {e}")
                    
        self.voice_thread = threading.Thread(target=process_voice_queue, daemon=True)
        self.voice_thread.start()

    def toggle_voice_input(self, e):
        def listen_thread():
            try:
                with sr.Microphone() as source:
                    self.mic_button.icon_color = ft.colors.RED_400
                    self.page.update()
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio, language="es-ES")
                    self.input_field.value = text
                    self.send_message(None)
            except Exception as e:
                logger.error(f"Error en entrada de voz: {e}")
            finally:
                self.mic_button.icon_color = ft.colors.BLUE_400
                self.page.update()

        threading.Thread(target=listen_thread, daemon=True).start()

    def run(self):
        """Método de inicio simplificado"""
        ft.app(target=self.main, view=ft.AppView.NATIVE)

    async def run_async(self):
        """Versión asíncrona del método run"""
        await ft.app_async(target=self.main)

    def toggle_settings(self, e):
        """Muestra/oculta la ventana de configuración"""
        try:
            if not self.config_window:
                self.config_window = ConfigWindow(self.page, on_close=self.on_config_close)
            
            # Bloquear botón
            self.settings_button.disabled = True
            self.page.update()
            
            # Mostrar config
            self.config_window.show()
            
            # Desbloquear después de breve delay
            def enable_button():
                time.sleep(0.3)
                self.settings_button.disabled = False
                self.page.update()
            
            threading.Thread(target=enable_button, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error mostrando configuración: {e}")
            self.settings_button.disabled = False
            self.page.update()

    def on_config_close(self):
        # Actualizar la UI con las nuevas configuraciones
        self._load_user_preferences()
        self.page.update()

    def _load_user_preferences(self):
        """Carga y aplica preferencias de forma optimizada"""
        try:
            user_manager = UserManager()
            theme = user_manager.obtener_dato("preferencias", "tema") or "dark"
            
            # Aplicar tema solo si ha cambiado
            if theme != self.config.theme_mode:
                self.config.theme_mode = theme
                self.page.theme_mode = theme.upper()
                self.page.bgcolor = "#1E1E1E" if theme == "dark" else "#F5F5F5"
                
            # Actualizar otras preferencias
            self.config.font_size = user_manager.obtener_dato("preferencias", "tamano_fuente") or 16
            voice_enabled = user_manager.obtener_dato("preferencias", "voz_activada") or False
            
            if voice_enabled != self.config.enable_voice:
                self.config.enable_voice = voice_enabled
                if voice_enabled and not hasattr(self, 'engine'):
                    self.init_voice_components()
                    self.start_voice_processor()
                elif not voice_enabled and hasattr(self, 'engine'):
                    self.voice_active = False
            
            self.page.update()
        except Exception as e:
            logger.error(f"Error cargando preferencias: {e}")

    def create_settings_view(self):
        return ft.Container(
            visible=False,
            content=ft.Column([
                ft.Text("Configuración", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Switch(label="Modo oscuro", value=self.config.theme_mode == "dark",
                         on_change=self.toggle_theme),
                ft.Switch(label="Voz activada", value=self.config.enable_voice,
                         on_change=self.toggle_voice),
                ft.Slider(
                    label="Tamaño de fuente",
                    min=12,
                    max=24,
                    value=self.config.font_size,
                    on_change=self.change_font_size
                ),
                self.search_settings,
            ]),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
            margin=10,
        )

    def main(self, page: ft.Page):
        try:
            self.page = page
            # Configuración básica de la página
            page.title = "Central Assistant"
            page.window_width = self.config.max_width
            page.window_min_width = 400
            page.theme_mode = getattr(ft.ThemeMode, self.config.theme_mode.upper())
            page.padding = 0
            page.bgcolor = self.get_theme_color("bg_primary")
            
            # Inicializar UI
            self.initialize_ui()
            
            # Iniciar verificación de conexión
            self.start_connection_checker()
            
            # Cargar preferencias
            self._load_user_preferences()
            
            # Actualizar la página
            page.update()
            
        except Exception as e:
            logger.error(f"Error inicializando la UI: {e}", exc_info=True)
            raise

    def initialize_ui(self):
        """Inicialización separada de la UI"""
        try:
            # Barra superior con acciones
            appbar = ft.AppBar(
                leading=ft.Icon(ft.icons.CHAT_ROUNDED),
                title=ft.Text("Central Assistant", size=20, weight=ft.FontWeight.BOLD),
                center_title=False,
                bgcolor=self.get_theme_color("bg_secondary"),
                elevation=0.5,
                actions=[
                    self.settings_button,
                    self.connection_icon_online,
                    self.connection_icon_offline,
                ],
            )

            # Barra de entrada flotante estilo Google Assistant
            input_container = ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ASSISTANT,
                            icon_color=self.get_theme_color("accent"),
                            icon_size=24,
                            tooltip="Assistant"
                        ),
                        self.input_field,
                        self.mic_button,
                        self.send_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8
                ),
                padding=20,
                margin=ft.margin.only(left=20, right=20, bottom=20),
                bgcolor=self.get_theme_color("bg_secondary"),
                border_radius=28,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                    offset=ft.Offset(0, 2)
                )
            )

            # Contenedor del chat con fondo degradado
            chat_container = ft.Container(
                content=ft.Column([
                    self.chat_history,
                    input_container
                ]),
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[
                        self.get_theme_color("bg_primary"),
                        self.get_theme_color("bg_secondary")
                    ]
                )
            )
            self.chat_container = chat_container

            # Vista de configuración
            self.settings_view = self.create_settings_view()
            
            # Contenedor principal
            main_content = ft.Row(
                [
                    chat_container,
                    self.settings_view
                ],
                expand=True,
            )

            self.page.add(appbar, main_content)
            self.page.on_resize = self.on_page_resize
            self.page.on_close = self.on_close

            self.update_layout()
            
        except Exception as e:
            logger.error(f"Error en initialize_ui: {e}")
            raise

    def on_page_resize(self, e):
        if self.page.width < 600:
            self.settings_view.visible = False
            self.settings_visible = False
        self.update_layout()
        self.page.update()

    def update_layout(self):
        """Actualiza el layout y espaciado de mensajes"""
        try:
            available_width = self.page.width if self.page else self.config.max_width
            max_width = min(available_width, self.config.max_width)
            message_width = max_width * (0.9 if available_width < 600 else self.config.message_width_ratio)
            
            # Actualizar contenedor del chat
            if self.chat_container:
                self.chat_container.width = available_width
                
            # Actualizar mensajes
            for msg in self.chat_history.controls:
                if hasattr(msg, 'content'):
                    msg.width = message_width
                    if hasattr(msg.content, 'content'):
                        msg.content.width = message_width
                        
            # Ajustar espaciado
            self.chat_history.spacing = self.config.message_spacing
            
            # Actualizar campo de entrada
            if hasattr(self, 'input_field'):
                self.input_field.width = available_width * 0.8
                
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error actualizando layout: {e}")

    def update_settings_view(self):
        if hasattr(self, 'settings_view'):
            self.settings_view.visible = self.settings_visible
            if self.page.width < 600:
                self.settings_view.width = self.page.width
                self.settings_view.height = self.page.height
                self.settings_view.offset = ft.Offset(0, 0 if self.settings_visible else 1)
            else:
                self.settings_view.width = min(300, self.page.width * 0.3)
                self.chat_container.width = (self.page.width - self.settings_view.width 
                                          if self.settings_visible else self.page.width)
            self.page.update()

    async def send_message(self, e):
        message = self.input_field.value.strip()
        if not message:
            return
            
        try:
            # Limpiar el campo de entrada
            self.input_field.value = ""
            self.page.update()
            
            # Guardar mensaje en el estado
            self.state.add_message(message, is_user=True)
            
            # Mostrar mensaje del usuario
            self.add_message_to_chat(message, is_user=True)
            
            # Procesar y mostrar respuesta
            response = await self.nlp_service.process_input(message)
            if response and isinstance(response, str):
                self.state.add_message(response, is_user=False)
                self.add_message_to_chat(response, is_user=False)
            else:
                error_msg = "Lo siento, hubo un error al procesar tu mensaje."
                self.state.add_message(error_msg, is_user=False)
                self.add_message_to_chat(error_msg, is_user=False)
                
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            error_msg = "Error al procesar el mensaje."
            self.state.add_message(error_msg, is_user=False)
            self.add_message_to_chat(error_msg, is_user=False)
            self.page.update()

    def add_message_to_chat(self, message: str, is_user: bool):
        """Crear tarjeta de mensaje estilo Google Assistant"""
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Icono y contenido
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(
                                ft.icons.PERSON if is_user else ft.icons.ASSISTANT,
                                color=self.get_theme_color("accent"),
                                size=20
                            ),
                            margin=ft.margin.only(right=12)
                        ),
                        ft.Text(
                            message,
                            size=16,
                            color=self.get_theme_color("text_primary"),
                            selectable=True,
                            weight=ft.FontWeight.W_400
                        )
                    ]),
                    # Acciones opcionales
                    ft.Row(
                        [
                            ft.TextButton(
                                "Copiar",
                                icon=ft.icons.COPY,
                                on_click=lambda _: self.page.set_clipboard(message)
                            ) if not is_user else ft.Container()
                        ],
                        alignment=ft.MainAxisAlignment.END
                    ) if not is_user else ft.Container()
                ]),
                padding=16
            ),
            elevation=0,
            color=self.get_theme_color("card_bg"),
            margin=ft.margin.symmetric(horizontal=is_user and 40 or 0),
            surface_tint_color=self.get_theme_color("accent" if is_user else "surface")
        )

        # Animar entrada
        card.opacity = 0
        card.offset = ft.transform.Offset(0, 0.5)
        self.chat_history.controls.append(card)
        
        def animate():
            time.sleep(0.05)
            card.opacity = 1
            card.offset = ft.transform.Offset(0, 0)
            self.page.update()

        threading.Thread(target=animate, daemon=True).start()

    def get_theme_color(self, color_name: str) -> str:
        """Obtiene el color del tema actual"""
        theme_data = self.config.themes.get(
            self.config.theme_mode.lower(),
            self.config.themes["light"]
        )
        return getattr(theme_data, color_name, "#000000")

    def toggle_theme(self, e):
        """Cambia entre modo claro y oscuro"""
        try:
            # Cambiar modo
            self.config.theme_mode = "dark" if e.control.value else "light"
            self.page.theme_mode = getattr(ft.ThemeMode, self.config.theme_mode.upper())
            
            # Actualizar colores principales
            self.page.bgcolor = self.get_theme_color("bg_primary")
            self.page.update()
            
            # Actualizar todos los componentes
            self.initialize_ui()
            self.update_layout()
            
            # Guardar preferencia
            user_manager = UserManager()
            user_manager.guardar_dato("preferencias", "tema", self.config.theme_mode)
            
        except Exception as e:
            logger.error(f"Error cambiando tema: {e}")

    def toggle_voice(self, e):
        self.config.enable_voice = e.control.value
        if self.config.enable_voice and not hasattr(self, 'engine'):
            self.init_voice_components()
            self.start_voice_processor()

    def change_font_size(self, e):
        self.config.font_size = int(e.control.value)
        self.update_layout()
        self.page.update()

    def on_close(self, e):
        self.voice_active = False
        self.connection_check_active = False
        if hasattr(self, 'engine'):
            self.engine.stop()
        if self.connection_thread:
            self.connection_thread.join(timeout=1)

    def _on_settings_saved(self):
        """Callback cuando se guardan las configuraciones"""
        self.nlp_service.reload_config()
        self.update()

    def create_message_card(self, message: str, is_user: bool) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.icons.PERSON if is_user else ft.icons.ASSISTANT,
                            color=self.get_theme_color("accent"),
                            size=24
                        ),
                        margin=ft.margin.only(right=16),
                        padding=8,
                        border_radius=20,
                        bgcolor=self.get_theme_color("surface")
                    ),
                    ft.Container(
                        content=ft.Text(
                            message,
                            size=16,
                            color=self.get_theme_color("text_primary"),
                            selectable=True,
                            weight=ft.FontWeight.W_400,
                            text_align=ft.TextAlign.LEFT
                        ),
                        expand=True,
                        bgcolor=self.get_theme_color("card_bg"),
                        border_radius=12,
                        padding=16
                    )
                ]),
                # ...existing code...
            ]),
            # ...existing code...
        )

    def create_input_bar(self) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.ASSISTANT,
                    icon_color=self.get_theme_color("accent"),
                    icon_size=24,
                    tooltip="Assistant",
                    bgcolor=self.get_theme_color("button_bg"),
                    hover_color=self.get_theme_color("hover")
                ),
                ft.TextField(
                    ref=self.input_field,
                    hint_text="Escribe un mensaje...",
                    border_radius=24,
                    filled=True,
                    expand=True,
                    text_size=16,
                    bgcolor=self.get_theme_color("input_bg"),
                    color=self.get_theme_color("input_text"),
                    cursor_color=self.get_theme_color("accent"),
                    border_color="transparent",
                    focused_border_color=self.get_theme_color("accent"),
                    hint_style=ft.TextStyle(
                        color=self.get_theme_color("text_secondary")
                    )
                ),
                self.mic_button,
                self.send_button
            ], spacing=8),
            # ...existing code...
        )

    def create_elevation_shadow(self, elevation: int) -> ft.BoxShadow:
        color = self.get_theme_color("shadow")
        return ft.BoxShadow(
            spread_radius=0,
            blur_radius=elevation * 4,
            color=color,
            offset=ft.Offset(0, elevation)
        )

    async def start_connection_checker_async(self):
        """Versión asíncrona del checker de conexión"""
        while self.connection_check_active and hasattr(self, 'page'):
            try:
                await self.check_internet_connection_async()
                await self.update_connection_status_async()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error en connection checker: {e}")
                await asyncio.sleep(1)
