"""
Pruebas para las skills básicas
"""
from integrations.skills.examples.demo_skills import SaludarDemoSkill
from integrations.skills.examples.user_skill import UserProfileSkill
from integrations.skills.base.skill_manager import SkillManager

def test_skills():
    """Función simple para probar las skills"""
    
    print("Skills registradas:", SkillManager.get_registered_skills().keys())
    
    # Probar guardar datos de usuario
    print("\nGuardando dato de usuario:")
    try:
        resultado = SkillManager.execute(
            "perfil",
            accion="guardar",
            categoria="datos_personales",
            clave="ciudad",
            valor="Madrid"
        )
        print(f"Resultado: {resultado}")
        
        # Probar obtener el dato guardado
        resultado = SkillManager.execute(
            "perfil",
            accion="obtener",
            categoria="datos_personales",
            clave="ciudad"
        )
        print(f"Dato recuperado: {resultado}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_skills()
