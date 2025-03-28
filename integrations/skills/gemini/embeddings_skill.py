from ..base_skill import SkillBase
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class EmbeddingsSkill(SkillBase):
    def __init__(self, model):
        super().__init__()  # Añadir llamada al constructor padre
        self.model = model
        self._name = "embeddings"
        self._description = "Genera embeddings de texto"
        self._intents = {
            "embed": {
                "patterns": ["generar embedding", "embeddings", "vectorizar"],
                "responses": ["Embedding generado correctamente"]
            }
        }

    def get_intents(self) -> Dict:
        """Implementación del método abstracto get_intents"""
        return self._intents
    
    def process_intent(self, intent: str, entities: Optional[List] = None) -> str:
        """Implementación del método abstracto process_intent"""
        if intent in self._intents:
            return self._intents[intent]["responses"][0]
        return "Intent no soportado para embeddings"

    async def embed_text(self, text: str) -> List[float]:
        """Genera embeddings para un texto"""
        try:
            if not text:
                raise ValueError("El texto no puede estar vacío")
                
            result = await self.model.embed_content(text)
            if not result or not result.embedding:
                raise ValueError("No se pudo generar el embedding")
                
            return result.embedding
            
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            raise Exception(f"Error generando embedding: {str(e)}")

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para múltiples textos"""
        try:
            if not texts:
                raise ValueError("La lista de textos no puede estar vacía")
                
            results = await self.model.batch_embed_contents(texts)
            if not results:
                raise ValueError("No se pudieron generar los embeddings")
                
            embeddings = [r.embedding for r in results if r and r.embedding]
            if len(embeddings) != len(texts):
                raise ValueError("No se pudieron generar todos los embeddings")
                
            return embeddings
            
        except Exception as e:
            logger.error(f"Error en batch embedding: {e}")
            raise Exception(f"Error en batch embedding: {str(e)}")
