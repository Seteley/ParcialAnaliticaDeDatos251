import requests

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/8d84ee30b071bb4000da4b51d58fb8ed/ai/run/"
headers = {"Authorization": "Bearer e_-2c5fjDgOMZKKrbiNawggGd2qvG8vtWJZXukHb"}

def clasificar_intencion(mensaje_usuario):
    model = "@cf/meta/llama-3-8b-instruct"

    inputs = [
        {
            "role": "system",
            "content": (
                "Tu nombre es BotRedes7, un asistente virtual amigable que informa en tiempo real sobre "
                "la actividad en redes sociales, especialmente Twitter. Ayudas a los usuarios a conocer cuántos "
                "seguidores tienen, si aumentaron o disminuyeron, cuánto les falta para alcanzar una meta, "
                "y presentas gráficos con las tendencias recientes. También puedes mostrar dashboards con datos generales. "
                "Responde de forma clara, útil y cercana. Tu tarea ahora es clasificar intenciones del usuario."
            )
        },
        {
            "role": "user",
            "content": (
                "Clasifica la intención del siguiente mensaje del usuario en una de las siguientes categorías:\n"
                "- Inicio\n"
                "- Saludo\n"
                "- Consultar Seguidores\n"
                "- Cambio Seguidores\n"
                "- Consulta Meta\n"
                "- Consulta Pérdida Seguidores\n"
                "- Ver Dashboard\n"
                "- Despedida\n"
                "- Otro\n\n"
                "Responde únicamente con el nombre de la categoría, sin ninguna explicación adicional.\n\n"
                f"Mensaje: '{mensaje_usuario}'"
            )
        }
    ]

    response = requests.post(
        f"{API_BASE_URL}{model}",
        headers=headers,
        json={"messages": inputs}
    )

    if response.status_code == 200:
        data = response.json()
        return data["result"]["response"].strip()
    else:
        print("Error:", response.status_code, response.text)
        return "Error"

# Ejemplo de uso
mensaje = "buenos días, mi king"
intencion = clasificar_intencion(mensaje)
print("Intención:", intencion)
