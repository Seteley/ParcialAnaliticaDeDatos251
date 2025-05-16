import re
import json
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from clasificador import clasificar_intencion
from responder_qwen import responder_saludo, responder_despedida
from funcionesauxiliar import obtener_link_dashboard
from conectaresp import guardar_datos_en_json, consultar_serial  # Se importan desde conectaresp

BOT_TOKEN = "7884267779:AAEvYsRU8GNbaBIGOIn81ZDitkkX5LTHPLA"
user_data = {}

executor = ThreadPoolExecutor()
serial_lectura_activa = False  # Controla si la lectura serial está activa

def actualizar_nombre_usuario_y_meta_json(nombre_usuario, meta=None):
    ruta_json = "Datos_consulta.json"
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        datos = {}

    datos["nombre_usuario"] = nombre_usuario
    if meta is not None:
        datos["meta"] = meta

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def actualizar_nombre_usuario_api_sync(nombre_usuario):
    url = 'https://parcialanaliticadedatos251-1.onrender.com/nombre_usuario'
    datos = {"nombre_usuario": nombre_usuario}
    try:
        requests.post(url, json=datos)
    except Exception:
        pass  # Mejor loggear en producción

async def actualizar_nombre_usuario_api(nombre_usuario):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, actualizar_nombre_usuario_api_sync, nombre_usuario)

async def actualizar_json_y_api(nombre_usuario, meta=None):
    # Guardar localmente y luego actualizar la API
    actualizar_nombre_usuario_y_meta_json(nombre_usuario, meta)
    await actualizar_nombre_usuario_api(nombre_usuario)

