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
Asistente_Virtual/
├── assets/                 
│   └── assistant_logo.png          # Recursos gráficos globales (logo, iconos, etc.)
├── config/                     
│   ├── credentials.yml             # Claves de API y configuración de servicios externos (LUIS, QnA Maker, etc.)
│   └── settings.json               # Configuración global (idioma, zona horaria, etc.)
├── data/                       
│   ├── training/                   # Corpus de entrenamiento (frases, ejemplos de intents)
│   ├── entities/                   # Definición de entidades personalizadas
│   └── user_profile.json           # Perfil o preferencias del usuario
├── dialogs/                    
│   ├── flows/                      # Flujos de conversación organizados por escenarios
│   └── responses/                  # Plantillas de respuestas (dinámicas o estáticas)
├── integrations/               
│   ├── skills/                     # Módulos de habilidades (skills) específicas del asistente
│   │   ├── base/
│   │   │   └── skill_manager.py    # Gestión y carga de habilidades base
│   │   ├── conversation/
│   │   │   └── conversation_skill.py  # Habilidad para manejar diálogos generales
│   │   ├── web_search/
│   │   │   └── web_search_skill.py    # Habilidad para realizar búsquedas en la web
│   │   └── __init__.py             # Inicializador del módulo de skills
│   ├── ui/                         # Interfaz de usuario desarrollada con Flet (solo para PC)
│   │   ├── flet_app.py             # Código principal de la aplicación Flet
│   │   └── assets/                 # Recursos específicos de la UI (estilos, imágenes adicionales)
│   └── webhooks/                   # Handlers para webhooks y fulfillment
│       └── webhook_handler.py      # Lógica para gestionar solicitudes entrantes de APIs externas
├── services/                    
│   ├── nlp/                        # Servicios para procesamiento del lenguaje natural
│   │   └── nlp_service.py          # Integración con motores NLP (LUIS, Dialogflow, etc.)
│   ├── messaging/                  # Adaptadores para distintos canales de mensajería
│   │   └── message_service.py      # Gestión de envío y recepción de mensajes
│   └── skills/                     # Servicios auxiliares para habilidades
│       ├── help_skill.py           # Servicio de ayuda e información al usuario
│       └── skill_registry.py       # Registro y administración de habilidades disponibles
├── tests/                        
│   ├── unit/                      # Pruebas unitarias de módulos y funciones individuales
│   ├── integration/               # Pruebas de integración (flujos de diálogo, conexiones a servicios)
│   └── test_main.py               # Pruebas generales e integración del sistema
├── utils/                        
│   ├── backup_manager.py          # Gestión y ejecución de copias de seguridad
│   ├── config.py                  # Funciones para cargar y manejar la configuración
│   ├── exceptions.py              # Definición de excepciones personalizadas
│   ├── helpers.py                 # Funciones utilitarias de uso común en el proyecto
│   ├── project_scanner.py         # Herramienta para analizar y reportar la estructura del proyecto
│   └── state_manager.py           # Gestión del estado global y sesiones de la aplicación
├── README.md                      # Documentación general y guía de uso del proyecto
├── requirements.txt               # Lista de dependencias del proyecto
└── main.py                        # Punto de entrada principal de la aplicación

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