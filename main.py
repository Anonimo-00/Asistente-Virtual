from services.nlp import NLPService
from services.messaging import MessageHandler
from utils.helpers import load_config
from integrations.ui.flet_app import FleetApp

def main():
    config = load_config()
    nlp_service = NLPService()
    message_handler = MessageHandler()
    
    print("Asistente Virtual iniciado...")
    
    # Inicializar la interfaz de usuario
    app = FleetApp(nlp_service, message_handler)
    app.run()

if __name__ == "__main__":
    main()
