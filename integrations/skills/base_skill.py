from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class SkillBase(ABC):
    @abstractmethod
    def get_intents(self) -> Dict:
        pass
    
    @abstractmethod
    def process_intent(self, intent: str, entities: Optional[List] = None) -> str:
        pass
