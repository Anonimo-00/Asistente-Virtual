import flet as ft
from services.nlp.nlp_service import NLPService
from integrations.ui.settings import SettingsWindow  # Importar la ventana de configuración

class FleetApp:
    def __init__(self, nlp_service: NLPService):
        self.nlp_service = nlp_service
        self.page = None  # Inicializar page como None
        self.nlp_service = nlp_service  # Almacenar el servicio NLP


    def main(self, page: ft.Page):


        self.page = page  # Almacenar el objeto page

        page.title = "Asistente Virtual"
        page.vertical_alignment = ft.MainAxisAlignment.START

        # Crear un contenedor para las tarjetas
        card_container = ft.Column()

        # Ejemplo de tarjeta
        settings_button = ft.ElevatedButton("Configuración", on_click=self.open_settings)
        card = ft.Card(
            content=ft.Column([
                settings_button,
                ft.Text("¡Hola! ¿En qué puedo ayudarte?", size=20),
                ft.ElevatedButton("Enviar", on_click=self.send_message)
            ])
        )

        # Agregar la tarjeta al contenedor
        card_container.controls.append(card)
        page.add(card_container)

    async def send_message(self, e):
        user_input = "Tu mensaje aquí"  # Aquí deberías obtener el texto del botón o campo de entrada
        response = await self.nlp_service.process_input(user_input)
        # Aquí puedes manejar la respuesta y actualizar la interfaz de usuario
        print(response)

    def open_settings(self, e):
        # Abrir la ventana de configuración
        SettingsWindow(self.page)

# Para ejecutar la aplicación
if __name__ == "__main__":
    nlp_service = NLPService()
    app = FleetApp(nlp_service)
    ft.app(target=app.main)
