"""
Sistema de skills simplificado con registro automático.
"""
from typing import Dict, Any, List, Type, Callable
from functools import wraps

class SkillRegistry:
    """Registro global de skills."""
    _skills: Dict[str, Type['SkillBase']] = {}
    
    @classmethod
    def register(cls, skill_name: str = None):
        def decorator(skill_class: Type['SkillBase']):
            name = skill_name or skill_class.__name__
            cls._skills[name] = skill_class
            return skill_class
        return decorator
    
    @classmethod
    def get_skill(cls, name: str) -> Type['SkillBase']:
        return cls._skills.get(name)

class SkillBase:
    """Clase base para todas las skills."""
    
    def __init__(self):
        self._name = self.__class__.__name__
        self._description = ""
        self._required_params: List[str] = []
    
    @property
    def required_params(self) -> List[str]:
        return self._required_params
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Ejecuta la skill con los parámetros proporcionados."""
        missing = [p for p in self.required_params if p not in kwargs]
        if missing:
            raise ValueError(f"Faltan parámetros requeridos: {missing}")
        return self._execute(**kwargs)
    
    def _execute(self, **kwargs) -> Dict[str, Any]:
        """Implementación específica de la skill."""
        raise NotImplementedError()

# Decorador para simplificar la definición de skills
def skill(name: str = None, required_params: List[str] = None):
    def decorator(cls: Type[SkillBase]):
        @SkillRegistry.register(name)
        class WrappedSkill(cls):
            def __init__(self):
                super().__init__()
                self._required_params = required_params or []
        return WrappedSkill
    return decorator
