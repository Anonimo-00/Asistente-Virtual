from typing import Dict, List, Optional

COMMON_INTENTS: Dict[str, Dict] = {
    "greeting": {
        "keywords": ["hola", "hey", "buenos dias", "buenas tardes", "buenas noches"],
        "responses": ["¡Hola! ¿En qué puedo ayudarte?", "¡Bienvenido! ¿Qué necesitas?"]
    },
    "farewell": {
        "keywords": ["adios", "chao", "hasta luego", "nos vemos"],
        "responses": ["¡Hasta luego!", "¡Que tengas un buen día!", "¡Adiós!"]
    },
    "thanks": {
        "keywords": ["gracias", "te lo agradezco", "muchas gracias"],
        "responses": ["¡De nada!", "Para eso estoy", "Con gusto"]
    }
}
