import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
import logging
from datetime import datetime, timedelta
import random
from flask import Flask, request

# Configuración básica
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de la aplicación Flask para Render
app = Flask(__name__)

@app.route('/')
def home():
    return "¡Sweet Spot Bot está activo! 🍰"

# Estados de la conversación
WAITING_RESPONSE = 1

# Configuración anti-spam
MAX_REPEATED_MESSAGES = 3
MESSAGE_TIME_WINDOW = 10
COOLDOWN_TIME = 30

# Datos de tu emprendimiento con respuestas más conversacionales
RESPUESTAS = {
    "saludo": [
        "¡Hola {nombre}! ¿Cómo estás? 😊\n\n✨ *Bienvenido/a a mi pequeño emprendimiento Sweet Spot!* ✨\n\nTú apoyo lo hace grande 💕\n\n¿En qué podemos ayudarte hoy? 🍰Puedes preguntarme sobre:\n"
        "- Productos disponibles\n- Precios\n- Envíos\n- Contacto\n- Ubicación\n- Tortas completas\n"
        "- O cualquier otra inquietud que tengas\n\n"
        "¡Estoy aquí para ayudarte! 💌"
    ],
    "hola": [
        "😊 ¡Hola! ¿Con qué información puedo ayudarte sobre Sweet Spot el dia de hoy? 🍪",
    ],
    "bien": [
        "Bien gracias 😊, ¿Con qué información puedo ayudarte sobre nosotros Sweet Spot? 🎂",
        "Estoy muy bien, gracias por preguntar 😊 ¿En qué puedo ayudarte hoy? 💖"
    ],
    "precios": [
        "💰 Nuestros precios y productos:\n\n🍰 Tortas por porción:\n- Chocolate: 3$ 🍫\n- Tres leches: 3$ 🥛\n- Vainilla con arequipe: 2.5$ �\n- Choco quesillo: 3.5$ 🍮\n\n🍪 Galletas polvorosas:\n- 1.5$ al detal\n- 1$ al mayor (a partir de 6 unidades)\n\n¡😊 En qué otra cosa puedo ayudarte!",
        "Aquí tienes nuestros precios actualizados productos:\n\n🎂 Tortas por porción:\n• Chocolate: 3$ 🍫\n• Tres leches: 3$ 🥛\n• Vainilla con arequipe: 2.5$ 🧁\n• Choco quesillo: 3.5$ 🍮\n\n🍪 Galletas:\n• 1.5$ unidad\n• 1$ c/u al mayor (6+ unidades)\n\n¿Necesitas información sobre algo más? 😊"
    ],
    "envios": [
        "🚚 Envíos a toda Cabimas:\n\n• Costo: Dependiendo de la zona 🗺️\n• Envio gratis por compras mayores a 10$ 💸\n\n¡😊 En qué otra cosa puedo ayudarte!",
        "📦 Nuestro servicio de envíos:\n\n• Cubrimos toda Cabimas 🏙️\n• Costo varía según la zona 🗺️\n• ¡Envío gratis para pedidos mayores a 10$! 💰\n\n¿Quieres saber algo más? 😊"
    ],
    "contacto": [
        "📞 CEO: Rossana Hernandez\n\n Contáctanos:\n\nWhatsApp: 0412-1422179 📱\nInstagram: @Sweetspot_29 📸\n\n😊 ¿Necesitas ayuda en algo más?",
        "📲 CEO: Rossana Hernandez\n\n Puedes comunicarte con nosotros por:\n\n• WhatsApp: 0412-1422179\n• Instagram: @Sweetspot_29\n\nEstamos aquí para atenderte. ¿Algo más en lo que pueda ayudar? 💖"
    ],
    "pagos": [
        "💳 Aceptamos:\n\n• Efectivo 💵\n• Transferencia 🏦\n• Pago móvil 📱\n\n😊 ¿Tienes alguna otra inquietud?",
        "💰 Métodos de pago disponibles:\n\n• Efectivo 💵\n• Transferencia bancaria 🏦\n• Pago móvel 📲\n\n¿Necesitas información adicional? 😊"
    ],
    "ubicacion": [
    "Aun no contamos con tienda fisica somos tinda online contactanos😊 ¿Tienes alguna otra inquietud?",
],
    "tortas_completas": [
        "🎂 Tortas completas:\n\n• 1KG:\n- Chocolate: 33$ 🍫\n- Tres leches: 33$ 🥛\n- Vainilla con arequipe: 27$ �\n- Choco quesillo: 39$ 🍮\n\n• 1/2KG:\n- Chocolate: 16$ 🍫\n- Tres leches: 16$ 🥛\n- Vainilla con arequipe: 15$ 🧁\n- Choco quesillo: 20$ 🍮\n\n• 1/4KG:\n- Chocolate: 9$ 🍫\n- Tres leches: 9$ 🥛\n- Vainilla con arequipe: 8$ 🧁\n- Choco quesillo: 11$ 🍮\n\n¡😊 Para realizar pedidos contáctanos! 📞",
        "🍰 Precios de tortas completas:\n\n• 1KG:\n- Chocolate: 33$ 🍫\n- Tres leches: 33$ 🥛\n- Vainilla con arequipe: 27$ 🧁\n- Choco quesillo: 39$ 🍮\n\n• 1/2KG:\n- Chocolate: 16$ 🍫\n- Tres leches: 16$ 🥛\n- Vainilla con arequipe: 15$ 🧁\n- Choco quesillo: 20$ 🍮\n\n• 1/4KG:\n- Chocolate: 9$ �\n- Tres leches: 9$ 🥛\n- Vainilla con arequipe: 8$ 🧁\n- Choco quesillo: 11$ 🍮\n\n¿Quieres hacer un pedido o necesitas otra información? 😊"
    ],
    "devoluciones": [
        "🔄 No se aceptan devoluciones ❌",
        "⚠️ Lamentablemente no manejamos políticas de devolución. ¿Puedo ayudarte con algo más? 😊"
    ],
    "despedida": [
        "¡Gracias por contactar a Sweet Spot! Vuelve pronto 😊 🍰",
        "¡Fue un placer ayudarte! Que tengas un dulce día 🎂 💝",
        "¡Hasta luego! Esperamos verte de nuevo en Sweet Spot 💕 🍪"
    ],
    "no_entendido": [
        "🤔 No entendí tu pregunta. ¿Podrías reformularla?",
        "😅 Disculpa, no estoy seguro de entender. ¿Puedes decirlo de otra manera?",
        "❓ ¿Te refieres a información sobre productos, precios, envíos o algo más?"
    ],
    "spam": [
        "⏳ Parece que estás enviando muchos mensajes seguidos. Voy a hacer una pausa por un momento.",
        "🤖 Voy a tomarme un breve descanso. Por favor envía tu consulta de nuevo más tarde.",
        "🚫 Para evitar spam, necesito esperar un momento antes de responder más mensajes."
    ],
    "repetido": [
        "🔁 Ya respondí a eso anteriormente. ¿Hay algo más en lo que pueda ayudarte? 😊",
        "🔄 Creo que ya hablamos sobre esto. ¿Quieres información sobre otro tema? 🍰",
        "❓ ¿Te gustaría que repita la información o prefieres preguntar sobre otra cosa? 💖"
    ]
}

