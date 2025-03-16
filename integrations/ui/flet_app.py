import flet as ft
import os

class FleetApp:
    def __init__(self, nlp_service, message_handler):
        self.nlp_service = nlp_service
        self.message_handler = message_handler
        self.search_field = None
        
    def search_clicked(self, e):
        if self.search_field and self.search_field.value:
            # Usar el servicio NLP local para procesar la consulta
            response = self.nlp_service.process(self.search_field.value)
            # Mostrar la respuesta usando el message_handler
            self.message_handler.send_message(response)
            
    def main_page(self, page: ft.Page):
        page.title = "Asistente Virtual"
        page.bgcolor = ft.colors.WHITE
        
        # Container principal centrado
        main_container = ft.Container(
            content=ft.Column(
                controls=[
                    # Logo (usar una imagen local)
                    ft.Image(
                        src=os.path.join("assets", "assistant_logo.png"),
                        width=272,
                        height=92
                    ),
                    # Campo de búsqueda
                    ft.Container(
                        content=ft.TextField(
                            ref=lambda field: setattr(self, 'search_field', field),
                            border=ft.InputBorder.OUTLINE,
                            prefix_icon=ft.icons.SEARCH,
                            suffix_icon=ft.icons.MIC,
                            width=550,
                            text_align=ft.TextAlign.LEFT,
                            border_radius=25,
                            hint_text="Escribe tu consulta aquí..."
                        ),
                        margin=ft.margin.only(top=20, bottom=20)
                    ),
                    # Botones con eventos
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                text="Buscar",
                                on_click=self.search_clicked
                            ),
                            ft.ElevatedButton(
                                text="Me siento con suerte",
                                on_click=self.search_clicked
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        page.add(main_container)

    def run(self):
        ft.app(target=self.main_page)
