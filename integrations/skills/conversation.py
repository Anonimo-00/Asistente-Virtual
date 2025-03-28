import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
from unidecode import unidecode
from .base_skill import SkillBase

logger = logging.getLogger(__name__)

class ConversationSkill(SkillBase):
    def __init__(self):
        self.basic_intents = {
            "greeting": {
                "patterns": ["hola", "buenas", "hey", "saludos"],
                "response": "¡Hola! ¿En qué puedo ayudarte?"
            },
            "capabilities": {
                "patterns": ["que puedes", "funciones", "ayuda", "capacidades"],
                "response": self._get_capabilities_response()
            }
        }

    def _get_capabilities_response(self) -> str:
        return """Como asistente virtual, puedo:
- Procesar y entender lenguaje natural
- Mantener conversaciones contextuales
- Responder preguntas sobre diversos temas
- Procesar comandos de voz
- Ayudarte con tareas específicas

¿En qué área te gustaría que te ayude?"""

    def process_basic_intent(self, message: str) -> Optional[str]:
        normalized_message = unidecode(message.lower())
        
        for intent in self.basic_intents.values():
            if any(pattern in normalized_message for pattern in intent["patterns"]):
                return intent["response"]
        
        return None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        message = params.get("message", "")
        response = self.process_basic_intent(message)
        return {"response": response if response else None}
