from typing import Dict, List, Callable, Any
import inspect

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, Callable] = {}
        self._contexts: Dict[str, List[str]] = {}
        self._parameters: Dict[str, Dict[str, type]] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, contexts: List[str], description: str = ""):
        """Decorador para registrar una skill con sus contextos"""
        def decorator(func: Callable):
            skill_name = func.__name__
            self._skills[skill_name] = func
            self._contexts[skill_name] = contexts
            self._descriptions[skill_name] = description
            
            # Obtener parámetros requeridos
            sig = inspect.signature(func)
            params = {
                name: param.annotation 
                for name, param in sig.parameters.items() 
                if param.default == inspect.Parameter.empty
            }
            self._parameters[skill_name] = params
            return func
        return decorator

    def get_skill_context(self, text: str) -> tuple[Callable, Dict[str, Any]]:
        """Encuentra la skill más apropiada y extrae sus parámetros"""
        matching_skills = []
        
        # Buscar skills que coincidan con el contexto
        for skill_name, contexts in self._contexts.items():
            if any(context.lower() in text.lower() for context in contexts):
                matching_skills.append(skill_name)
        
        if not matching_skills:
            return None, {}
            
        # Usar la primera skill que coincida
        skill_name = matching_skills[0]
        skill = self._skills[skill_name]
        
        # Extraer parámetros requeridos
        params = {}
        required_params = self._parameters[skill_name]
        
        # Aquí podrías implementar extracción de parámetros más sofisticada
        # Por ahora solo un ejemplo simple
        for param_name, param_type in required_params.items():
            # Buscar valor en el texto según el tipo
            if param_type == str:
                # Buscar palabras después del contexto
                words = text.split()
                if len(words) > 1:
                    params[param_name] = words[-1]
            elif param_type == int:
                # Buscar números en el texto
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    params[param_name] = int(numbers[0])
                    
        return skill, params

    def get_skill_info(self) -> str:
        """Retorna información sobre todas las skills registradas"""
        info = []
        for skill_name in self._skills:
            contexts = self._contexts[skill_name]
            params = self._parameters[skill_name]
            desc = self._descriptions[skill_name]
            
            param_info = ", ".join(f"{name}: {t.__name__}" for name, t in params.items())
            info.append(f"Skill: {skill_name}")
            info.append(f"Contextos: {', '.join(contexts)}")
            info.append(f"Parámetros: {param_info}")
            info.append(f"Descripción: {desc}\n")
            
        return "\n".join(info)

# Instancia global
skill_registry = SkillRegistry()
