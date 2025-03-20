from typing import Dict, Any
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        logger.info("Creando MessageHandler")
        self.messages = []
        self.callbacks = []
    
    def send_message(self, message: str, metadata: Dict[str, Any] = None) -> bool:
        """Envía un mensaje y notifica a los callbacks"""
        msg_obj = {
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(msg_obj)
        
        # Notificar a todos los callbacks registrados
        for callback in self.callbacks:
            try:
                asyncio.create_task(callback(msg_obj))
            except Exception as e:
                print(f"Error en callback de mensaje: {e}")
        
        return True
    
    def register_callback(self, callback):
        """Registra un callback para notificaciones de mensajes"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
