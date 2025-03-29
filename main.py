import flet as ft
import logging
import time
import threading
import asyncio
import platform
from integrations.ui.flet_app import FleetApp
from services.nlp.nlp_service import NLPService
from integrations.skills.base_skill import SkillBase
from integrations.skills.conversation import ConversationSkill

from utils.wifi_monitor import start_wifi_monitor
from global_vars import set_global_var, update_global_state, _global_state, get_global_var
import sys
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suprimir mensajes de TensorFlow

# Configurar logging básico antes que todo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suprimir mensajes específicos
for logger_name in ['absl', 'tensorflow', 'tensorboard', 'google']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)
    logging.getLogger(logger_name).propagate = False

# Desactivar advertencias innecesarias
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Intentar configurar absl logging si está disponible
try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.ERROR)
    absl.logging.use_absl_handler()
except ImportError:
    # Si absl no está instalado, silenciar los warnings relacionados
    logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

def print_global_vars():
    """Imprime el estado de las variables globales cada 20 segundos"""
    while True:
        try:
            logger.info("\n=== Estado de Variables Globales ===")
            for key, value in _global_state.items():
                logger.info(f"{key}: {value}")
            logger.info("=" * 35)
            time.sleep(20)
        except Exception as e:
            logger.error(f"Error imprimiendo variables: {e}")

def main():
    try:
        # Iniciar monitores en threads separados
        set_global_var("is_active", True)
        
        vars_monitor = threading.Thread(target=print_global_vars, daemon=True)
        vars_monitor.start()
        logger.info("Monitor de variables iniciado")
        
        wifi_monitor_thread = start_wifi_monitor()
        logger.info("Monitor WiFi iniciado")

        # Inicializar servicios
        nlp_service = NLPService()
        if not nlp_service.initialized:
            raise RuntimeError("No se pudo inicializar el servicio NLP")
        
        # Ejecutar aplicación de forma simple y directa
        ft.app(
            target=lambda page: FleetApp(nlp_service).main(page),
            assets_dir="assets",
            upload_dir="uploads"
        )
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        set_global_var("is_active", False)

if __name__ == "__main__":
    main()
