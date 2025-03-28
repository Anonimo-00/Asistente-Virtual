from .. import skill, SkillBase
from typing import Dict, Any
from utils.user_manager import UserManager

@skill(name="perfil", required_params=["accion"])
class UserProfileSkill(SkillBase):
    def __init__(self):
        super().__init__()
        self._description = "Gestiona el perfil del usuario"
        self.user_manager = UserManager()

    def _execute(self, **kwargs) -> Dict[str, Any]:
        accion = kwargs["accion"]
        
        if accion == "guardar":
            categoria = kwargs.get("categoria")
            clave = kwargs.get("clave")
            valor = kwargs.get("valor")
            
            if not all([categoria, clave, valor]):
                return {"error": "Faltan parámetros requeridos"}
                
            self.user_manager.actualizar_dato(categoria, clave, valor)
            return {
                "mensaje": f"Dato guardado: {categoria}/{clave}",
                "valor": valor
            }
            
        elif accion == "obtener":
            categoria = kwargs.get("categoria")
            clave = kwargs.get("clave")
            
            if not all([categoria, clave]):
                return {"error": "Faltan parámetros requeridos"}
                
            valor = self.user_manager.obtener_dato(categoria, clave)
            return {
                "valor": valor
            }

        return {"error": "Acción no válida"}
