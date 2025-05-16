from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, ConversationHandler
from clasificador import clasificar_intencion
from responder_qwen import responder_saludo, responder_despedida

# Estados de la conversación
NOMBRE_USUARIO = 1

BOT_TOKEN = "7884267779:AAEvYsRU8GNbaBIGOIn81ZDitkkX5LTHPLA"
# Diccionario para almacenar el nombre de usuario por cada usuario
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¿Cuál es tu nombre de usuario de Twitter?")
    return NOMBRE_USUARIO

async def obtener_nombre_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre_usuario = update.message.text.strip()
    user_data[update.message.from_user.id] = nombre_usuario  # Guardamos el nuevo nombre de usuario
    await update.message.reply_text(f"¡Gracias, {nombre_usuario}! ¿En qué puedo ayudarte ahora?")
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    intencion = clasificar_intencion(user_message)

    if intencion in ["Saludo", "Despedida"]:
        if intencion == "Saludo":
            respuesta = responder_saludo(user_message)
        else:
            respuesta = responder_despedida(user_message)
        await update.message.reply_text(respuesta)
        return

    if intencion == "Cambiar de cuenta":
        user_data.pop(user_id, None)  # Eliminar la cuenta registrada anteriormente
        await update.message.reply_text("Claro, indícame la nueva cuenta que quieres consultar.")
        return await start(update, context)

    # Si no tenemos el nombre de usuario, lo solicitamos
    if user_id not in user_data:
        return await start(update, context)

    # Lógica principal del bot con el nombre de usuario ya disponible
    username = user_data[user_id]
    if intencion == "Consultar Seguidores":
        respuesta = f"Actualmente, {username}, tienes 550 seguidores."
    elif intencion == "Cambio Seguidores":
        respuesta = f"¡Ganaste 25 seguidores hoy, {username}!"
    elif intencion == "Ver Dashboard":
        respuesta = f"¡Aquí va tu gráfico, {username}!. Entra aquí: https://bd84-2001-1388-b6f-1617-89a0-e82e-aad9-a6ef.ngrok-free.app/"
    elif intencion == "Consulta Pérdida Seguidores":
        respuesta = f"Perdiste algunos seguidores, {username}. ¡Ánimo!"
    elif intencion == "Ver Dashboard":
        respuesta = f"Mostrándote el dashboard ahora, {username}."
    else:
        respuesta = "No entendí bien. ¿Podrías reformularlo?"

    await update.message.reply_text(respuesta)

# Configuración del ConversationHandler
conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
    states={
        NOMBRE_USUARIO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_nombre_usuario)
        ]
    },
    fallbacks=[],
)

# Crear la aplicación y agregar el handler
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(conv_handler)
app.run_polling()
