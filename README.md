# Asistente Virtual Personal

Este proyecto es un asistente virtual personal desarrollado en Python, diseñado para integrarse con diversas APIs y proporcionar una variedad de funcionalidades.

## Características

- 🎯 Monitoreo de Conexión a Internet con estado en tiempo real
- 🤖 Integración con Gemini AI para procesamiento de lenguaje natural
- 🖼️ Soporte para análisis de imágenes con Gemini Vision
- 🔄 Modo offline con respuestas inteligentes
- 🔍 Búsqueda web con extracción de contenido
- 🗣️ Text-to-Speech y Speech-to-Text
- 📱 Interfaz gráfica amigable con Flet
- 🌐 Estado de conexión en tiempo real
- 📊 Sistema de logs y monitoreo
- ⚙️ Configuración personalizable

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```
3. Instalar dependencias:
```bash
pip install -r requirements.txt
```
4. Configurar archivo `.env` en la carpeta `config/`:
```env
LANGUAGE_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_api_key_here
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

## Estructura del Proyecto

```
Asistente Virtual/
├── config/
│   ├── credentials.yml     # Claves de API, configuración de servicios
│   └── settings.json       # Configuraciones generales
├── integrations/
│   ├── skills/
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   └── skill_manager.py  # Gestor central de skills
│   │   ├── conversation/         # Skills de conversación
│   │   ├── system/              # Skills del sistema
│   │   └── utils/               # Skills de utilidades
│   └── webhooks/
├── data/
│   ├── training/           # Corpus y frases de entrenamiento
│   └── entities/           # Definiciones de entidades
├── intents/
│   ├── common/            # Intents predeterminados
│   └── custom/            # Intents específicos
├── dialogs/
│   ├── flows/             # Flujos de conversación
│   └── responses/         # Plantillas de respuestas
├── integrations/
│   ├── ui/
│   │   ├── flet_app.py    # Interfaz de usuario
│   │   └── assets/        # Recursos estáticos
│   ├── skills/            # Habilidades del asistente
│   └── webhooks/          # Conexiones externas
├── services/
│   ├── nlp/               # Procesamiento de lenguaje
│   └── messaging/         # Gestión de mensajes
├── tests/
│   ├── unit/             
│   └── integration/      
└── utils/
    └── helpers.py         # Utilidades comunes
```

## Desarrollo de Skills

Las skills son módulos independientes que implementan funcionalidades específicas.
Cada skill debe:

1. Heredar de `SkillBase`
2. Implementar los métodos abstractos:
   - `get_required_params()`
   - `execute()`
3. Registrarse en el `SkillManager`

Ejemplo:

```python
from integrations.skills import SkillBase

class MySkill(SkillBase):
    def __init__(self):
        super().__init__()
        self._description = "Mi skill personalizada"
    
    def get_required_params(self):
        return ["param1", "param2"]
        
    def execute(self, params):
        # Implementación de la skill
        return {"result": "success"}
```

## Pruebas de Skills

Para probar las skills, ejecute:

```bash
# Desde el directorio raíz del proyecto
python -m tests.skills.test_basic_skills
```

## Plan de Desarrollo

El desarrollo del asistente virtual está organizado en tres fases principales:

### Fase 1: Fundamentos e Integraciones Básicas (8 semanas)

#### Semanas 1-2: Estructura del Proyecto y Entorno
- Configuración del entorno de desarrollo
- Implementación de estructura modular
- Sistema de logs y monitoreo de conexión
- Interfaz gráfica básica con Flet

#### Semanas 3-4: Integración Google Services
- Autenticación y credenciales seguras
- Integración Gmail, Calendar y Contacts
- Manejo de errores y excepciones

#### Semanas 5-6: Sistema de Notas
- Sistema de notas persistente
- CRUD de notas
- Búsqueda por palabras clave

#### Semanas 7-8: Sistema de Archivos y Voz
- Gestión de archivos
- Integración Text-to-Speech
- Integración Speech-to-Text

### Fase 2: Funcionalidades Avanzadas (12 semanas)

#### Semanas 9-10: Programación de Tareas
- Sistema de tareas programadas
- Tareas recurrentes

#### Semanas 11-12: Integraciones Office
- Integración con Excel
- Integración con WhatsApp

#### Semanas 13-14: Búsqueda Avanzada
- Mejoras al sistema de búsqueda
- Algoritmos optimizados

#### Semanas 15-16: Traductor
- Integración servicio de traducción

#### Semanas 17-18: Optimización
- Mejoras de rendimiento
- Pruebas exhaustivas

### Fase 3: Escalabilidad e IA Local

- Integración de IA local
- Despliegue en la nube
- Optimizaciones de rendimiento

## Uso

```bash
python main.py
```

## Licencia
MIT