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
import yaml  # Añadir importación de yaml

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env"))
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.initialized = False
        self.supports_images = False
        self.model = None
        self.model_name = None  # Añadir atributo model_name
        self.embeddings_skill = None
        self.token_counter_skill = None
        self.generation_skill = None
        
        try:
            self._load_config()
            self.init_gemini()
            self.initialized = True
        except Exception as e:
            logger.error(f"Error crítico inicializando Gemini: {e}")
            raise

    def _load_config(self):
        """Carga la configuración del servicio NLP"""
        try:
            config_path = os.path.join("config", "credentials.yml")
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)  # Cambiar json.load por yaml.safe_load
                
            google_ai_config = config.get('google_ai', {})
            api_key = google_ai_config.get('api_key')
            if not api_key:
                raise ValueError("API key no encontrada en la configuración")
                
            genai.configure(api_key=api_key)
            
            # Cargar modelo configurado y guardar nombre
            self.model_name = google_ai_config.get('model', 'gemini-pro')
            self.model = genai.GenerativeModel(self.model_name)
            
            # Configuración generación
            self.generate_config = {
                "temperature": google_ai_config.get('temperature', 0.7),
                "top_p": google_ai_config.get('top_p', 0.8),
                "top_k": google_ai_config.get('top_k', 40),
                "max_output_tokens": google_ai_config.get('max_tokens', 2048),
            }
            
            logger.info(f"Configuración NLP cargada correctamente: modelo={self.model_name}")
            
        except Exception as e:
            logger.error(f"Error cargando configuración NLP: {e}")
            raise

    def init_gemini(self):
        """Inicializa el modelo Gemini y sus skills"""
        try:
            # Verificar si el modelo está disponible
            if not self.model:
                raise ValueError("Modelo no inicializado")
                
            # Inicializar skills
            self._init_skills()
            
            logger.info(f"Servicio NLP inicializado correctamente con modelo: {self.model}")
            
        except Exception as e:
            logger.error(f"Error inicializando Gemini: {e}")
            raise

    def _init_skills(self):
        """Inicializa las skills del servicio"""
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
