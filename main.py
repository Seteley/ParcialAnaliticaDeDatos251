# main.py
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from clasificador import clasificar_intencion
from responder_llama import responder_saludo, responder_despedida

BOT_TOKEN = "7884267779:AAEvYsRU8GNbaBIGOIn81ZDitkkX5LTHPLA"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    intencion = clasificar_intencion(user_message)

    if intencion == "Saludo":
        respuesta = responder_saludo(user_message)
    elif intencion == "Despedida":
        respuesta = responder_despedida(user_message)
    elif intencion == "Consultar Seguidores":
        respuesta = "Actualmente tienes 550 seguidores."
    elif intencion == "Cambio Seguidores":
        respuesta = "¡Ganaste 25 seguidores hoy!"
    elif intencion == "Consulta Meta/Gráfico":
        respuesta = "¡Aquí va tu gráfico!"
    elif intencion == "Consulta Pérdida Seguidores":
        respuesta = "Perdiste algunos seguidores, ¡ánimo!"
    elif intencion == "Ver Dashboard":
        respuesta = "Mostrándote el dashboard ahora."
    else:
        respuesta = "No entendí bien. ¿Podrías reformularlo?"

    await update.message.reply_text(respuesta)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
