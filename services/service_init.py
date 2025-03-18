from typing import Dict, Any
from .nlp_service import NLPService
from .message_service import MessageHandler

class ServiceManager:
    _instance = None
    _services: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
        return cls._instance

    def initialize_services(self):
        self._services["nlp"] = NLPService()
        self._services["message"] = MessageHandler()
        
        # Inicializar servicios
        self._services["nlp"].initialize()
        
        return self._services

    def get_service(self, service_name: str) -> Any:
        return self._services.get(service_name)

    def get_all_services(self) -> Dict[str, Any]:
        return self._services
