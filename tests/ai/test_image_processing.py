import unittest
import os
import sys
import logging
from dotenv import load_dotenv
from global_vars import set_global_var
from PIL import Image
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from services.nlp.nlp_service import NLPService

class TestGeminiImageProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env"))
        logging.basicConfig(level=logging.INFO)
        cls.nlp_service = NLPService()
        set_global_var("wifi_status", True)
        
        # Crear una imagen de prueba
        cls.test_image_path = "test_image.png"
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(cls.test_image_path)

    def test_vision_model_initialization(self):
        """Prueba que el modelo vision se inicialice correctamente"""
        self.assertEqual(self.nlp_service.model_name, "gemini-pro-vision")
        self.assertTrue(self.nlp_service.supports_images)
        self.assertTrue(self.nlp_service.initialized)

    def test_image_processing(self):
        """Prueba el procesamiento de imágenes"""
        prompt = "¿Qué color ves en esta imagen?"
        response = self.nlp_service.process_input(prompt, self.test_image_path)
        self.assertIsNotNone(response)
        self.assertIn("roj", response.lower())  # Debería detectar rojo

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)

if __name__ == '__main__':
    unittest.main(verbosity=2)
