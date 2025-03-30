# Asistente Virtual Personal

Este proyecto es un asistente virtual personal desarrollado en Python, diseñado para integrarse con diversas APIs y proporcionar una variedad de funcionalidades.

## Características

## Librerías Recomendadas para el Desarrollo de la UI en Python 3.12

- **Flet:** Una opción moderna y sencilla para construir interfaces web y de escritorio en Python.
- **PySide6 (Qt for Python):** Ofrece amplias posibilidades de personalización y es ideal para interfaces complejas y de alta calidad.
- **Kivy:** Especializada en aplicaciones táctiles y responsivas, ideal para dispositivos móviles y de escritorio.
- **Dear PyGui:** Basada en el paradigma de “modo inmediato”, excelente para prototipos y aplicaciones con actualizaciones dinámicas.


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
│   ├── assistant_logo.png          # Logo e íconos globales
│   └── assistant-hero.png          # Imagen adicional para la presentación (hero)
├── config/                     
│   ├── credentials.yml             # Claves de API y configuración de servicios externos (por ejemplo, LUIS, QnA Maker)
│   └── settings.json               # Configuración global (idioma, zona horaria, etc.)
├── data/                       
│   ├── training/                   # Corpus de entrenamiento (frases, ejemplos para intents)
│   ├── entities/                   # Definiciones de entidades personalizadas
│   ├── cache/                      # Datos temporales para mejorar el rendimiento
│   │   ├── audio/                  
│   │   ├── documents/              
│   │   ├── images/                 
│   │   ├── search/                 
│   │   └── video/                  
│   ├── user_profile.json           # Perfil y preferencias del usuario
│   └── global_vars.json            # Variables globales (por ejemplo, parámetros compartidos)
├── dialogs/                    
│   ├── flows/                      # Flujos de conversación estructurados por escenarios
│   └── responses/                  # Plantillas de respuestas (estáticas o dinámicas)
├── integrations/               
│   ├── skills/                     # Módulos de habilidades (skills) específicas del asistente
│   │   ├── base/
│   │   │   └── skill_manager.py    # Gestión y carga de habilidades base
│   │   ├── conversation/
│   │   │   └── conversation_skill.py  # Habilidad para manejar diálogos generales
│   │   ├── examples/               # Ejemplos de skills para referencia o pruebas
│   │   │   ├── basic_skills.py     
│   │   │   ├── demo_skills.py      
│   │   │   ├── user_skill.py       
│   │   │   └── __init__.py         
│   │   ├── gemini/
│   │   │   ├── embeddings_skill.py   # Skill para trabajar con embeddings
│   │   │   ├── generation_skill.py   # Skill para generación de contenido
│   │   │   └── token_counter_skill.py # Skill para contar tokens en textos
│   │   ├── web_search/
│   │   │   └── web_search_skill.py   # Skill para realizar búsquedas en la web
│   │   ├── web_skill/              # (Si se requiere alguna habilidad web adicional)
│   │   │   └── __init__.py         
│   │   ├── base_skill.py           # Clase base para todas las skills
│   │   ├── conversation.py         # Funciones comunes para la gestión de diálogos
│   │   └── __init__.py             # Inicializador del módulo de skills
│   ├── ui/                         # Interfaz de usuario (UI) desarrollada con Flet para PC
│   │   ├── flet_app.py             # Código principal de la aplicación Flet (punto de entrada de la UI)
│   │   ├── config_window.py        # Ventana de configuración de la UI
│   │   ├── assets/
│   │   └── settings_view.py        # Vista para ajustes y configuraciones de la UI
│   └── webhooks/                   # Handlers para procesamiento de webhooks y fulfillment
│       └── webhook_handler.py      # Lógica para gestionar solicitudes entrantes de APIs externas
├── intents/                    
│   ├── common/
│   │   └── basic_intents.py        # Intents predeterminados (bienvenida, fallback, cancelación)
│   └── custom/                     # Intents específicos definidos por el usuario (actualmente vacío o en desarrollo)
├── logs/                    # Aquí se guardarán los archivos de log (errores, info, etc.)
├── services/                    
│   ├── nlp/                        # Servicios para procesamiento del lenguaje natural
│   │   └── nlp_service.py          # Conexión e integración con motores NLP (LUIS, Dialogflow, etc.)
│   ├── messaging/                  # Adaptadores para distintos canales de mensajería
│   │   └── message_service.py      # Gestión del envío y recepción de mensajes
│   └── skills/                     # Servicios auxiliares para las skills
│       ├── help_skill.py           # Servicio de ayuda e información al usuario
│       └── skill_registry.py       # Registro y administración de las skills disponibles
├── tests/                        
│   ├── unit/                      # Pruebas unitarias para funciones y clases individuales
│   ├── integration/               # Pruebas de integración (flujos de diálogo, conexiones a servicios)
│   └── test_main.py               # Pruebas generales e integración del sistema
├── utils/                        
│   ├── backup_manager.py          # Gestión y ejecución de copias de seguridad del sistema
│   ├── config.py                  # Funciones para cargar y manejar la configuración
│   ├── exceptions.py              # Definición de excepciones personalizadas
│   ├── helpers.py                 # Funciones utilitarias de uso común en el proyecto
│   ├── project_scanner.py         # Herramienta para analizar y reportar la estructura del proyecto
│   └── state_manager.py           # Gestión del estado global y de las sesiones de la aplicación
├── .gitignore                     # Archivos y carpetas a ignorar por Git
├── README.md                      # Documentación general y guía de uso del proyecto
├── requirements.txt               # Lista de dependencias del proyecto
└── main.py                        # Punto de entrada principal de la aplicación

