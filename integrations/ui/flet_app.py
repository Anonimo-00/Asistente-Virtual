import flet as ft
from services.nlp.nlp_service import NLPService
from integrations.ui.config_window import ConfigWindow  # Cambiar a la nueva ventana de configuración

class FleetApp:
    def __init__(self, nlp_service: NLPService):
        self.nlp_service = nlp_service
        self.page = None
        self._setup_theme()

    def _setup_theme(self):
        """Configura el tema inicial y efectos visuales"""
        self.theme_data = {
            "glass_blur": 10,
            "card_elevation": 2,
            "animation_duration": 250
        }

    def _build_chat_area(self):
        """Construye el área principal de chat con efectos modernos"""
        return ft.Container(
            content=ft.Column([
                # Área de mensajes
                ft.Container(
                    content=ft.ListView(expand=True, spacing=10),
                    expand=True,
                    padding=20,
                    border_radius=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=["transparent", "rgba(255,255,255,0.1)"]
                    ),
                    blur=self.theme_data["glass_blur"]
                ),
                
                # Campo de entrada con micrófono
                ft.Container(
                    content=ft.Row([
                        ft.TextField(
                            expand=True,
                            border_radius=30,
                            filled=True,
                            hint_text="Escribe un mensaje...",
                        ),
                        ft.IconButton(
                            icon=ft.icons.MIC,
                            icon_color="blue400",
                            tooltip="Activar micrófono"
                        )
                    ], spacing=10),
                    padding=ft.padding.only(top=20)
                )
            ]),
            expand=True
        )

    def main(self, page: ft.Page):
        self.page = page  # Almacenar el objeto page

        page.title = "Asistente Virtual - Central"  # Título de la aplicación

        page.vertical_alignment = ft.MainAxisAlignment.START

        # Configurar tema y efectos
        page.theme_mode = ft.ThemeMode.DARK
        page.window_bgcolor = ft.colors.TRANSPARENT
        page.window_title_bar_buttons_hidden = True

        # Configurar efectos globales
        page.theme = ft.Theme(
            visual_density=ft.ThemeVisualDensity.COMFORTABLE,
            use_material3=True,
        )
        
        # Agregar contenido principal con nuevo diseño
        main_content = ft.Container(
            content=ft.Column([
                self._build_header(),
                self._build_chat_area()
            ]),
            expand=True,
            padding=20
        )
        
        page.add(main_content)

    def _build_header(self):
        """Construye la barra superior con efecto glassmorphism"""
        return ft.Container(
            content=ft.Row([
                ft.Text("Central",
                       size=28,
                       weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.IconButton(
                        ft.icons.DARK_MODE,
                        on_click=self._toggle_theme
                    ),
                    ft.IconButton(
                        ft.icons.SETTINGS,
                        on_click=self._show_settings
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            margin=ft.margin.only(bottom=20),
            border_radius=15,
            gradient=ft.LinearGradient(
                ["transparent", "rgba(255,255,255,0.1)"]
            ),
            blur=self.theme_data["glass_blur"]
        )

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