# Diccionario para mantener el contexto de la conversación
conversaciones = {}
# Diccionario para control de spam
user_spam_control = {}


def determinar_tema(texto):
    texto = texto.lower()
    
    if any(palabra in texto for palabra in ['hola', 'hi', 'buenos días', 'buenas tardes', 'buenas noches']):
        return 'hola'
    elif any(palabra in texto for palabra in ['y tu']):
        return 'bien'
    elif any(palabra in texto for palabra in ['precio', 'costó', 'valor', 'cuánto sale', 'precios', 'cuanto vale''producto', 'productos', 'servicio', 'qué venden', 'qué ofrecen']):
        return 'precios'
    elif any(palabra in texto for palabra in ['envío', 'envios', 'entrega', 'cuándo llega', 'domicilio']):
        return 'envios'
    elif any(palabra in texto for palabra in ['contacto', 'hablar', 'whatsapp', 'teléfono', 'instagram', 'redes']):
        return 'contacto'
    elif any(palabra in texto for palabra in ['pago', 'pagos', 'tarjeta', 'pago movil', 'transferencia']):
        return 'pagos'
    elif any(palabra in texto for palabra in ['torta', 'completa', 'completas', 'al mayor', 'entera']):
        return 'tortas_completas'
    elif any(palabra in texto for palabra in ['ubicacion', 'donde se encuentran', 'donde estan ubicados', 'como encontralos','ubicación', 'son tienda fisica', 'dirección','direccion']):
        return 'ubicacion'
    elif any(palabra in texto for palabra in ['devolución', 'cambio']):
        return 'devoluciones'
    elif any(palabra in texto for palabra in [' gracias por la ayuda', 'thanks', 'adiós', 'chao', 'hasta luego']):
        return 'despedida'
    else:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    respuesta = random.choice(RESPUESTAS["saludo"]).format(nombre=user.first_name)
    await update.message.reply_text(respuesta, parse_mode='Markdown')
    
    # Iniciar contexto de conversación
    conversaciones[user.id] = {
        'ultimo_tema': None,
        'hora_inicio': datetime.now(),
        'pasos': 0,
        'ultimo_mensaje': None,
        'repeticiones': 0
    }
    
    # Iniciar control de spam
    user_spam_control[user.id] = {
        'last_message_time': datetime.now(),
        'message_count': 0,
        'in_cooldown': False,
        'cooldown_until': None
    }
    
    return WAITING_RESPONSE

