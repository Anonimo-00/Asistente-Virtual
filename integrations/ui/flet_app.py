import flet as ft
import logging
from services.nlp.nlp_service import NLPService

logger = logging.getLogger(__name__)

class FleetApp:
    def __init__(self, nlp_service):
        self.nlp_service = nlp_service
        self.page = None
        self.chat_history = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.input_field = ft.TextField(label="Escribe tu mensaje", expand=True, shift_enter=True, on_submit=self.send_message)
        self.send_button = ft.IconButton(ft.icons.SEND, on_click=self.send_message)

    def run(self):
        ft.app(target=self.main)

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Asistente Virtual"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.window_width = 500
        page.window_height = 600
        page.theme_mode = ft.ThemeMode.DARK

        # Barra superior
        appbar = ft.AppBar(
            title=ft.Text("Asistente Virtual", color=ft.colors.WHITE),
            bgcolor=ft.colors.BLUE_GREY_900,
        )
        page.appbar = appbar

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        self.chat_history,
                        ft.Row([self.input_field, self.send_button]),
                    ],
                    expand=True
                ),
                padding=10,
                expand=True
            )
        )

    def send_message(self, e):
        message = self.input_field.value
        if not message:
            return
        self.input_field.value = ""
        self.add_message_to_chat(message, is_user=True)
        response = self.nlp_service.get_response(message)
        self.add_message_to_chat(response, is_user=False)
        self.page.update()

    def add_message_to_chat(self, message, is_user):
        self.chat_history.controls.append(
            ft.Container(
                content=ft.Text(message, color=ft.colors.WHITE),
                alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
                bgcolor=ft.colors.BLUE_GREY_200 if is_user else ft.colors.BLUE_GREY_400,
                padding=10,
                border_radius=5,
                margin=5,
            )
        )
        self.page.update()

class MainApp:
    def __init__(self):
        self.name = "Asistente Virtual"
        self.nlp_service = NLPService()
        self.fleet_app = FleetApp(self.nlp_service)

    def run(self):
        logger.info(f"Ejecutando {self.name}")
        self.fleet_app.run()
