"""
Paquete de servicios del asistente virtual.
Define interfaces comunes para servicios NLP y mensajería.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class ServiceBase(ABC):
    """Clase base para todos los servicios."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa el servicio con la configuración dada."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el servicio está disponible."""
        pass
