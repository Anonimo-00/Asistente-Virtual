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
from global_vars import get_global_var, set_global_var
from .config_window import ConfigWindow  # Cambiar esta línea - importación correcta
from .settings_view import SearchSettingsView  # Moved after flet imports
from .components.chat_bubble import ChatBubble
from .components.input_bar import InputBar

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
            bg_primary="#121212",
            bg_secondary="#1E1E1E",
            accent="#8ab4f8",
            text_primary="#FFFFFF",
            text_secondary="#B3B3B3",
            surface="#2D2D2D",
            error="#CF6679",
            success="#03DAC6"
        ),
        "light": UITheme(
            bg_primary="#FFFFFF",
            bg_secondary="#F8F9FA",
            accent="#1A73E8",
            text_primary="#202124",
            text_secondary="#5F6368",
            surface="#FFFFFF",
            error="#B00020",
            success="#0F9D58"
        )
    }

    def toggle_theme(self, e):
        """Toggle de tema optimizado con actualización completa"""
        try:
            new_theme = "dark" if e.control.value else "light"
            if new_theme == self.config.theme_mode:
                return
                
            # Actualizar tema en todos los niveles
            self.config.theme_mode = new_theme
            self._theme_color_cache.clear()
            set_global_var("theme_mode", new_theme)
            
            # Actualizar página
            self.page.theme_mode = getattr(ft.ThemeMode, new_theme.upper())
            self.page.bgcolor = self.get_theme_color("bg_primary")
            
            # Actualizar todos los componentes recursivamente
            self._update_component_colors(self.page)
            
            # Guardar en preferencias
            UserManager().guardar_dato("preferencias", "tema", new_theme)
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error cambiando tema: {e}")

    def _update_component_colors(self, component):
        """Actualiza recursivamente los colores de todos los componentes"""
        try:
            if hasattr(component, 'controls'):
                for control in component.controls:
                    self._update_component_colors(control)
                    
            # Actualizar colores según el tipo de componente
            if isinstance(component, ft.Container):
                component.bgcolor = self.get_theme_color("bg_secondary")
            elif isinstance(component, ft.Text):
                component.color = self.get_theme_color("text_primary")
            elif isinstance(component, ft.IconButton):
                component.icon_color = self.get_theme_color("accent")
            elif isinstance(component, ft.TextField):
                component.bgcolor = self.get_theme_color("input_bg")
                component.color = self.get_theme_color("input_text")
            
            # Actualizar propiedades especiales
            if hasattr(component, 'gradient'):
                component.gradient.colors = [
                    self.get_theme_color("bg_primary"),
                    self.get_theme_color("bg_secondary")
                ]
                
        except Exception as e:
            logger.error(f"Error actualizando colores: {e}")

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
        self._theme_color_cache = {}
        self._last_theme_mode = None

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
            
            # Obtener tema de variables globales primero
            theme = get_global_var("theme_mode") or user_manager.obtener_dato("preferencias", "tema") or "dark"
            
            if theme != self.config.theme_mode:
                self.config.theme_mode = theme
                self.page.theme_mode = theme.upper()
                self.page.bgcolor = "#1E1E1E" if theme == "dark" else "#F5F5F5"
                set_global_var("theme_mode", theme)
            
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
                ft.Text(
                    "Configuración",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=self.get_theme_color("text_primary")
                ),
                ft.Divider(color=self.get_theme_color("divider")),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Tema",
                            size=16,
                            color=self.get_theme_color("text_primary")
                        ),
                        ft.Switch(
                            label="Modo oscuro",
                            value=self.config.theme_mode == "dark",
                            on_change=self.toggle_theme,
                        ),
                    ]),
                    padding=10,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Voz",
                            size=16,
                            color=self.get_theme_color("text_primary")
                        ),
                        ft.Switch(
                            label="Activar voz",
                            value=self.config.enable_voice,
                            on_change=self.toggle_voice,
                        ),
                    ]),
                    padding=10,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Tamaño de fuente",
                            size=16,
                            color=self.get_theme_color("text_primary")
                        ),
                        ft.Row([
                            ft.Icon(
                                ft.icons.FORMAT_SIZE,
                                color=self.get_theme_color("text_secondary")
                            ),
                            ft.Slider(  # Slider corregido
                                min=12,
                                max=24,
                                value=self.config.font_size,
                                on_change=self.change_font_size,
                                expand=True,
                                active_color=self.get_theme_color("accent"),
                                inactive_color=self.get_theme_color("divider")
                            ),
                        ]),
                    ]),
                    padding=10,
                ),
                self.search_settings,
            ]),
            padding=20,
            bgcolor=self.get_theme_color("settings_bg"),
            border=ft.border.all(
                color=self.get_theme_color("settings_border"),
                width=1
            ),
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
        try:
            self.chat_container = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

            self.input_bar = InputBar(
                self.page,
                on_submit=self.send_message,
                on_voice=self.toggle_voice_input
            )

            main_view = ft.Column([
                self.chat_container,
                self.input_bar
            ], expand=True)

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
        """Actualiza el layout y espaciado de mensajes de forma optimizada"""
        try:
            if not hasattr(self, 'page') or not self.page:
                return
                
            available_width = self.page.width or self.config.max_width
            max_width = min(available_width, self.config.max_width)
            message_width = max_width * (0.9 if available_width < 600 else self.config.message_width_ratio)
            
            # Actualizar solo si hay cambios
            if hasattr(self, '_last_width') and self._last_width == message_width:
                return
                
            self._last_width = message_width
            
            # Batch updates para mejor rendimiento
            updates_needed = False
            
            if self.chat_container and self.chat_container.width != available_width:
                self.chat_container.width = available_width
                updates_needed = True
            
            # Actualizar mensajes solo si necesario
            for msg in self.chat_history.controls:
                if hasattr(msg, 'content'):
                    if msg.width != message_width:
                        msg.width = message_width
                        updates_needed = True
                    if hasattr(msg.content, 'content'):
                        if msg.content.width != message_width:
                            msg.content.width = message_width
                            updates_needed = True
            
            if updates_needed:
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
        """Envío de mensajes optimizado y con mejor manejo de errores"""
        if not hasattr(self, 'input_field') or not self.input_field:
            return
            
        message = (self.input_field.value or "").strip()
        if not message:
            return
            
        try:
            # Desactivar campo de entrada mientras procesa
            self.input_field.disabled = True
            self.send_button.disabled = True
            self.page.update()
            
            # Procesar mensaje
            self.input_field.value = ""
            self.state.add_message(message, is_user=True)
            self.add_message_to_chat(message, is_user=True)
            
            # Obtener respuesta con timeout
            try:
                response = await asyncio.wait_for(
                    self.nlp_service.process_input(message),
                    timeout=10.0
                )
                
                if response and isinstance(response, str):
                    self.state.add_message(response, is_user=False)
                    self.add_message_to_chat(response, is_user=False)
                else:
                    raise ValueError("Respuesta inválida")
                    
            except asyncio.TimeoutError:
                self.add_message_to_chat(
                    "Lo siento, tardé demasiado en responder. Por favor intenta de nuevo.",
                    is_user=False
                )
                
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            self.add_message_to_chat(
                "Ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo.",
                is_user=False
            )
            
        finally:
            # Reactivar campos
            self.input_field.disabled = False
            self.send_button.disabled = False
            self.page.update()

    def add_message_to_chat(self, message: str, is_user: bool):
        card = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(
                                ft.icons.PERSON if is_user else ft.icons.ASSISTANT,
                                color=self.get_theme_color("accent"),
                                size=24
                            ),
                            margin=ft.margin.only(right=12),
                            padding=8,
                            border_radius=20,
                            bgcolor=self.get_theme_color("surface")
                        ),
                        ft.Text(
                            message,
                            size=16,
                            color=self.get_theme_color("text_primary"),
                            selectable=True,
                            weight=ft.FontWeight.W_400
                        )
                    ]),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.COPY,
                                icon_color=self.get_theme_color("accent"),
                                tooltip="Copiar",
                                on_click=lambda _: self.page.set_clipboard(message)
                            ) if not is_user else ft.Container()
                        ],
                        alignment=ft.MainAxisAlignment.END
                    ) if not is_user else ft.Container()
                ]),
                padding=16
            ),
            margin=ft.margin.only(
                left=40 if is_user else 0,
                right=0 if is_user else 40,
                bottom=8
            ),
            border_radius=20,
            bgcolor=self.get_theme_color("card_bg"),
            animate=ft.animation.Animation(300, "easeOut"),
            animate_opacity=300,
            animate_position=ft.animation.Animation(300, "easeOut"),
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
        """Obtiene el color del tema actual con cache"""
        cache_key = f"{self.config.theme_mode}_{color_name}"
        if cache_key in self._theme_color_cache:
            return self._theme_color_cache[cache_key]
            
        theme_data = self.config.themes.get(
            self.config.theme_mode.lower(),
            self.config.themes["light"]
        )
        color = getattr(theme_data, color_name, "#000000")
        self._theme_color_cache[cache_key] = color
        return color

    def toggle_theme(self, e):
        """Toggle de tema optimizado con actualización inmediata"""
        try:
            new_theme = "dark" if e.control.value else "light"
            
            # Evitar cambios innecesarios
            if new_theme == self.config.theme_mode:
                return
                
            # Actualizar configuración local y limpiar cache
            self.config.theme_mode = new_theme
            self._theme_color_cache.clear()
            
            # Actualizar variable global y preferencias
            set_global_var("theme_mode", new_theme)
            UserManager().guardar_dato("preferencias", "tema", new_theme)
            
            # Actualizar página inmediatamente
            self.page.theme_mode = getattr(ft.ThemeMode, new_theme.upper())
            self.page.bgcolor = self.get_theme_color("bg_primary")
            
            # Actualizar elementos principales inmediatamente
            self._quick_theme_update()
            
            # Actualizar el resto de componentes en segundo plano
            threading.Thread(target=self._background_theme_update, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error cambiando tema: {e}")

    def _quick_theme_update(self):
        """Actualización rápida de elementos críticos"""
        try:
            # Actualizar contenedor principal
            self.chat_container.bgcolor = self.get_theme_color("bg_primary")
            
            # Actualizar barra de entrada
            self.input_field.bgcolor = self.get_theme_color("input_bg")
            self.input_field.color = self.get_theme_color("text_primary")
            
            # Actualizar botones principales
            for btn in [self.mic_button, self.send_button, self.settings_button]:
                btn.icon_color = self.get_theme_color("accent")
            
            # Forzar actualización inmediata
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error en actualización rápida: {e}")

    def _background_theme_update(self):
        """Actualización completa en segundo plano"""
        try:
            # Actualizar gradientes
            self.chat_container.gradient.colors = [
                self.get_theme_color("bg_primary"),
                self.get_theme_color("bg_secondary")
            ]
            
            # Actualizar mensajes
            for msg in self.chat_history.controls:
                if isinstance(msg, ft.Container):
                    self._update_message_colors(msg)
            
            # Actualizar configuración y otros elementos
            self.settings_view.bgcolor = self.get_theme_color("settings_bg")
            self.update_component_themes()
            
            # Actualizar layout
            self.update_layout()
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error en actualización de fondo: {e}")

    def _update_message_colors(self, msg_container):
        """Actualiza los colores de un mensaje específico"""
        try:
            msg_container.bgcolor = self.get_theme_color("card_bg")
            
            if hasattr(msg_container, 'content') and isinstance(msg_container.content, ft.Container):
                for control in msg_container.content.content.controls:
                    if isinstance(control, ft.Row):
                        for item in control.controls:
                            if isinstance(item, ft.Text):
                                item.color = self.get_theme_color("text_primary")
                            elif isinstance(item, ft.Container):
                                if isinstance(item.content, ft.Icon):
                                    item.content.color = self.get_theme_color("accent")
                                item.bgcolor = self.get_theme_color("surface")
        except Exception as e:
            logger.error(f"Error actualizando colores de mensaje: {e}")

    def update_component_themes(self):
        """Actualiza los temas de todos los componentes"""
        try:
            components_to_update = {
                "bg": [self.chat_container, self.settings_view],
                "accent": [self.mic_button, self.send_button, self.settings_button],
                "text": [control for control in self.chat_history.controls if isinstance(control, ft.Text)],
                "surface": [self.input_field]
            }
            
            for component_type, components in components_to_update.items():
                color = self.get_theme_color({
                    "bg": "bg_secondary",
                    "accent": "accent",
                    "text": "text_primary",
                    "surface": "surface"
                }[component_type])
                
                for component in components:
                    if hasattr(component, 'bgcolor'):
                        component.bgcolor = color
                    if hasattr(component, 'color'):
                        component.color = color
                    if hasattr(component, 'icon_color'):
                        component.icon_color = color
            
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error actualizando temas de componentes: {e}")

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
            padding=20,
            margin=ft.margin.only(left=20, right=20, bottom=20),
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

    def add_message(self, message: str, is_user: bool):
        bubble = ChatBubble(self.page, message, is_user)
        self.chat_container.controls.append(bubble)
        self.page.update()
