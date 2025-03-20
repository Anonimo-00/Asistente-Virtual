import logging
from integrations.ui.flet_app import MainApp

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except Exception as e:
        logger.critical(f"Error fatal: {e}")
        exit(1)
