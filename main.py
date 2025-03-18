import asyncio
from utils.wifi_monitor import start_wifi_monitor
from global_vars import set_global_var, get_global_var
from services.nlp_service import NLPService
from services.message_service import MessageHandler
from utils.config import Config
import threading
import time

class MainApp:
    def __init__(self):
        self.config: Config = None
        self.nlp_service: NLPService = None
        self.message_handler: MessageHandler = None
        self.is_active = True
        self.wifi_thread = None
        self.load_conf()

    def load_conf(self):
        self.config = Config()
        set_global_var("app_settings", self.config.get_all_config())

    def initialize_services(self):
        self.nlp_service = NLPService()
        self.nlp_service.initialize()
        self.message_handler = MessageHandler()

    def start_wifi(self):
        self.wifi_thread = threading.Thread(target=start_wifi_monitor, daemon=True)
        self.wifi_thread.start()

    def main_loop(self):
        try:
            while self.is_active:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def stop_app(self):
        self.is_active = False
        set_global_var("is_active", False)
        if self.wifi_thread and self.wifi_thread.is_alive():
            self.wifi_thread.join(timeout=2)

    def run(self):
        self.initialize_services()
        self.start_wifi()
        self.main_loop()
        self.stop_app()

if __name__ == "__main__":
    app = MainApp()
    app.run()
