import re
import json
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os

from clasificador import clasificar_intencion
from responder_qwen import responder_saludo, responder_despedida
from funcionesauxiliar import obtener_link_dashboard
from conectaresp import guardar_datos_en_json, consultar_serial  # Se importan desde conectaresp

BOT_TOKEN = "7884267779:AAEvYsRU8GNbaBIGOIn81ZDitkkX5LTHPLA"
user_data = {}

executor = ThreadPoolExecutor()
serial_lectura_activa = False  # Controla si la lectura serial está activa

def actualizar_nombre_usuario_api_sync(usuario):
    url = 'https://parcialanaliticadedatos251-1.onrender.com/nombre_usuario'
    datos = {"nombre_usuario": usuario}
    try:
        requests.post(url, json=datos)
    except Exception:
        pass  # Mejor loggear en producción

async def actualizar_nombre_usuario_api(usuario):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, actualizar_nombre_usuario_api_sync, usuario)

async def actualizar_json_y_api(usuario):
    ruta_json = "Datos_consulta.json"
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        datos = {}

    datos["nombre_usuario"] = usuario

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    await actualizar_nombre_usuario_api(usuario)

def extraer_username(texto):
    match = re.search(r'@(\w{1,15})', texto)
    if match:
        return match.group(1)
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global serial_lectura_activa

    user_message = update.message.text
    user_id = update.message.from_user.id
    intencion = clasificar_intencion(user_message)

    if intencion == "Cambiar de cuenta":
        user_data.pop(user_id, None)
        await update.message.reply_text("Claro, ¿cuál es tu nueva cuenta de Twitter? (sin el @)")
        return

    if intencion == "Saludo":
        posible_usuario = extraer_username(user_message)
        if posible_usuario:
            user_data[user_id] = posible_usuario
            await actualizar_json_y_api(posible_usuario)

            if not serial_lectura_activa:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    executor,
                    lambda: consultar_serial(
                        puerto="COM4",
                        baudrate=115200,
                        timeout=5,
                        nombre_archivo=f"seguidores_{posible_usuario}.json"
                    )
                )
                serial_lectura_activa = True

            respuesta = f"Bonito nombre, @{posible_usuario}. Empezaré a recolectar tus datos. ¿Qué necesitas que haga?"
            await update.message.reply_text(respuesta)
            return
        elif user_id in user_data:
            username = user_data[user_id]
            respuesta = f"¡Hola de nuevo, @{username}! ¿Qué necesitas que haga?"
            await update.message.reply_text(respuesta)
            return
        else:
            await update.message.reply_text(responder_saludo(user_message))
            return

    if intencion == "Despedida":
        respuesta = responder_despedida(user_message)
        await update.message.reply_text(respuesta)
        return

    if user_id not in user_data:
        posible_usuario = user_message.strip().lstrip('@')
        if re.fullmatch(r'\w{1,15}', posible_usuario):
            user_data[user_id] = posible_usuario
            await actualizar_json_y_api(posible_usuario)

            if not serial_lectura_activa:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    executor,
                    lambda: consultar_serial(
                        puerto="COM4",
                        baudrate=115200,
                        timeout=5,
                        nombre_archivo=f"seguidores_{posible_usuario}.json"
                    )
                )
                serial_lectura_activa = True

            await update.message.reply_text(f"¡Gracias, @{posible_usuario}! ¿En qué puedo ayudarte ahora?")
        else:
            await update.message.reply_text("Por favor, dime tu nombre de usuario de Twitter (sin el @)")
        return

    username = user_data[user_id]

    if intencion == "Consultar seguidores":
        respuesta = f"Actualmente, @{username}, tienes 550 seguidores."
    elif intencion == "Cambio seguidores":
        respuesta = f"¡Ganaste 25 seguidores hoy, @{username}!"
    elif intencion == "Ver Dashboard o gráfico":
        try:
            url_ngrok = obtener_link_dashboard()
            respuesta = f"¡Aquí va tu gráfico, @{username}! Entra aquí: {url_ngrok}"
        except Exception as e:
            respuesta = f"No se pudo obtener el enlace del dashboard: {e}"
    else:
        respuesta = "No entendí bien. ¿Podrías reformularlo?"

    await update.message.reply_text(respuesta)

# Inicialización del bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
