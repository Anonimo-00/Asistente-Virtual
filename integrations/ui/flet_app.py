import flet as ft
import logging
import time
from services.nlp.nlp_service import NLPService
from utils.state_manager import StateManager
from utils.user_manager import UserManager
from typing import Optional
from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3
import threading
import queue
import urllib.request
from global_vars import get_global_var
from .config_window import ConfigWindow  # Cambiar esta línea - importación correcta

logger = logging.getLogger(__name__)

class UIConfig(BaseModel):
    max_width: int = 800
    message_width_ratio: float = 0.7
    theme_mode: str = "dark"
    enable_voice: bool = True
    voice_lang: str = "es"
    font_size: int = 16
    accent_color: str = "blue"
    message_spacing: int = 10

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
        ft.app(target=self.main)

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
            ]),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
            margin=10,
        )

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Asistente Virtual"
        page.window_width = self.config.max_width
        page.window_min_width = 400
        page.theme_mode = getattr(ft.ThemeMode, self.config.theme_mode.upper())
        page.padding = 0
        page.bgcolor = ft.colors.SURFACE_VARIANT

        appbar = ft.AppBar(
            leading=ft.Icon(ft.icons.CHAT_ROUNDED),
            title=ft.Text("Asistente Virtual", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            elevation=0.5,
            actions=[
                self.settings_button,
                self.connection_icon_online,
                self.connection_icon_offline,
            ],
        )
        
        input_row = [self.input_field, self.send_button]
        if hasattr(self, 'mic_button'):
            input_row.append(self.mic_button)
        
        chat_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.chat_history,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=15),
                ),
                ft.Container(
                    content=ft.Row(
                        input_row,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(15),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border=ft.border.only(top=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT)),
                )
            ]),
            expand=True,
        )
        self.chat_container = chat_container

        self.settings_view = self.create_settings_view()
        main_content = ft.Row(
            [
                ft.Container(
                    content=chat_container,
                    expand=True,
                ),
                self.settings_view
            ],
            expand=True,
        )

        page.add(appbar, main_content)
        page.on_resize = self.on_page_resize
        page.on_close = self.on_close

        self.start_connection_checker()
        self._load_user_preferences()

    def on_page_resize(self, e):
        if self.page.width < 600:
            self.settings_view.visible = False
            self.settings_visible = False
        self.update_layout()
        self.page.update()

    def update_layout(self):
        max_width = min(self.page.width, self.config.max_width)
        for msg in self.chat_history.controls:
            msg.width = max_width * self.config.message_width_ratio

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

    def send_message(self, e):
        message = self.input_field.value
        if not message:
            return
        self.input_field.value = ""
        self.add_message_to_chat(message, is_user=True)
        response = self.nlp_service.process_input(message)
        self.add_message_to_chat(response, is_user=False)
        self.page.update()

    def add_message_to_chat(self, message, is_user):
        max_width = min(
            self.page.width * self.config.message_width_ratio if self.page else 300,
            self.config.max_width * self.config.message_width_ratio
        )
        
        # Determinar colores basados en el tema
        is_dark = self.page.theme_mode == "DARK"
        text_color = ft.colors.WHITE if is_user or is_dark else ft.colors.BLACK
        bg_color = (ft.colors.BLUE_700 if is_user else 
                   (ft.colors.SURFACE_VARIANT if is_dark else ft.colors.WHITE))
        
        msg_container = ft.Container(
            content=ft.Text(
                value=message,
                size=self.config.font_size,
                color=text_color,
                selectable=True,
                weight=ft.FontWeight.W_400,
                overflow=ft.TextOverflow.CLIP,
                text_align=ft.TextAlign.LEFT,
            ),
            bgcolor=bg_color,
            border_radius=ft.border_radius.all(15),
            padding=ft.padding.all(15),
            width=max_width,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color=ft.colors.BLACK12,
                offset=ft.Offset(0, 2),
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            offset=ft.transform.Offset(0, 0.5),
        )

        wrapper = ft.Container(
            content=msg_container,
            alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
            margin=ft.margin.symmetric(vertical=4, horizontal=20),
            width=self.page.width * self.config.message_width_ratio if self.page else 300,
        )

        try:
            self.chat_history.controls.append(wrapper)
            self.state.add_message(message, is_user)
            
            # Animación con threading
            def animate_message():
                time.sleep(0.05)  # Pequeño delay para la animación
                msg_container.opacity = 1
                msg_container.offset = ft.transform.Offset(0, 0)
                self.page.update()
            
            threading.Thread(target=animate_message, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error al agregar mensaje: {e}")

        if not is_user and self.config.enable_voice:
            self.voice_queue.put(message)

    def toggle_theme(self, e):
        self.config.theme_mode = "dark" if e.control.value else "light"
        self.page.theme_mode = getattr(ft.ThemeMode, self.config.theme_mode.upper())
        self.page.bgcolor = "#1E1E1E" if self.config.theme_mode == "dark" else "#F5F5F5"
        self.page.update()

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
