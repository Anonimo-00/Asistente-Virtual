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

# Variable booleana para determinar si usar la IA
use_ai = True

# Historial de chat y modo oscuro
chat_history = []
is_dark_mode = True

# Manejador de señales para cerrar la aplicación
def signal_handler(signum, frame):
    print("\nDeteniendo la aplicación...")
    stop_loading.set()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Definir la ruta para los modelos
MODEL_PATH = os.path.join(os.path.expanduser("~"), ".cache", "gpt4all")
os.makedirs(MODEL_PATH, exist_ok=True)

def save_chat_history(messages):
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        for msg in messages:
            f.write(f"{msg}\n")

def load_chat_history():
    try:
        with open("chat_history.txt", "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Asistente Virtual"
    page.theme_mode = ft.ThemeMode.DARK if is_dark_mode else ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO
    
    # Crear componentes mejorados
    txt_input = ft.TextField(
        label="Hazme una pregunta",
        on_submit=lambda e: send_message(),
        width=page.window_width - 40,
        border_radius=20,
        filled=True,
        multiline=False,
        text_size=14,
        autofocus=True
    )

    def create_message_bubble(text, is_user=False):
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Tú:" if is_user else "Asistente:",
                    size=12,
                    color=ft.Colors.GREY_400
                ),
                ft.Text(text, size=14, selectable=True),
            ]),
            bgcolor=ft.Colors.BLUE_700 if is_user else ft.Colors.GREY_800,
            border_radius=20,
            padding=15,
            margin=ft.margin.only(left=50 if is_user else 0, right=0 if is_user else 50),
            alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
        )

    chat_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        expand=True,
    )

    response_container = ft.Container(
        content=chat_column,
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREY_900),
        width=page.window_width - 20,
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
        icon=ft.Icons.SEND,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=20),
        ),
        width=100,
        height=40,
    )

    stop_button = ft.ElevatedButton(
        "Detener carga",
        on_click=lambda _: stop_loading.set(),
        icon=ft.Icons.STOP,
        visible=False,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED,
            shape=ft.RoundedRectangleBorder(radius=20),
        ),
        width=150,
        height=40,
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
        "Asistente Virtual",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE,
        text_align=ft.TextAlign.CENTER
    )

    # Botones de funciones rápidas
    quick_actions = ft.Row([
        ft.ElevatedButton(
            "Limpiar Chat",
            icon=ft.icons.CLEAR_ALL,
            on_click=lambda _: clear_chat(),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_400,
            )
        ),
        ft.ElevatedButton(
            "Guardar Chat",
            icon=ft.icons.SAVE,
            on_click=lambda _: save_chat_history([msg.content.controls[1].value for msg in chat_column.controls]),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_400,
            )
        ),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    def clear_chat():
        chat_column.controls.clear()
        page.update()

    # Contenedor principal actualizado
    main_container = ft.Container(
        content=ft.Column(
            [
                title,
                ft.Divider(height=20, color=ft.Colors.BLUE_200),
                quick_actions,
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
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE),
        width=page.window_width - 20
    )

    # Pestaña de configuración
    def toggle_ai(e):
        global use_ai
        use_ai = e.control.value
        page.update()

    ai_switch = ft.Switch(
        label="Usar IA",
        value=use_ai,
        on_change=toggle_ai
    )

    def toggle_theme(e):
        global is_dark_mode
        is_dark_mode = not is_dark_mode
        page.theme_mode = ft.ThemeMode.DARK if is_dark_mode else ft.ThemeMode.LIGHT
        page.update()

    # Agregar botón de tema en la pestaña de configuración
    theme_switch = ft.Switch(
        label="Modo Oscuro",
        value=is_dark_mode,
        on_change=toggle_theme
    )

    config_tab = ft.Tab(
        text="Configuración",
        content=ft.Container(
            content=ft.Column(
                [
                    ai_switch,
                    theme_switch,
                ],
                spacing=10
            ),
            padding=20
        )
    )

    # Pestañas principales
    tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="Asistente", content=main_container),
            config_tab
        ],
        expand=True
    )

    # Agregar las pestañas a la página
    page.add(tabs)

    # Inicializar el modelo en un hilo separado para no bloquear la UI
    def init_model():
        global nlp
        try:
            stop_button.visible = True
            page.update()
            chat_column.controls.append(create_message_bubble("Descargando modelo ligero... esto tomará unos minutos."))
            page.update()
            
            # Timer para auto-cerrar después de 5 minutos
            def check_timeout():
                time.sleep(300)  # 5 minutos
                if not model_ready.is_set():
                    stop_loading.set()
                    chat_column.controls.append(create_message_bubble("Tiempo de carga excedido. Por favor reinicia la aplicación."))
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
                
            chat_column.controls.append(create_message_bubble("¡Modelo cargado correctamente! Puedes empezar a hacer preguntas."))
            model_ready.set()
        except Exception as e:
            error_msg = (
                f"Error al cargar el modelo: {str(e)}\n"
                "Sugerencia: Intenta reiniciar la aplicación o usar otro modelo."
            )
            chat_column.controls.append(create_message_bubble(error_msg))
        finally:
            progress.visible = False
            stop_button.visible = False
            page.update()

    # Iniciar la carga del modelo
    progress.visible = True
    threading.Thread(target=init_model).start()

    # Cargar historial al inicio
    for msg in load_chat_history():
        if msg.strip():
            chat_column.controls.append(create_message_bubble(msg.strip()))
    page.update()

    # Función para enviar mensaje (refactorizada desde on_send)
    def send_message():
        if not txt_input.value:
            return
        
        user_message = txt_input.value
        chat_column.controls.append(create_message_bubble(user_message, True))
        page.update()
        
        if not model_ready.is_set():
            response = "Por favor espera a que el modelo termine de cargar..."
        elif not use_ai:
            response = "La IA está desactivada. Actívala en la pestaña de configuración."
        else:
            try:
                with nlp.chat_session():
                    response = nlp.generate(
                        user_message,
                        max_tokens=512,
                        temp=0.7,
                        top_k=40,
                        top_p=0.4
                    )
            except Exception as e:
                response = f"Error: {str(e)}"

        chat_column.controls.append(create_message_bubble(response))
        save_chat_history([user_message, response])
        
        progress.visible = False
        txt_input.value = ""
        page.update()
        
        # Auto-scroll al último mensaje
        chat_column.scroll_to(offset=chat_column.scroll_extent)

# Simplificar la ejecución principal
if __name__ == "__main__":
    ft.app(target=main)
