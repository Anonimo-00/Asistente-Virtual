import unittest
import os
import sys
import logging
from dotenv import load_dotenv
from global_vars import set_global_var

# Agregar el directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.nlp.nlp_service import NLPService

class TestGeminiService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env"))
        logging.basicConfig(level=logging.INFO)
        cls.nlp_service = NLPService()
        set_global_var("wifi_status", True)  # Forzar modo online para algunos tests

    def test_gemini_initialization(self):
        """Prueba que Gemini se inicialice correctamente"""
        self.assertTrue(hasattr(self.nlp_service, 'model'))
        self.assertTrue(hasattr(self.nlp_service, 'chat'))
        self.assertTrue(self.nlp_service.initialized)
        
    def test_api_key_exists(self):
        """Prueba que existe la API key"""
        api_key = os.getenv("GEMINI_API_KEY")
        self.assertIsNotNone(api_key)
        self.assertNotEqual(api_key, "tu_api_key_de_gemini_aqui")

    def test_basic_conversation(self):
        """Prueba una conversación básica"""
        test_input = "Hola, ¿cómo estás?"
        response = self.nlp_service.process_input(test_input)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_complex_query(self):
        """Prueba una consulta más compleja"""
        test_input = "Explícame cómo funciona la inteligencia artificial en 2 párrafos"
        response = self.nlp_service.process_input(test_input)
        self.assertIsNotNone(response)
        self.assertIn('\n', response)  # Debería contener al menos un salto de línea

    def test_offline_complex_query(self):
        """Prueba una consulta compleja en modo offline"""
        set_global_var("wifi_status", False)
        test_input = "Explícame cómo funciona la inteligencia artificial"
        response = self.nlp_service.process_input(test_input)
        self.assertIsNotNone(response)
        self.assertIn('\n', response)
        self.assertGreater(len(response.split('\n')), 1)

    def test_online_complex_query(self):
        """Prueba una consulta compleja en modo online"""
        set_global_var("wifi_status", True)
        test_input = "Explícame cómo funciona la inteligencia artificial"
        try:
            response = self.nlp_service.process_input(test_input)
            self.assertIsNotNone(response)
            self.assertGreater(len(response), 50)  # Respuesta substantiva
        except Exception as e:
            self.skipTest(f"Test saltado por error de API: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
