import os
from gpt4all import GPT4All

# Configurar el directorio para los modelos
MODEL_PATH = os.path.join(os.path.expanduser("~"), ".cache", "gpt4all")
os.makedirs(MODEL_PATH, exist_ok=True)

# Usar un modelo compatible
model = GPT4All("orca-mini-3b.q4_0.gguf")

# Configurar y usar el modelo
with model.chat_session():
    response = model.generate(
        "¿Cómo puedo ejecutar LLMs eficientemente en mi laptop?",
        max_tokens=512,
        temp=0.7,
        top_k=40,
        top_p=0.4
    )
    print("\nRespuesta:", response)