import signal
import sys
from gpt4all import GPT4All
import flet as ft
import threading
import os
import time

# Declaración global del modelo y eventos
nlp = None
model_ready = threading.Event()
stop_loading = threading.Event()

# Manejador de señales para cerrar la aplicación
def signal_handler(signum, frame):
    print("\nDeteniendo la aplicación...")
    stop_loading.set()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Definir la ruta para los modelos
MODEL_PATH = os.path.join(os.path.expanduser("~"), ".cache", "gpt4all")
os.makedirs(MODEL_PATH, exist_ok=True)

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Asistente Virtual"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1000
    page.window_height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Crear componentes mejorados
    txt_input = ft.TextField(
        label="Escribe tu pregunta aquí",
        on_submit=lambda e: send_message(),
        width=600,
        border_radius=10,
        filled=True,
        multiline=True,
        min_lines=1,
        max_lines=3,
        text_size=16,
        autofocus=True
    )

    txt_response = ft.Text(
        value="Esperando respuesta...",
        size=16,
        selectable=True,
        text_align=ft.TextAlign.LEFT,
        width=800,
        color=ft.Colors.BLUE_200,
        weight=ft.FontWeight.W_400,
    )

    # Contenedor de respuesta con scroll
    response_container = ft.Container(
        content=ft.Column(
            [txt_response],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            expand=True
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.BLUE_400),
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY),
        width=800,
        height=400
    )

    progress = ft.ProgressRing(
        width=20,
        height=20,
        stroke_width=2,
        visible=False,
        color=ft.Colors.BLUE
    )

    def on_send(e):
        send_message()

    send_button = ft.ElevatedButton(
        "Enviar",
        on_click=on_send,
        icon=ft.Icons.SEND_ROUNDED,
        style=ft.ButtonStyle(
            color={
                "default": ft.Colors.WHITE,
                "hovered": ft.Colors.BLUE,
            },
            bgcolor={
                "default": ft.Colors.BLUE,
                "hovered": ft.Colors.BLUE_100,
            },
            animation_duration=300,
        )
    )

    stop_button = ft.ElevatedButton(
        "Detener carga",
        on_click=lambda _: stop_loading.set(),
        icon=ft.Icons.STOP,
        visible=False,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED,
        )
    )

    # Contenedor para input y botón
    input_container = ft.Container(
        content=ft.Row(
            [txt_input, send_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        padding=10,
        margin=ft.margin.only(bottom=20)
    )

    # Título con animación (eliminado el parámetro animate)
    title = ft.Text(
        "Bienvenido al Asistente Virtual",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE,
        text_align=ft.TextAlign.CENTER
    )

    # Contenedor principal actualizado
    main_container = ft.Container(
        content=ft.Column(
            [
                title,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                input_container,
                ft.Row(
                    [progress, stop_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                response_container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        padding=ft.padding.all(20),
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE),
        width=900
    )

    # Agregar el contenedor principal centrado en la página
    page.add(
        ft.Container(
            content=main_container,
            alignment=ft.alignment.center
        )
    )

    # Inicializar el modelo en un hilo separado para no bloquear la UI
    def init_model():
        global nlp
        try:
            stop_button.visible = True
            page.update()
            txt_response.value = "Descargando modelo ligero... esto tomará unos minutos."
            page.update()
            
            # Timer para auto-cerrar después de 5 minutos
            def check_timeout():
                time.sleep(300)  # 5 minutos
                if not model_ready.is_set():
                    stop_loading.set()
                    txt_response.value = "Tiempo de carga excedido. Por favor reinicia la aplicación."
                    page.update()
            
            threading.Thread(target=check_timeout, daemon=True).start()
            
            # Usando un modelo más ligero
            model_name = "gpt4all-j-v1.3-groovy"
            
            nlp = GPT4All(
                model_name=model_name,
                model_path=MODEL_PATH,
                allow_download=True,
                verbose=True
            )
            
            if stop_loading.is_set():
                raise Exception("Carga cancelada por el usuario")

            if nlp is None:
                raise Exception("El modelo no se pudo cargar correctamente")
                
            txt_response.value = "¡Modelo cargado correctamente! Puedes empezar a hacer preguntas."
            model_ready.set()
        except Exception as e:
            error_msg = (
                f"Error al cargar el modelo: {str(e)}\n"
                "Sugerencia: Intenta reiniciar la aplicación o usar otro modelo."
            )
            txt_response.value = error_msg
        finally:
            progress.visible = False
            stop_button.visible = False
            page.update()

    # Iniciar la carga del modelo
    progress.visible = True
    threading.Thread(target=init_model).start()

    # Función para enviar mensaje (refactorizada desde on_send)
    def send_message():
        if not txt_input.value:
            return
        
        if not model_ready.is_set():
            txt_response.value = "Por favor espera a que el modelo termine de cargar..."
            page.update()
            return
            
        progress.visible = True
        page.update()
        
        try:
            with nlp.chat_session():
                response = nlp.generate(
                    txt_input.value,
                    max_tokens=512,
                    temp=0.7,
                    top_k=40,
                    top_p=0.4
                )
            txt_response.value = response
        except Exception as e:
            txt_response.value = f"Error: {str(e)}"
        
        progress.visible = False
        txt_input.value = ""
        page.update()

# Simplificar la ejecución principal
if __name__ == "__main__":
    ft.app(target=main)
