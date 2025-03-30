import flet as ft
from typing import Optional

class ChatCard(ft.UserControl):
    def __init__(
        self,
        message: str,
        is_user: bool = False,
        media_url: Optional[str] = None,
        actions: Optional[list] = None
    ):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.media_url = media_url
        self.actions = actions or []

    def build(self):
        return ft.Container(
            content=ft.Column([
                # Contenido del mensaje
                ft.Text(
                    self.message,
                    size=16,
                    color="white" if self.is_user else "black"
                ),
                
                # Imagen/Media si existe
                ft.Image(src=self.media_url) if self.media_url else None,
                
                # Botones de acción
                ft.Row([
                    ft.ElevatedButton(
                        text=action["text"],
                        on_click=action["on_click"]
                    ) for action in self.actions
                ]) if self.actions else None
            ]),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    "rgba(100,149,237,0.9)" if self.is_user else "rgba(255,255,255,0.95)",
                    "rgba(100,149,237,0.7)" if self.is_user else "rgba(255,255,255,0.85)"
                ]
            ),
            blur=5,
            border_radius=20,
            padding=15,
            animate=ft.animation.Animation(250, "easeOut")
        )