```

## Librerías Recomendadas para el Desarrollo de la UI en Python 3.12

- **Flet:** Una opción moderna y sencilla para construir interfaces web y de escritorio en Python.
- **PySide6 (Qt for Python):** Ofrece amplias posibilidades de personalización y es ideal para interfaces complejas y de alta calidad.
- **Kivy:** Especializada en aplicaciones táctiles y responsivas, ideal para dispositivos móviles y de escritorio.
- **Dear PyGui:** Basada en el paradigma de “modo inmediato”, excelente para prototipos y aplicaciones con actualizaciones dinámicas.


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
Plan de Acción para el Asistente Virtual Personal "Central"
Este proyecto es un asistente virtual personal desarrollado en Python, diseñado para integrarse con diversas APIs y proporcionar una variedad de funcionalidades. El plan se divide en tres fases principales, cada una con objetivos, tareas y entregables específicos.

Fase 1: Fundamentos e Integraciones Básicas (8 semanas)
Objetivo:
Establecer la estructura base del proyecto, configurar el entorno de desarrollo y desarrollar las integraciones iniciales, tanto en la interfaz gráfica como en la conexión con servicios esenciales.

Semanas 1-2: Estructura del Proyecto y Configuración del Entorno
Tareas:

Configurar el entorno de desarrollo en Python 3.12 (crear entorno virtual, instalar dependencias).

Definir y documentar la estructura del proyecto (carpetas, módulos y flujo de trabajo).

Establecer un sistema de logging robusto y un monitoreo básico de conexión a Internet.

Configurar la interfaz gráfica inicial con Flet (u otra librería elegida), mostrando un layout básico basado en tarjetas.

Entregables:

Entorno configurado y estructura del proyecto documentada.

Primer prototipo de UI (layout base) con soporte para logging.

Semanas 3-4: Integración con Servicios de Google
Tareas:

Configurar autenticación y gestionar credenciales de forma segura (uso de archivos .env y configuración en config/).

Desarrollar la integración con APIs de Gmail, Calendar y Contacts (probar consultas y manejo de datos).

Manejar errores y excepciones en la conexión con servicios externos.

Entregables:

Módulos de integración de Google Services funcionales y testeados.

Documentación de los procesos de autenticación y manejo de errores.

Semanas 5-6: Sistema de Notas y Gestión de Datos
Tareas:

Implementar un sistema de notas con capacidad CRUD (crear, leer, actualizar, borrar), utilizando una base de datos local (por ejemplo, SQLite).

Incluir funcionalidad de búsqueda por palabras clave en las notas.

Crear una interfaz para visualizar y gestionar las notas, integrada en la UI mediante tarjetas.

Entregables:

Sistema de notas completamente funcional.

Integración de la funcionalidad de búsqueda en la UI.

Pruebas unitarias para las operaciones CRUD.

Semanas 7-8: Gestión de Archivos y Funciones de Voz
Tareas:

Desarrollar módulos para la gestión de archivos (subir, descargar, organizar).

Integrar servicios de Text-to-Speech (TTS) y Speech-to-Text (STT), asegurando la interacción conversacional.

Realizar pruebas de usabilidad para el reconocimiento de voz y respuesta automática.

Entregables:

Módulos de gestión de archivos y TTS/STT integrados.

Demostración funcional de la interacción por voz en la UI.

Fase 2: Funcionalidades Avanzadas (12 semanas)
Objetivo:
Ampliar las funcionalidades del asistente, incluyendo herramientas de productividad, integración de comandos avanzados y mejoras en la interacción, asegurando una experiencia de usuario más rica.

Semanas 9-10: Programación de Tareas y Comandos Avanzados
Tareas:

Desarrollar un sistema de tareas programadas (incluyendo tareas recurrentes) utilizando una librería como APScheduler.

Crear una interfaz para la gestión de tareas que se integre en el dashboard de Central.

Implementar la configuración de atajos y comandos personalizados (configurables desde la ventana de settings).

Entregables:

Módulo de tareas y programación de comandos con interfaz gráfica.

Documentación de flujos y pruebas de funcionamiento.

Semanas 11-12: Integración de Funcionalidades Office
Tareas:

Desarrollar integraciones con Excel (por ejemplo, usando openpyxl) para extraer y procesar datos.

Configurar la integración con WhatsApp (por ejemplo, mediante WhatsApp Web API o soluciones de terceros) para el envío/recepción de mensajes.

Entregables:

Módulos de integración con Office (Excel) y WhatsApp, con pruebas de funcionamiento.

Ejemplos de uso documentados en la interfaz.

Semanas 13-14: Sistema Avanzado de Búsqueda y Actualización de Datos
Tareas:

Mejorar el sistema de búsqueda web con algoritmos optimizados (posiblemente usando bibliotecas de búsqueda difusa).

Configurar la opción de establecer intervalos de actualización de datos en la UI (configurable en settings).

Entregables:

Módulo de búsqueda avanzado y funcional.

Configuración de intervalos de actualización integrada y testeada.

Semanas 15-16: Modo Inmersivo y Configuración de Feedback
Tareas:

Implementar un "modo inmersivo" o de lectura que minimice distracciones y optimice la visualización de información.

Desarrollar opciones de feedback visual y sonoro (por ejemplo, animaciones o sonidos de confirmación) que se puedan activar desde la ventana de configuración.

Entregables:

Funcionalidad de modo inmersivo y opciones de feedback integradas.

Pruebas de usabilidad y documentación del modo inmersivo.

Semanas 17-18: Optimización de Rendimiento y Seguridad
Tareas:

Realizar pruebas de rendimiento y optimización en la UI y en los módulos de integración.

Implementar mejoras de seguridad (validación de datos, manejo robusto de excepciones).

Configurar un panel de análisis y logs para monitorear el rendimiento y detectar problemas.

Entregables:

Informes de rendimiento y seguridad, con optimizaciones aplicadas.

Integración del panel de logs en la UI.

Fase 3: Escalabilidad e Integración de IA Local (Tiempo variable)
Objetivo:
Preparar el sistema para futuras ampliaciones, integrando módulos de inteligencia artificial local y desplegando la aplicación en la nube si fuese necesario.

Tareas y Objetivos:
Integración de IA Local:
Desarrollar e integrar módulos de IA local para mejorar la respuesta y personalización sin depender únicamente de servicios externos.

Despliegue en la Nube:
Preparar el proyecto para su despliegue en servicios cloud (por ejemplo, AWS, GCP o Azure) y ajustar la escalabilidad.

Optimización y Monitorización Avanzada:
Implementar herramientas avanzadas de monitorización y optimización (caché distribuido, balanceo de carga, etc.).

Actualizaciones y Mantenimiento Continuo:
Establecer un plan de mantenimiento y actualizaciones periódicas basadas en feedback y análisis de uso.

Integración Tipográfica
Utiliza las diferentes versiones de SpaceGrotesk que se encuentran en la carpeta integrations/ui/assets para definir la identidad tipográfica de la interfaz, asegurando una apariencia moderna, coherente y que complemente el resto de los elementos de diseño.

Recomendaciones Generales Adicionales
Coherencia y Modularidad:
Asegúrate de que cada componente y efecto se aplique de forma uniforme en toda la UI para lograr una experiencia cohesiva y escalable.

Usabilidad y Accesibilidad:
Realiza pruebas de usabilidad y accesibilidad para validar que la alternancia entre modos claro y oscuro y el acceso a la configuración sean intuitivos y efectivos.

Feedback en Tiempo Real y Microinteracciones:
Implementa microinteracciones y animaciones que brinden feedback inmediato (por ejemplo, cambios de color o animaciones al confirmar un cambio) para reforzar la sensación de control y mejorar la experiencia.

Personalización Integral:
Incorpora opciones avanzadas (como la configuración del tono conversacional, modo inmersivo, ajustes de sensibilidad de reconocimiento de voz y controles de accesibilidad adicionales) para adaptar la UI a tus preferencias person

## Uso

```bash
python main.py
```

## Licencia
MIT
