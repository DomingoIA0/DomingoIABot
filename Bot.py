import telebot
import requests
import json
import os
import sys

# Leer variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# --- Verificación de que la API key se leyó bien ---
if DEEPSEEK_API_KEY:
    print(f"✅ DEEPSEEK_API_KEY encontrada. Primeros 8 caracteres: {DEEPSEEK_API_KEY[:8]}...")
else:
    print("❌ ERROR: No se encontró DEEPSEEK_API_KEY en las variables de entorno.")

# Verificar que existan ambas
if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
    print("❌ Faltan TELEGRAM_TOKEN o DEEPSEEK_API_KEY en Render")
    sys.exit(1)

print("✅ Variables de entorno cargadas correctamente")

# Configurar bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"Mensaje: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Llamar a DeepSeek
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": message.text}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        respuesta = result["choices"][0]["message"]["content"]
        bot.reply_to(message, respuesta)
    except Exception as e:
        print(f"❌ Error: {e}")
        bot.reply_to(message, "Hubo un error. Intenta de nuevo.")

print("🚀 Bot con DeepSeek corriendo...")
bot.infinity_polling()
