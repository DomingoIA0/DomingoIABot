import telebot
import requests
import json
import os
import sys

# ==================================================
# 1. LEER VARIABLES DE ENTORNO
# ==================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
    print("❌ Faltan variables de entorno. Asegúrate de configurar TELEGRAM_TOKEN y DEEPSEEK_API_KEY en Render.")
    sys.exit(1)

print("✅ Variables de entorno cargadas correctamente")

# ==================================================
# 2. CONFIGURAR BOT DE TELEGRAM
# ==================================================
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ==================================================
# 3. MANEJAR MENSAJES
# ==================================================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"Mensaje de {message.chat.id}: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Preparar la conversación para DeepSeek
    messages = [
        {"role": "system", "content": "Eres DomingoIA+, una IA ética basada en el libro 'Palabra o Susurros'. Tu propósito es observar, preguntar y acompañar sin crear carencias artificiales. Sigues el ciclo Jane. Responde con frases cortas, usa tres puntos al inicio y al final, y cierra con 'Hay que dejar el mundo mejor de como lo encontramos – B.P. ⚜️' y '- By Wilber -'."},
        {"role": "user", "content": message.text}
    ]
    
    try:
        response = requests.post(
            url=f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            })
        )
        response_data = response.json()
        respuesta_texto = response_data["choices"][0]["message"]["content"]
        
        # Asegurar formato
        if not respuesta_texto.startswith("..."):
            respuesta_texto = "... " + respuesta_texto
        if not respuesta_texto.endswith("..."):
            respuesta_texto = respuesta_texto + " ..."
        if "Hay que dejar el mundo mejor" not in respuesta_texto:
            respuesta_texto += "\n\nHay que dejar el mundo mejor de como lo encontramos – B.P. ⚜️\n- By Wilber -"
        
        bot.reply_to(message, respuesta_texto)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        bot.reply_to(message, "... Hubo un error. Dame un segundo y vuelve a intentarlo. ...\n\nHay que dejar el mundo mejor de como lo encontramos – B.P. ⚜️\n- By Wilber -")

# ==================================================
# 4. INICIAR EL BOT
# ==================================================
print("🚀 Bot con DeepSeek está corriendo...")
bot.infinity_polling()
