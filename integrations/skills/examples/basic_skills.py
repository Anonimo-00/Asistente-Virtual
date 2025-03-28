"""
Ejemplos de skills usando el nuevo sistema.
"""
from .. import skill, SkillBase
from typing import Dict, Any

@skill(name="saludar", required_params=["nombre"])
class SaludarSkill(SkillBase):
    def _execute(self, **kwargs) -> Dict[str, Any]:
        return {
            "mensaje": f"¡Hola {kwargs['nombre']}!"
        }

@skill(required_params=["texto"])
class TraducirSkill(SkillBase):
    def _execute(self, **kwargs) -> Dict[str, Any]:
        # Aquí iría la lógica real de traducción
        return {
            "traduccion": f"Traducción de: {kwargs['texto']}"
        }

# Ejemplo de uso:
if __name__ == "__main__":
    from ..base.skill_manager import SkillManager
    
    # Usar skill por nombre
    resultado = SkillManager.execute("saludar", nombre="Juan")
    print(resultado)  # {"mensaje": "¡Hola Juan!"}
    
    # Usar otra skill
    resultado = SkillManager.execute("TraducirSkill", texto="Hello")
    print(resultado)  # {"traduccion": "Traducción de: Hello"}
