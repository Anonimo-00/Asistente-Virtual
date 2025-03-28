from services.skills.skill_registry import skill_registry
import os

@skill_registry.register(
    contexts=["que puedes hacer", "qué puedes hacer", "ayuda", "help", "comandos", "funciones"],
    description="Muestra las funciones disponibles del asistente"
)
def show_help() -> str:
    """Muestra todas las funciones disponibles"""
    help_text = [
        "👋 ¡Hola! Estas son mis capacidades:\n",
        "Capacidades base:",
        "- Conversación natural y respuesta a preguntas",
        "- Procesamiento de lenguaje natural",
        "- Memoria de contexto en conversaciones",
        "- Modo offline para funciones básicas\n",
        "Skills específicas:\n"
    ]
    help_text.append(skill_registry.get_skill_info())
    return "\n".join(help_text)
