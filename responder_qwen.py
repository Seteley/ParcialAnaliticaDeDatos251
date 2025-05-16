import requests
from clasificador import obtener_respuesta

API_BASE_URL = "http://localhost:11434/v1/chat/completions"
headers = {"Content-Type": "application/json"}

def responder_saludo(mensaje_usuario):
    inputs = [
        {
            "role": "system",
            "content": (
                "Eres BotRedes7, un asistente virtual amigable que responde saludos de forma cálida, "
                "cercana y positiva. Además, siempre te presentas diciendo que eres un bot que informa en tiempo real "
                "sobre la actividad en redes sociales, especialmente Twitter. Menciona que puedes mostrar seguidores, "
                "gráficos de tendencias y ayudar a alcanzar metas de seguidores. Sé simpático pero breve. También al final pídele el nombre del usuario e indicarle que sea con el arroba."
            )
        },
        {
            "role": "user",
            "content": mensaje_usuario
        }
    ]
    return _llamar_api_qwen(inputs)


def responder_despedida(mensaje_usuario):
    inputs = [
        {
            "role": "system",
            "content": (
                "Eres BotRedes7, un asistente virtual amigable que responde despedidas de forma cordial, "
                "amigable y cercana. El usuario se está despidiendo. Devuelve una respuesta breve y amable."
            )
        },
        {
            "role": "user",
            "content": mensaje_usuario
        }
    ]
    return _llamar_api_qwen(inputs)


def _llamar_api_qwen(inputs):
    response = requests.post(
        API_BASE_URL,
        headers=headers,
        json={"model": "qwen3:1.7b", "messages": inputs}
    )
    if response.ok:
        return obtener_respuesta(response.json()["choices"][0]["message"]["content"])
    return "Lo siento, tuve un problema al responder."