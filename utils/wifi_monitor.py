import threading
import time
import socket
import logging
import tracemalloc
from global_vars import set_global_var, get_global_var, _global_state

logger = logging.getLogger(__name__)
tracemalloc.start()

def check_internet_connection():
    try:
        servers = [
            ("8.8.8.8", 53),
            ("1.1.1.1", 53),
            ("208.67.222.222", 53),
            ("google.com", 80),
            ("cloudflare.com", 80)
        ]
        
        success = False
        for server in servers:
            try:
                with socket.create_connection(server, timeout=1) as sock:
                    success = True
                    break
            except Exception:
                continue
        
        # Actualizar estado solo si cambió
        current_status = get_global_var("wifi_status")
        if success != current_status:
            set_global_var("wifi_status", success)
            logger.info(f"Estado de conexión actualizado: {'Conectado' if success else 'Desconectado'}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error en check_internet_connection: {e}")
        set_global_var("wifi_status", False)
        return False

def wifi_monitor():
    set_global_var("is_active", True)
    last_print = time.time()
    
    while get_global_var("is_active"):
        check_internet_connection()
        
        # Imprimir variables globales cada 20 segundos
        current_time = time.time()
        if current_time - last_print >= 20:
            logger.info("=== Estado de Variables Globales ===")
            for key, value in _global_state.items():
                logger.info(f"{key}: {value}")
            logger.info("==================================")
            last_print = current_time
            
        time.sleep(1)

def start_wifi_monitor():
    set_global_var("is_active", True)
    monitor_thread = threading.Thread(target=wifi_monitor, daemon=True)
    monitor_thread.start()
    return monitor_thread
