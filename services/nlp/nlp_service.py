import logging
import base64
import os
import google.generativeai as genai
from google.generativeai import types  # Añadir esta importación
from typing import List, Dict, Any
from dotenv import load_dotenv
import json
from global_vars import get_global_var, set_global_var
from PIL import Image
import io
import time
from services.skills.skill_registry import skill_registry
from services.cache.cache_cleaner import cache_manager as cache
from integrations.skills.gemini.embeddings_skill import EmbeddingsSkill
from integrations.skills.gemini.token_counter_skill import TokenCounterSkill
from integrations.skills.gemini.generation_skill import GenerationSkill
from integrations.skills.conversation.conversation_skill import ConversationSkill

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env"))
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.context = {}
        # Configurar Gemini con la API key
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        self.conversation_skill = ConversationSkill()
        self.skills = [self.conversation_skill]
        self.initialized = False
        
        # Cargar modelo desde .env
        self.model_name = os.getenv("LANGUAGE_MODEL", "gemini-pro")
        self.supports_images = False
        self.chat_history = []
        
        # Inicializar skills de Gemini
        self.embeddings_skill = None
        self.token_counter_skill = None
        self.generation_skill = None
        
        self.init_gemini()
        
        # Inicializar todas las skills disponibles
        self.skills = {
            'conversation': self.conversation_skill,
            'embeddings': self.embeddings_skill,
            'tokens': self.token_counter_skill,
            'generation': self.generation_skill
        }
        
        # Mapeo de intenciones a skills
        self.intent_mapping = {
            # Intents de conversación
            'chat': 'conversation',
            'preguntar': 'conversation',
            'hablar': 'conversation',
            
            # Intents de embeddings
            'vectorizar': 'embeddings',
            'embedding': 'embeddings',
            
            # Intents de tokens
            'contar': 'tokens',
            'tokens': 'tokens',
            'longitud': 'tokens',
            
            # Intents de generación
            'generar': 'generation',
            'crear': 'generation',
            'escribir': 'generation'
        }

        self.offline_responses = {
            "explanation": ["""Te explico de manera sencilla:

La inteligencia artificial es un campo que estudia cómo hacer que las computadoras aprendan y tomen decisiones.

Este proceso implica el uso de algoritmos y datos para que las máquinas puedan resolver problemas de forma autónoma."""],
            
            "technical": ["""Entiendo tu consulta técnica.

Por favor, proporciona más detalles para poder ayudarte mejor.

Actualmente estoy en modo offline, pero intentaré asistirte con la información disponible."""],
            
            "greeting": ["¡Hola!\n\n¿En qué puedo ayudarte hoy?"],
            "farewell": ["¡Hasta luego!\n\nQue tengas un excelente día."],
            "help": ["Estas son algunas cosas en las que puedo ayudarte:\n\n- Responder preguntas\n- Explicar conceptos\n- Analizar problemas\n\n¿Qué necesitas?"],
            "error": ["Lo siento, estoy en modo offline.\n\nPor favor, espera a que se restablezca la conexión para obtener una respuesta más detallada."]
        }
        
        self.last_wifi_check = 0
        self.wifi_check_interval = 1  # segundos
        self.load_readme_context()
        
    def load_readme_context(self):
        """Carga el contenido del README como contexto"""
        try:
            readme_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "..",
                "README.md"
            )
            if (os.path.exists(readme_path)):
                with open(readme_path, "r", encoding="utf-8") as f:
                    self.readme_context = f.read()
                logger.info("README cargado como contexto")
            else:
                logger.warning("README.md no encontrado")
                self.readme_context = ""
        except Exception as e:
            logger.error(f"Error cargando README: {e}")
            self.readme_context = ""

    def check_connectivity(self) -> bool:
        """Verifica el estado actual de la conexión"""
        current_time = time.time()
        if current_time - self.last_wifi_check >= self.wifi_check_interval:
            self.is_online = get_global_var("wifi_status")
            self.last_wifi_check = current_time
            logger.debug(f"Estado de conexión actualizado: {'Online' if self.is_online else 'Offline'}")
        return self.is_online

    def init_gemini(self):
        try:
            if not self.model_name:
                raise ValueError("LANGUAGE_MODEL no definido en .env. Usando modelo por defecto: gemini-pro")
                self.model_name = "gemini-pro"
            
            logger.info(f"Inicializando modelo: {self.model_name}")
            
            # Configuración del modelo
            model_config = {
                "temperature": 0.9,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
                "stop_sequences": []
            }

            # Configuración simplificada
            self.generate_config = genai.types.GenerationConfig(**model_config)

            # Crear modelo con configuración básica
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generate_config
            )

            # Inicializar skills especializadas con mejor control de errores
            try:
                self.embeddings_skill = EmbeddingsSkill(self.model)
                logger.info("EmbeddingsSkill inicializada correctamente")
            except Exception as e:
                logger.error(f"Error inicializando EmbeddingsSkill: {e}")
                self.embeddings_skill = None

            try:
                self.token_counter_skill = TokenCounterSkill(self.model)
                logger.info("TokenCounterSkill inicializada correctamente")
            except Exception as e:
                logger.error(f"Error inicializando TokenCounterSkill: {e}")
                self.token_counter_skill = None

            try:
                self.generation_skill = GenerationSkill(self.model)
                logger.info("GenerationSkill inicializada correctamente")
            except Exception as e:
                logger.error(f"Error inicializando GenerationSkill: {e}")
                self.generation_skill = None

            if not self.supports_images:
                self.personality_prompt = self.load_personality_prompt()
                # Iniciar chat sin pasar generation_config directamente
                self.chat = self.model.start_chat(history=[])
                
                # Configurar el chat después de crearlo
                self.chat.generation_config = self.generate_config
                
                if self.personality_prompt:
                    self.chat.send_message(self.personality_prompt)

            self.initialized = True
            logger.info(f"Modelo {self.model_name} inicializado con configuración completa")
            return True
            
        except Exception as e:
            logger.error(f"Error crítico inicializando Gemini: {str(e)}")
            self.initialized = False
            return False

    def load_personality_prompt(self) -> str:
        """Carga el prompt de personalidad desde archivo"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "..", "..",
                "config",
                "prompts",
                "assistant_personality.txt"
            )
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            else:
                logger.warning("Archivo de personalidad no encontrado")
                return ""
        except Exception as e:
            logger.error(f"Error cargando prompt de personalidad: {e}")
            return ""

    def _add_to_history(self, role: str, content: str):
        """Agrega un mensaje al historial usando el formato oficial"""
        self.chat_history.append(
            genai.types.Content(  # Cambiar types por genai.types
                role=role,
                parts=[genai.types.Part.from_text(text=content)]  # Cambiar aquí también
            )
        )

    async def process_input(self, text: str, image_path: str = None) -> str:
        try:
            if self.check_connectivity() and self.initialized:
                # Detectar intent y skill apropiada
                skill_name = self._detect_skill(text.lower())
                skill = self.skills.get(skill_name)

                if skill:
                    try:
                        # Configurar parámetros según el tipo de skill
                        if skill_name == 'generation':
                            return await skill.generate_content(
                                text,
                                temperature=0.9,
                                top_p=0.8,
                                top_k=40,
                                max_output_tokens=2048
                            )
                        elif skill_name == 'embeddings':
                            embeddings = await skill.embed_text(text)
                            return f"Embeddings generados con {len(embeddings)} dimensiones"
                        elif skill_name == 'tokens':
                            count = await skill.count_tokens(text)
                            return f"El texto contiene {count} tokens"
                        else:
                            # Usar conversación por defecto
                            generation_config = genai.types.GenerationConfig(
                                temperature=0.9,
                                top_p=0.8,
                                top_k=40,
                                max_output_tokens=2048,
                                stop_sequences=[]
                            )
                            response = await self.chat.send_message(
                                text, 
                                generation_config=generation_config
                            )
                            return response.text if response.text else self._handle_model_error()
                            
                    except Exception as e:
                        logger.error(f"Error procesando con skill {skill_name}: {e}")
                        return self._handle_model_error()
                else:
                    logger.warning(f"No se encontró skill para: {text}")
                    return self._handle_model_error()
            else:
                return self._process_offline(text)
        except Exception as e:
            logger.error(f"Error en NLP: {e}")
            return "Hubo un error procesando tu solicitud."

    def _detect_skill(self, text: str) -> str:
        """Detecta qué skill usar basado en el texto de entrada"""
        for keyword, skill_name in self.intent_mapping.items():
            if keyword in text:
                return skill_name
        return 'conversation'  # Skill por defecto

    async def get_embeddings(self, text: str) -> List[float]:
        """Obtiene embeddings para un texto"""
        return await self.embeddings_skill.embed_text(text)

    async def count_tokens(self, text: str) -> int:
        """Cuenta tokens en un texto"""
        return await self.token_counter_skill.count_tokens(text)

    async def generate_with_params(self, prompt: str, **kwargs) -> str:
        """Genera contenido con parámetros personalizados"""
        return await self.generation_skill.generate_content(prompt, **kwargs)

    def get_available_commands(self) -> str:
        """Retorna información sobre comandos disponibles"""
        return skill_registry.get_skill_info()

    def _process_offline(self, text: str) -> str:
        text = text.lower()
        
        # Determinar el tipo de consulta
        if any(word in text for word in ["explicar", "explicame", "como funciona", "que es"]):
            return self.offline_responses["explanation"][0]
        elif any(word in text for word in ["ayuda", "problema", "error"]):
            return self.offline_responses["technical"][0]
        elif any(word in text for word in ["hola", "buenos", "saludos"]):
            return self.offline_responses["greeting"][0]
        elif any(word in text for word in ["adios", "chau", "hasta luego"]):
            return self.offline_responses["farewell"][0]
        
        # Respuesta por defecto con formato
        return """Lo siento, estoy en modo offline.
        Por favor, intenta tu consulta nuevamente cuando se restablezca la conexión.

Mientras tanto, puedo ayudarte con preguntas básicas."""
        
        return "Estoy en modo offline. Para una mejor respuesta, espera a que se restablezca la conexión."
