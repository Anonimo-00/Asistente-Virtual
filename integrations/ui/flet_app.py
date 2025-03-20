import flet as ft
import logging
from services.nlp.nlp_service import NLPService
from utils.state_manager import StateManager
from typing import Optional
from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3
import threading

logger = logging.getLogger(__name__)

class UIConfig(BaseModel):
    max_width: int = 800
    message_width_ratio: float = 0.7
    theme_mode: str = "dark"
    enable_voice: bool = True
    voice_lang: str = "es"

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
        if UIConfig().enable_voice:
            self.init_voice_components()

    def init_voice_components(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', 'spanish')
        
        self.mic_button = ft.IconButton(
            ft.icons.MIC,
            on_click=self.toggle_voice_input,
            icon_color=ft.colors.BLUE_400
        )

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

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Asistente Virtual"
        page.window_width = self.config.max_width
        page.window_min_width = 400
        page.theme_mode = getattr(ft.ThemeMode, self.config.theme_mode.upper())
        page.padding = 0
        page.bgcolor = ft.colors.SURFACE_VARIANT

        # Barra superior estilo Google
        appbar = ft.AppBar(
            leading=ft.Icon(ft.icons.CHAT_ROUNDED),
            title=ft.Text("Asistente Virtual", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            elevation=0.5,
        )
        
        # Contenedor principal
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

        page.add(appbar, chat_container)

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
        
        msg_container = ft.Container(
            content=ft.Text(
                value=message,
                size=16,
                color=ft.colors.WHITE if is_user else ft.colors.BLACK,
                selectable=True,
                weight=ft.FontWeight.W_400,
                overflow=ft.TextOverflow.WRAP,
                text_align=ft.TextAlign.LEFT,
            ),
            bgcolor=ft.colors.BLUE_700 if is_user else ft.colors.WHITE,
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
        )

        # Wrapper con ancho responsivo
        wrapper = ft.Container(
            content=msg_container,
            alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
            margin=ft.margin.symmetric(vertical=4, horizontal=20),
            width=self.page.width * self.config.message_width_ratio if self.page else 300,
        )

        try:
            self.chat_history.controls.append(wrapper)
            self.state.add_message(message, is_user)
            self.page.update()
        except Exception as e:
            logger.error(f"Error al agregar mensaje: {e}")

        if not is_user and self.config.enable_voice:
            threading.Thread(
                target=lambda: self.engine.say(message) or self.engine.runAndWait(),
                daemon=True
            ).start()

class MainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Asistente Virtual"
        self.nlp_service = NLPService()
        self.setup_ui()
        
    def setup_ui(self):
        # Configuración básica de la UI
        self.input_text = ft.TextField(
            label="Escribe tu mensaje",
            multiline=False,
            on_submit=self.send_message
        )
        
        self.chat_view = ft.Column(
            scroll=True,
            expand=True
        )
        
        self.page.add(
            self.chat_view,
            ft.Row([
                self.input_text,
                ft.IconButton(
                    icon=ft.icons.SEND,
                    on_click=self.send_message
                )
            ])
        )
    
    def send_message(self, e):
        if self.input_text.value:
            response = self.nlp_service.process_input(self.input_text.value)
            self.chat_view.controls.append(ft.Text(f"Tú: {self.input_text.value}"))
            self.chat_view.controls.append(ft.Text(f"Asistente: {response}"))
            self.input_text.value = ""
            self.page.update()
