"""
Gestor simplificado de skills.
"""
from typing import Dict, Any, List
from .. import SkillRegistry

class SkillManager:
    """Gestor centralizado para ejecutar skills."""
    
    @classmethod
    def get_registered_skills(cls) -> Dict:
        """Retorna todas las skills registradas"""
        return SkillRegistry._skills
    
    @classmethod
    def execute(cls, skill_name: str, **params) -> Dict[str, Any]:
        """Ejecuta una skill por su nombre con los parámetros dados."""
        skill_class = SkillRegistry.get_skill(skill_name)
        if not skill_class:
            raise ValueError(f"Skill '{skill_name}' no encontrada")
            
        skill = skill_class()
        return skill.execute(**params)
