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
    await update.message.reply_text("Para hacer lo que me pides necesito tu usuario. ¿Cuál es tu nombre de usuario de Twitter?")
    return NOMBRE_USUARIO

async def obtener_nombre_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre_usuario = update.message.text
    user_data[update.message.from_user.id] = nombre_usuario  # Guardamos el nombre de usuario
    await update.message.reply_text(f"Gracias {nombre_usuario}! ¿En qué puedo ayudarte?")
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    intencion = clasificar_intencion(user_message)

    # Si la intención es "Saludo" o "Despedida", no necesitamos pedir el nombre de usuario
    if intencion in ["Saludo", "Despedida"]:
        if intencion == "Saludo":
            respuesta = responder_saludo(user_message)
        else:
            respuesta = responder_despedida(user_message)
        await update.message.reply_text(respuesta)
        return

    # Si no tenemos el nombre de usuario, lo solicitamos
    if update.message.from_user.id not in user_data:
        return await start(update, context)  # Pedir el nombre de usuario si no está registrado

    # Si ya tenemos el nombre de usuario, continuamos con la clasificación de la intención
    if intencion == "Consultar Seguidores":
        respuesta = f"Actualmente, {user_data[update.message.from_user.id]} tienes 550 seguidores."
    elif intencion == "Cambio Seguidores":
        respuesta = f"¡Ganaste 25 seguidores hoy, {user_data[update.message.from_user.id]}!"
    elif intencion == "Consulta Meta/Gráfico":
        respuesta = "¡Aquí va tu gráfico!"
    elif intencion == "Consulta Pérdida Seguidores":
        respuesta = "Perdiste algunos seguidores, ¡ánimo!"
    elif intencion == "Ver Dashboard":
        respuesta = "Mostrándote el dashboard ahora."
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
