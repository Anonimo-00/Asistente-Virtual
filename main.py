from services.nlp import NLPService
from services.messaging import MessageHandler
from utils.helpers import load_config
from integrations.ui.flet_app import FleetApp
from global_vars import set_global_var, get_global_var
from utils.wifi_monitor import start_wifi_monitor

def main():
    config = load_config()
    set_global_var("app_settings", config)
    set_global_var("is_active", True)
    
    # Iniciar el monitor de WiFi
    wifi_monitor_thread = start_wifi_monitor()
    
    nlp_service = NLPService()
    message_handler = MessageHandler()
    
    print("Asistente Virtual iniciado...")
    
    try:
        app = FleetApp(nlp_service, message_handler)
        app.run()
    finally:
        set_global_var("is_active", False)  # Esto detendrá el monitor de WiFi
        wifi_monitor_thread.join(timeout=2)

if __name__ == "__main__":
    main()
