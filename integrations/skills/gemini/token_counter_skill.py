from ..base_skill import SkillBase
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class TokenCounterSkill(SkillBase):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self._name = "token_counter"
        self._description = "Cuenta tokens en el texto"
        self._intents = {
            "count_tokens": {
                "patterns": ["contar tokens", "tokens", "longitud"],
                "responses": ["Conteo de tokens realizado"]
            }
        }

    def get_intents(self) -> Dict:
        return self._intents
    
    def process_intent(self, intent: str, entities: Optional[List] = None) -> str:
        if intent in self._intents:
            return self._intents[intent]["responses"][0]
        return "Intent no soportado para conteo de tokens"

    async def count_tokens(self, text: str) -> int:
        """Cuenta los tokens en un texto"""
        try:
            result = await self.model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            raise Exception(f"Error contando tokens: {e}")
