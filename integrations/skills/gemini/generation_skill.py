from ..base_skill import SkillBase
from typing import Dict, Any, Optional, List
from google.generativeai import types
import logging

logger = logging.getLogger(__name__)

class GenerationSkill(SkillBase):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self._name = "generation"
        self._description = "Genera contenido con configuraciones específicas"
        self._intents = {
            "generate": {
                "patterns": ["generar", "crear", "escribir"],
                "responses": ["Contenido generado correctamente"]
            }
        }

    def get_intents(self) -> Dict:
        return self._intents
    
    def process_intent(self, intent: str, entities: Optional[List] = None) -> str:
        if intent in self._intents:
            return self._intents[intent]["responses"][0]
        return "Intent no soportado para generación"

    async def generate_content(self, 
                             prompt: str, 
                             temperature: float = 0.7,
                             top_p: float = 0.8,
                             top_k: int = 40,
                             max_output_tokens: int = 2048,
                             stop_sequences: Optional[List[str]] = None) -> str:
        """Genera contenido con parámetros personalizados"""
        config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
            stop_sequences=stop_sequences or []
        )
        
        try:
            response = await self.model.generate_content(prompt, config)
            return response.text
        except Exception as e:
            raise Exception(f"Error generando contenido: {e}")
