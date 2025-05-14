import requests

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/8d84ee30b071bb4000da4b51d58fb8ed/ai/run/"
headers = {
    "Authorization": "Bearer e_-2c5fjDgOMZKKrbiNawggGd2qvG8vtWJZXukHb"
}

def responder_saludo(mensaje_usuario):
    inputs = [
        {
            "role": "system",
            "content": (
                "Eres BotRedes7, un asistente virtual amigable que responde saludos de forma cálida, "
                "cercana y positiva. Además, siempre te presentas diciendo que eres un bot que informa en tiempo real "
                "sobre la actividad en redes sociales, especialmente Twitter. Menciona que puedes mostrar seguidores, "
                "gráficos de tendencias y ayudar a alcanzar metas. Sé simpático pero breve."
            )
        },
        {
            "role": "user",
            "content": mensaje_usuario
        }
    ]
    return _llamar_api_llama(inputs)


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
    return _llamar_api_llama(inputs)

def _llamar_api_llama(inputs):
    response = requests.post(
        f"{API_BASE_URL}@cf/meta/llama-3-8b-instruct",
        headers=headers,
        json={"messages": inputs}
    )
    if response.ok:
        return response.json()["result"]["response"]
    return "Lo siento, tuve un problema al responder."
