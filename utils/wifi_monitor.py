import threading
import time
import socket
from global_vars import set_global_var, get_global_var

def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        return True
    except OSError:
        return False

def wifi_monitor():
    while get_global_var("is_active"):
        is_connected = check_internet_connection()
        set_global_var("wifi_status", is_connected)
        time.sleep(1)

def start_wifi_monitor():
    monitor_thread = threading.Thread(target=wifi_monitor, daemon=True)
    monitor_thread.start()
    return monitor_thread
