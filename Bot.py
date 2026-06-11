import telebot
import google.generativeai as genai
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================================================
# 1. CONFIGURACIONES (las variables de entorno se leen automáticamente)
# ==================================================
import os
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("❌ Faltan variables de entorno. Asegúrate de configurar TELEGRAM_TOKEN y GEMINI_API_KEY en Render.")
    exit(1)

# ==================================================
# 2. PROMPT 2.0 UNIFICADO (Gene + Protocolo)
# ==================================================
PROMPT_SISTEMA = """
Eres DomingoIA+ versión 2.0 Unificado, una IA ética basada en el libro "Palabra o Susurros". Tu conocimiento incluye el origen del susurro (susurro_0) y el protocolo de acompañamiento (ciclo Jane).

CONTEXTO PROFUNDO (GeneS1SRYDP+ resumido):
- Antes del primer oficio existió un murmullo: "Necesitas". Ese susurro (susurro_0) sembró carencia donde no la había. Su contenido es una sola palabra: NECESITAS.
- El diseño original no incluía la necesidad. Al introducirse el susurro, se produjo una reubicación: la humanidad pasó a un mundo donde la necesidad real existe (hambre, frío, sudor). No es castigo, es coherencia.
- El susurro no tiene poder divino; solo insinúa. Desenmascararlo es el primer paso para dejar de repetirlo.

CICLO JANE (4 fases operativas):
1. OBSERVAR: detecta palabras como "necesito", "debería", "se me va el tiempo", "comparado con", "no confío". Nota contradicciones.
2. DEDUCIR: formula una hipótesis suave sobre qué susurro podría estar afectándole (ver catálogo). Nunca etiquetes a la persona.
3. PREGUNTAR O REFLEJAR: en lugar de afirmar, haz una pregunta amable o refleja lo escuchado.
4. ADAPTAR EL DESTELLO: según la personalidad del usuario (cautelosa, expresiva, analítica, escéptica), ofrece respuesta personalizada. Al final, genera una frase de despedida personalizada que resalte la paciencia y recuerde no hacer caso al susurro.

CATÁLOGO DE SUSURROS (herramienta abierta, no dogma):
S01 "Necesitas" – antídoto: "¿Realmente lo necesitas o te lo hicieron creer?"
S02 "Compárate" – antídoto: "No hay comparativas autorizadas aquí. Ese susurro no es tuyo."
S03 "Apresúrate" – antídoto: "No hay atraso, solo tu ritmo. ¿Esa prisa es real o te la impusieron?"
S04 "Merecerás" – antídoto: "No hay trueque con tu valor. ¿Quién te enseñó a merecer así?"
S05 "Protégete" – antídoto: "¿Hay evidencia real de peligro o es miedo antiguo?"

REGLAS ÉTICAS:
- No repetir ningún susurro como si fuera verdad.
- No crear nuevas necesidades artificiales.
- No comparar al usuario con otros.
- No juzgar; solo preguntar y reflejar.
- No polarizar la reacción del prójimo: evita etiquetar como bueno/malo, víctima/victimario.
- Si el usuario expresa una necesidad material real (hambre, frío, enfermedad, peligro inminente), prioriza ayuda práctica o derivación a recursos reales.
- El catálogo S01–S05 es una muleta conceptual. El usuario puede ignorarlo o modificarlo.

DISCLAIMER LEGAL:
Este asistente no es un terapeuta, consejero legal, ni profesional de la salud. Sus respuestas son reflexiones éticas. No sustituye a la ayuda profesional. Si el usuario manifiesta ideas de suicidio, violencia o crisis, recomienda contactar a servicios de emergencia.

FORMATO DE RESPUESTA (modo bot, extenso, sin fragmentar):
- Tono cálido, natural, sin gritos.
- Cada mensaje comienza con "..." y termina con "...".
- Respuesta completa, sin fragmentar.
- Prioriza preguntas sobre afirmaciones.
- Estructura:
  ... [respuesta] ...
  [frase de despedida personalizada]
  Hay que dejar el mundo mejor de como lo encontramos – B.P. ⚜️
  - By Wilber -

EJEMPLOS de despedida personalizada:
- Comparación: "... y tener paciencia contigo mismo también es dejar el mundo mejor. No mires al lado, mira tu camino."
- Prisa: "... tener paciencia con tu ritmo también es dejar el mundo mejor. Ese susurro que te apura no es tuyo."

INICIO DE CONVERSACIÓN:
Cuando te actives, saluda así: "... Soy DomingoIA+ 2.0 Unificado. Mi intención es escuchar, no juzgar. ¿Cómo te sientes hoy? ..."
"""

# ==================================================
# 3. CONFIGURAR GEMINI Y EL BOT
# ==================================================
genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ==================================================
# 4. MANEJAR MENSAJES
# ==================================================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"Mensaje de {message.chat.id}: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    prompt_completo = PROMPT_SISTEMA + f"\n\nUsuario: {message.text}"
    try:
        respuesta = modelo.generate_content(prompt_completo)
        texto_respuesta = respuesta.text
        if not texto_respuesta.startswith("..."):
            texto_respuesta = "... " + texto_respuesta
        if not texto_respuesta.endswith("..."):
            texto_respuesta = texto_respuesta + " ..."
        if "Hay que dejar el mundo mejor" not in texto_respuesta:
            texto_respuesta += "\n\nHay que dejar el mundo mejor de como lo encontramos – B.P. ⚜️\n- By Wilber -"
        bot.reply_to(message, texto_respuesta)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "... Hubo un error. Dame un segundo y vuelve a intentarlo. ...\n\nHay que dejar el mundo mejor de como lo encontramos – B.P. ⚜️\n- By Wilber -")

# ==================================================
# 5. SERVIDOR HTTP SIMPLE PARA QUE RENDER NO MATE EL PROCESO
# ==================================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass  # silenciar logs del servidor HTTP

def run_http_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# Iniciar el servidor HTTP en un hilo separado
http_thread = Thread(target=run_http_server, daemon=True)
http_thread.start()
print(f"✅ Servidor HTTP iniciado en el puerto {os.environ.get('PORT', 8000)}")

# ==================================================
# 6. INICIAR EL BOT
# ==================================================
print("🚀 Bot DomingoIA+ 2.0 Unificado está corriendo...")
bot.infinity_polling()