def extraer_username(texto):
    match = re.search(r'@(\w{1,15})', texto)
    if match:
        return match.group(1)
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global serial_lectura_activa

    user_message = update.message.text.strip()
    user_id = update.message.from_user.id
    intencion = clasificar_intencion(user_message)

    # Estado por defecto si no existe
    if user_id not in user_data:
        user_data[user_id] = {
            "nombre_usuario": None,
            "meta": None,
            "estado": "esperando_saludo"  # Estados: esperando_saludo, esperando_usuario, esperando_meta, listo
        }

    estado = user_data[user_id]["estado"]

    # Cambiar de cuenta reinicia todo
    if intencion == "Cambiar de cuenta":
        user_data[user_id] = {
            "nombre_usuario": None,
            "meta": None,
            "estado": "esperando_usuario"
        }
        await update.message.reply_text("Claro, ¿cuál es tu nueva cuenta de Twitter? (sin el @)")
        return

    # Estado: esperando saludo inicial
    if estado == "esperando_saludo":
        if intencion == "Saludo":
            user_data[user_id]["estado"] = "esperando_usuario"
            await update.message.reply_text(
                "¡Hola! Por favor dime tu nombre de usuario de Twitter usando la arroba (@usuario)."
            )
        else:
            await update.message.reply_text("Por favor, salúdame para comenzar.")
        return

    # Estado: esperando usuario Twitter
    if estado == "esperando_usuario":
        posible_usuario = extraer_username(user_message)
        if posible_usuario:
            user_data[user_id]["nombre_usuario"] = posible_usuario
            user_data[user_id]["estado"] = "esperando_meta"
            await actualizar_json_y_api(posible_usuario)  # Solo usuario

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

            await update.message.reply_text(
                f"Bonito nombre, @{posible_usuario}. Empezaré a recolectar tus datos.\n"
                "Ahora, por favor dime cuál es tu meta (número de seguidores que quieres alcanzar)."
            )
        else:
            await update.message.reply_text(
                "El nombre de usuario no es válido o no tiene el formato correcto. "
                "Por favor, envíalo usando la arroba, ejemplo: @usuario"
            )
        return

    # Estado: esperando meta
    if estado == "esperando_meta":
        meta_usuario = user_message
        if not meta_usuario.isdigit():
            await update.message.reply_text("Por favor, ingresa un número válido para tu meta de seguidores.")
            return

        user_data[user_id]["meta"] = meta_usuario
        user_data[user_id]["estado"] = "listo"

        nombre_usuario = user_data[user_id]["nombre_usuario"]
        actualizar_nombre_usuario_y_meta_json(nombre_usuario, meta_usuario)

        await update.message.reply_text(f"¡Perfecto! He guardado tu meta: {meta_usuario} seguidores. ¿En qué más puedo ayudarte?")
        return

    # Estado listo para otras interacciones
    if estado == "listo":
        nombre_usuario = user_data[user_id]["nombre_usuario"]

        if intencion == "Saludo":
            await update.message.reply_text(f"¡Hola de nuevo, @{nombre_usuario}! ¿Qué necesitas que haga?")
            return

        if intencion == "Despedida":
            respuesta = responder_despedida(user_message)
            await update.message.reply_text(respuesta)
            return

        if intencion == "Consultar número de Seguidores":
            ruta_archivo = f"datos_json/seguidores_{nombre_usuario}.json"
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos_seguidores = json.load(f)
                if datos_seguidores:
                    ultimo_registro = datos_seguidores[-1]
                    seguidores = ultimo_registro.get("seguidores", "desconocido")
                    respuesta = f"Actualmente, @{nombre_usuario}, tienes {seguidores} seguidores."
                else:
                    respuesta = f"No hay datos de seguidores disponibles para @{nombre_usuario}."
            except FileNotFoundError:
                respuesta = f"No se encontró el archivo de datos para @{nombre_usuario}."
            except Exception as e:
                respuesta = f"Error al leer los datos de seguidores: {e}"
        elif intencion == "Consultar cambio de Seguidores":
            ruta_archivo = f"datos_json/seguidores_{nombre_usuario}.json"
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos_seguidores = json.load(f)
                if datos_seguidores:
                    # Último registro (más reciente)
                    ultimo_registro = datos_seguidores[-1]
                    seguidores_ultimo = ultimo_registro.get("seguidores", 0)

                    # Primer registro de todo el historial
                    primer_registro = datos_seguidores[0]
                    seguidores_inicio = primer_registro.get("seguidores", 0)

                    # Filtrar registros del día actual (según formato "dd-mm-yyyy hh:mm:ss")
                    from datetime import datetime

                    hoy_str = datetime.now().strftime("%d-%m-%Y")
                    registros_hoy = [reg for reg in datos_seguidores if reg["hora"].startswith(hoy_str)]

                    if registros_hoy:
                        primero_hoy = registros_hoy[0]
                        seguidores_primero_hoy = primero_hoy.get("seguidores", 0)
                        cambio_hoy = seguidores_ultimo - seguidores_primero_hoy
                    else:
                        cambio_hoy = 0  # No hay registros hoy

                    cambio_inicio = seguidores_ultimo - seguidores_inicio

                    respuesta = (
                        f"@{nombre_usuario}, has ganado {cambio_hoy} seguidores hoy "
                        f"y {cambio_inicio} seguidores desde que empezamos a registrar."
                    )
                else:
                    respuesta = f"No hay datos de seguidores disponibles para @{nombre_usuario}."
            except FileNotFoundError:
                respuesta = f"No se encontró el archivo de datos para @{nombre_usuario}."
            except Exception as e:
                respuesta = f"Error al leer los datos de seguidores: {e}"

        elif intencion == "Ver Dashboard o gráfico":
            try:
                url_ngrok = obtener_link_dashboard()
                respuesta = f"¡Aquí va tu gráfico, @{nombre_usuario}! Entra aquí: {url_ngrok}"
            except Exception as e:
                respuesta = f"No se pudo obtener el enlace del dashboard: {e}"
        elif intencion == "Consultar Meta de seguidores":
            ruta_archivo = f"datos_json/seguidores_{nombre_usuario}.json"
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos_seguidores = json.load(f)

                if datos_seguidores:
                    ultimo_registro = datos_seguidores[-1]
                    seguidores_actuales = ultimo_registro.get("seguidores", 0)

                    meta = user_data[user_id].get("meta")
                    if meta is not None:
                        try:
                            faltan = int(meta) - seguidores_actuales
                            if faltan > 0:
                                respuesta = (
                                    f"@{nombre_usuario}, te faltan {faltan:,} seguidores para llegar a tu meta de {int(meta):,}."
                                )
                            else:
                                respuesta = (
                                    f"¡Felicidades @{nombre_usuario}! Ya alcanzaste tu meta de {int(meta):,} seguidores 🎉"
                                )
                        except ValueError:
                            respuesta = "Tu meta no es un número válido."
                    else:
                        respuesta = "No tengo registrada tu meta. Por favor, envíamela para poder ayudarte."
                else:
                    respuesta = f"No hay datos de seguidores disponibles para @{nombre_usuario}."
            except FileNotFoundError:
                respuesta = f"No se encontró el archivo de datos para @{nombre_usuario}."
            except Exception as e:
                respuesta = f"Error al leer los datos de seguidores: {e}"

        else:
            respuesta = "No entendí bien. ¿Podrías reformularlo?"

        await update.message.reply_text(respuesta)

# Inicialización del bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
