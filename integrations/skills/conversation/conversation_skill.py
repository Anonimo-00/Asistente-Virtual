from ..base_skill import SkillBase
from intents.common.basic_intents import COMMON_INTENTS
from typing import Dict, List, Optional

class ConversationSkill(SkillBase):
    def __init__(self):
        self.intents = COMMON_INTENTS

    def get_intents(self) -> Dict:
        return self.intents
    
    def process_intent(self, intent: str, entities: Optional[List] = None) -> str:
        if intent in self.intents:
            import random
            return random.choice(self.intents[intent]["responses"])
        return "No entiendo esa intención"
