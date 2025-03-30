import flet as ft

class SettingsWindow:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Configuración del Asistente Virtual"
        self.create_settings_ui()

    def create_settings_ui(self):
        # Crear contenedor principal
        settings_container = ft.Column()

        # Tarjeta de Tema y Efectos y Vista Previa

        theme_card = ft.Card(
            content=ft.Column([
                ft.Text("Opciones de Tema", size=20),
                ft.Row([
                    ft.Text("Modo Claro"),
                    ft.Switch(value=False, on_change=self.toggle_theme)
                ]),
                ft.Row([
                    ft.Text("Modo Oscuro"),
                    ft.Switch(value=False, on_change=self.toggle_theme)
                ]),
                ft.Text("Efecto de Glassmorphism:"),
                ft.Text("Vista previa:"),
                ft.Row([
                    ft.Container(content=ft.Text("Modo Claro"), bgcolor="white", padding=10),
                    ft.Container(content=ft.Text("Modo Oscuro"), bgcolor="black", padding=10)
                ]),

                ft.Switch(value=False, on_change=self.toggle_glassmorphism),
                ft.Text("Vista previa:"),
                ft.Row([
                    ft.Container(content=ft.Text("Modo Claro"), bgcolor="white", padding=10),
                    ft.Container(content=ft.Text("Modo Oscuro"), bgcolor="black", padding=10)
                ])
            ])
        )

        theme_card = ft.Card(
            content=ft.Column([
                ft.Text("Opciones de Tema", size=20),
                ft.Row([
                    ft.Text("Modo Claro"),
                    ft.Switch(value=False, on_change=self.toggle_theme)
                ]),
                ft.Row([
                    ft.Text("Modo Oscuro"),
                    ft.Switch(value=False, on_change=self.toggle_theme)
                ]),
                ft.Text("Vista previa:"),
                ft.Row([
                    ft.Container(content=ft.Text("Modo Claro"), bgcolor="white", padding=10),
                    ft.Container(content=ft.Text("Modo Oscuro"), bgcolor="black", padding=10)
                ])
            ])
        )

        # Tarjeta de Personalización de Colores
        color_card = ft.Card(
            content=ft.Column([
                ft.Text("Personalización de Colores", size=20),
                ft.Row([
                    ft.Text("Color de Fondo:"),
                    ft.TextField(label="Color de Fondo (hex)", on_change=self.change_background_color)
                ]),
                ft.Row([
                    ft.Text("Gradiente de Fondo:"),
                    ft.TextField(label="Gradiente (hex)", on_change=self.change_gradient_color)
                ]),
                ft.Row([
                    ft.Text("Tamaño de Fuente:"),
                    ft.Slider(min=10, max=30, value=14, on_change=self.change_font_size)
                ]),
                ft.Row([
                    ft.Text("Color de Texto:"),
                    ft.TextField(label="Color de Texto (hex)", on_change=self.change_text_color)
                ])
            ])
        )

        # Agregar tarjetas al contenedor
        settings_container.controls.extend([theme_card, color_card])
        self.page.controls.append(settings_container)  # Asegurarse de agregar el contenedor a la página
        self.page.update()  # Actualizar la página para reflejar los cambios

    def toggle_theme(self, e):
        # Lógica para alternar entre temas
        if e.control.value:  # Modo Oscuro
            self.page.theme_mode = ft.ThemeMode.DARK
        else:  # Modo Claro
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()

        # Lógica para alternar entre temas

    def toggle_glassmorphism(self, e):
        # Lógica para alternar el efecto de glassmorphism
        if e.control.value:  # Efecto activado
            self.page.bgcolor = "rgba(255, 255, 255, 0.8)"  # Ejemplo de color con efecto
        else:  # Efecto desactivado
            self.page.bgcolor = "white"  # Color normal
        self.page.update()

        if e.control.value:  # Modo Oscuro
            self.page.theme_mode = ft.ThemeMode.DARK
        else:  # Modo Claro
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()

    def change_background_color(self, e):
        # Lógica para cambiar el color de fondo
        self.page.bgcolor = e.control.value
        self.page.update()

    def change_text_color(self, e):
        # Lógica para cambiar el color de texto
        self.page.text_color = e.control.value
        self.page.update()

# Para usar la ventana de configuración, se puede instanciar SettingsWindow en el main de la aplicación.
