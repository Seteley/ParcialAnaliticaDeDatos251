import execjs

# Cargar el código JavaScript de Puter.js
with open("puter.js", "r") as file:
    js_code = file.read()

# Inicializar el contexto de ejecución
context = execjs.compile(js_code)

# Definir la función para interactuar con Grok
def chat_with_grok(prompt):
    return context.call("puter.ai.chat", prompt, {"model": "x-ai/grok-3-beta"})

# Generar una respuesta
response = chat_with_grok("¿Cuál es la capital de Perú?")
print(response)
