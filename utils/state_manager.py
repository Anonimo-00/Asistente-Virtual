import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class Message(BaseModel):
    text: str
    timestamp: datetime = datetime.now()
    user: bool = True

class State(BaseModel):
    messages: List[Message] = []
    last_update: datetime = datetime.now()
    current_context: Dict[str, Any] = {}

class StateManager:
    def __init__(self):
        self.state = State()
        
    def add_message(self, text: str, is_user: bool = True) -> None:
        """Añade un mensaje al historial"""
        try:
            message = Message(text=text, user=is_user)
            self.state.messages.append(message)
            self.state.last_update = datetime.now()
        except Exception as e:
            logger.error(f"Error añadiendo mensaje: {e}")

    def get_messages(self) -> List[Message]:
        """Retorna el historial de mensajes"""
        return self.state.messages

    def clear_messages(self) -> None:
        """Limpia el historial de mensajes"""
        self.state.messages = []
        self.state.last_update = datetime.now()

    def update_context(self, context: Dict[str, Any]) -> None:
        """Actualiza el contexto actual"""
        self.state.current_context.update(context)
        self.state.last_update = datetime.now()

    def get_context(self) -> Dict[str, Any]:
        """Obtiene el contexto actual"""
        return self.state.current_context
