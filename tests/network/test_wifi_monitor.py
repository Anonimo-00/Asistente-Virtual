import unittest
import threading
import time
import sys
import os
import tracemalloc
import gc

# Agregar el directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.wifi_monitor import check_internet_connection, start_wifi_monitor, wifi_monitor
from global_vars import get_global_var, set_global_var

class TestWiFiMonitor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tracemalloc.start()
    
    def setUp(self):
        set_global_var("is_active", True)
        set_global_var("wifi_status", False)
        self.monitor_thread = None
        gc.collect()  # Forzar recolección de basura

    def tearDown(self):
        set_global_var("is_active", False)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        gc.collect()

    def test_check_internet_connection(self):
        """Prueba la función de verificación de conexión"""
        result = check_internet_connection()
        # Agregamos un print para debug
        print(f"\nEstado de conexión: {result}")
        print(f"Estado global wifi_status: {get_global_var('wifi_status')}")
        self.assertIsInstance(result, bool)
        self.assertEqual(result, get_global_var("wifi_status"))

    def test_monitor_startup(self):
        """Prueba que el monitor inicie correctamente"""
        self.monitor_thread = start_wifi_monitor()
        self.assertTrue(self.monitor_thread.is_alive())
        self.assertTrue(get_global_var("is_active"))
        time.sleep(2)  # Esperar a que actualice el estado
        self.assertIsInstance(get_global_var("wifi_status"), bool)

    def test_monitor_shutdown(self):
        """Prueba que el monitor se detenga correctamente"""
        self.monitor_thread = start_wifi_monitor()
        set_global_var("is_active", False)
        self.monitor_thread.join(timeout=2)
        self.assertFalse(self.monitor_thread.is_alive())

    @classmethod
    def tearDownClass(cls):
        tracemalloc.stop()

if __name__ == '__main__':
    # Configurar logging para ver mensajes de debug
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
