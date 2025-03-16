from typing import Dict, Any

class SkillBase:
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Las skills deben implementar el método execute")
