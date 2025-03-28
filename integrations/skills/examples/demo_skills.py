"""
Skills de demostración para probar el sistema.
"""
from .. import skill, SkillBase
from typing import Dict, Any

@skill(name="hola", required_params=["nombre"])
class SaludarDemoSkill(SkillBase):
    def __init__(self):
        super().__init__()
        self._description = "Saluda al usuario por su nombre"
        
    def _execute(self, **kwargs) -> Dict[str, Any]:
        return {
            "mensaje": f"¡Hola {kwargs['nombre']}!",
            "tipo": "saludo"
        }
