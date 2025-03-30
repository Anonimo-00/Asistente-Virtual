import flet as ft
from services.nlp.nlp_service import NLPService

class FleetApp:
    def __init__(self, nlp_service: NLPService):
        self.nlp_service = nlp_service

    def main(self, page: ft.Page):
        page.title = "Asistente Virtual"
        page.vertical_alignment = ft.MainAxisAlignment.START

        # Crear un contenedor para las tarjetas
        card_container = ft.Column()

        # Ejemplo de tarjeta
        card = ft.Card(
            content=ft.Column([
                ft.Text("¡Hola! ¿En qué puedo ayudarte?", size=20),
                ft.ElevatedButton("Enviar", on_click=self.send_message)
            ]),
            color="rgba(255, 255, 255, 0.98)",


            hover_color="rgba(255, 255, 255, 0.05)"
        )

        card_container.controls.append(card)
        page.add(card_container)

    def send_message(self, e):
        # Lógica para enviar un mensaje y obtener una respuesta
        pass
