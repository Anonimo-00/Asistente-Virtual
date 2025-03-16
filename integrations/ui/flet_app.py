import flet as ft

class FleetApp:
    def __init__(self, nlp_service, message_handler):
        self.nlp_service = nlp_service
        self.message_handler = message_handler

    def main_page(self, page: ft.Page):
        page.title = "Asistente Virtual"
        page.add(ft.Text("Bienvenido al Asistente Virtual"))

    def run(self):
        ft.app(target=self.main_page)
