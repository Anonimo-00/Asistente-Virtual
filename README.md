# Asistente Virtual Personal

Este proyecto es un asistente virtual personal desarrollado en Python, diseñado para integrarse con diversas APIs y proporcionar una variedad de funcionalidades.

## Características

- 🎯 Monitoreo de Conexión a Internet con estado en tiempo real
- 🤖 Integración con Gemini AI para procesamiento de lenguaje natural
- 🖼️ Soporte para análisis de imágenes con Gemini Vision
- 🔄 Modo offline con respuestas inteligentes
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
```

## Estructura

```
Asistente Virtual/
├── config/
├── integrations/
├── services/
├── utils/
├── global_vars.py
└── main.py
```

## Uso

```bash
python main.py
```

## Licencia
MIT