async def manejar_conversacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    texto = update.message.text
    user_id = user.id
    now = datetime.now()

    # Verificar si el usuario está en cooldown por spam
    if user_id in user_spam_control and user_spam_control[user_id]['in_cooldown']:
        if user_spam_control[user_id]['cooldown_until'] > now:
            # Todavía en cooldown, no responder
            return WAITING_RESPONSE
        else:
            # Cooldown terminado
            user_spam_control[user_id]['in_cooldown'] = False
            user_spam_control[user_id]['message_count'] = 0

    # Control de spam: mensajes muy frecuentes
    if user_id in user_spam_control:
        time_since_last = (now - user_spam_control[user_id]['last_message_time']).total_seconds()
        
        if time_since_last < 1:  # Mensajes demasiado rápidos
            user_spam_control[user_id]['message_count'] += 1
            if user_spam_control[user_id]['message_count'] > 5:
                user_spam_control[user_id]['in_cooldown'] = True
                user_spam_control[user_id]['cooldown_until'] = now + timedelta(seconds=COOLDOWN_TIME)
                await update.message.reply_text(random.choice(RESPUESTAS["spam"]))
                return WAITING_RESPONSE
        else:
            user_spam_control[user_id]['message_count'] = max(0, user_spam_control[user_id]['message_count'] - 1)
        
        user_spam_control[user_id]['last_message_time'] = now

    if user_id not in conversaciones:
        return await start(update, context)
    
    # Control de mensajes repetidos
    if texto == conversaciones[user_id].get('ultimo_mensaje'):
        conversaciones[user_id]['repeticiones'] += 1
        if conversaciones[user_id]['repeticiones'] >= MAX_REPEATED_MESSAGES:
            await update.message.reply_text(random.choice(RESPUESTAS["repetido"]))
            return WAITING_RESPONSE
    else:
        conversaciones[user_id]['ultimo_mensaje'] = texto
        conversaciones[user_id]['repeticiones'] = 0
    
    tema = determinar_tema(texto)
    conversaciones[user_id]['pasos'] += 1
    
    # Manejar despedidas
    if tema == 'despedida':
        respuesta = random.choice(RESPUESTAS["despedida"])
        del conversaciones[user_id]
        if user_id in user_spam_control:
            del user_spam_control[user_id]
        await update.message.reply_text(respuesta)
        return ConversationHandler.END
    
    # Determinar respuesta apropiada
    if tema:
        respuesta = random.choice(RESPUESTAS.get(tema, RESPUESTAS["no_entendido"]))
        conversaciones[user_id]['ultimo_tema'] = tema
    else:
        if conversaciones[user_id]['ultimo_tema']:
            respuesta = f"{random.choice(RESPUESTAS['no_entendido'])}\n\n¿Quieres más información sobre {conversaciones[user_id]['ultimo_tema']} contactanos?"
        else:
            respuesta = random.choice(RESPUESTAS["no_entendido"])
    
    # Hacer la conversación más natural
    if conversaciones[user_id]['pasos'] > 3 and "?" not in respuesta:
        respuesta += "\n\n¿Hay algo más en lo que pueda ayudarte?"
    
    await update.message.reply_text(respuesta)
    return WAITING_RESPONSE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in conversaciones:
        del conversaciones[user.id]
    if user.id in user_spam_control:
        del user_spam_control[user.id]
    await update.message.reply_text("¡Hasta luego! 😊 Fue un placer ayudarte.")
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=True)
    if update.message:
        await update.message.reply_text("Ocurrió un error inesperado. Por favor intenta nuevamente más tarde.")

def main():
    # Configuración para Render
    TOKEN = os.getenv('TELEGRAM_TOKEN', '7841638412:AAGso5OXD-tsQhRJxNPXH1LTHH66XzQ_S0g')
    PORT = int(os.getenv('PORT', 5000))
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_conversacion)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Modo webhook para Render
    if WEBHOOK_URL:
        logger.info("Iniciando en modo webhook...")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            secret_token='SECRETO_UNICO'
        )
    else:
        # Modo polling para desarrollo local
        logger.info("Iniciando en modo polling...")
        application.run_polling()

if __name__ == '__main__':
    main()
