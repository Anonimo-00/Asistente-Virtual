import flet as ft
from utils.user_manager import UserManager
from typing import Callable, List
import threading
import time
import logging

logger = logging.getLogger(__name__)

class ConfigWindow:
    def __init__(self, page: ft.Page, on_close: Callable = None):
        self.page = page
        self.user_manager = UserManager()
        self.on_close = on_close
        self.view = None
        self.main_view = None
        self.previous_controls = []

    def build(self):
        self.view = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.icons.SETTINGS, size=30, color=ft.colors.BLUE_400),
                            ft.Text("Configuración", size=28, weight=ft.FontWeight.BOLD),
                        ], spacing=10),
                        ft.IconButton(
                            icon=ft.icons.CLOSE_ROUNDED,
                            icon_color=ft.colors.RED_400,
                            icon_size=30,
                            on_click=self.close_window,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.all(20),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                ),

                # Panel de configuración
                ft.Container(
                    content=self._build_system_prefs(),
                    expand=True,
                    padding=20,
                ),
            ]),
            expand=True,
            bgcolor=ft.colors.with_opacity(0.95, ft.colors.BLACK),
        )
        return self.view

    def _on_menu_hover(self, e):
        e.control.bgcolor = ft.colors.with_opacity(0.2, ft.colors.WHITE) if e.data == "true" else ft.colors.with_opacity(0.1, ft.colors.WHITE)
        self.page.update()

    def _build_system_prefs(self):
        theme = self.user_manager.obtener_dato("preferencias", "tema") or "dark"
        return ft.Container(
            content=ft.Column([
                ft.Text("Configuración del Sistema", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400),
                ft.Container(
                    content=ft.Column([
                        # Control de tema modificado
                        ft.Switch(
                            label="Tema Oscuro",
                            value=theme == "dark",
                            active_color=ft.colors.BLUE_400,
                            on_change=lambda e: self._save_theme(e.control.value)
                        ),
                        # Control de voz
                        ft.Switch(
                            label="Voz activada",
                            value=self.user_manager.obtener_dato("preferencias", "voz_activada") or False,
                            active_color=ft.colors.BLUE_400,
                            on_change=lambda e: self._save_pref("preferencias", "voz_activada", e.control.value)
                        ),
                        
                        # Control de tamaño de fuente
                        ft.Text("Tamaño de fuente", size=16, color=ft.colors.WHITE70),
                        ft.Row([
                            ft.Icon(ft.icons.FORMAT_SIZE_ROUNDED, size=20),
                            ft.Slider(
                                min=12,
                                max=24,
                                value=float(self.user_manager.obtener_dato("preferencias", "tamano_fuente") or 16),
                                on_change=lambda e: self._save_pref("preferencias", "tamano_fuente", e.control.value),
                                expand=True,
                            ),
                            ft.Text(f"{int(float(self.user_manager.obtener_dato('preferencias', 'tamano_fuente') or 16))}px")
                        ])
                    ], spacing=20),
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                    border_radius=15,
                )
            ], spacing=20),
            padding=20,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            border_radius=10,
        )

    def _save_pref(self, categoria: str, clave: str, valor: any):
        self.user_manager.actualizar_dato(categoria, clave, valor)

    def _save_theme(self, value):
        theme = "dark" if value else "light"
        self._save_pref("preferencias", "tema", theme)
        self.page.theme_mode = theme.upper()
        self.page.bgcolor = "#1E1E1E" if theme == "dark" else "#F5F5F5"
        self.page.update()

    def close_window(self, e=None):
        """Cierra la ventana de configuración"""
        try:
            logger.info("Cerrando ventana de configuración")
            if hasattr(self.view, 'opacity'):
                self.view.opacity = 0
            if hasattr(self.view, 'scale'):
                self.view.scale = ft.transform.Scale(0.8)
            self.page.update()
            
            def delayed_close():
                time.sleep(0.2)
                if self.previous_controls:
                    self.page.controls = self.previous_controls
                if self.on_close:
                    self.on_close()
                self.page.update()
            
            threading.Thread(target=delayed_close, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error cerrando configuración: {e}")
            if self.previous_controls:
                self.page.controls = self.previous_controls
                self.page.update()
            
    def show(self):
        """Muestra la ventana de configuración con animación"""
        try:
            logger.info("Mostrando ventana de configuración")
            if self.page.controls:
                self.previous_controls = self.page.controls.copy()
            
            if not self.view:
                self.view = self.build()
            
            self.page.controls = [self.view]
            self.page.update()
            
            # Breve delay antes de mostrar
            def delayed_show():
                time.sleep(0.1)
                if hasattr(self.view, 'opacity'):
                    self.view.opacity = 1
                if hasattr(self.view, 'scale'):
                    self.view.scale = ft.transform.Scale(1)
                self.page.update()
            
            threading.Thread(target=delayed_show, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error mostrando configuración: {e}")
            if self.previous_controls:
                self.page.controls = self.previous_controls
                self.page.update()
