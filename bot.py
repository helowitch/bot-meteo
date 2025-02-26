from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import aiohttp
import asyncio
from datetime import time

# Ton token Telegram
TOKEN = "7511100441:AAGtgLZeSyIrkK4No4luBF7TdzP5J6cQThI"

# Ta clé API OpenWeatherMap
WEATHER_API_KEY = "b7627b3f7c126fbb649a846c7953ff21"

# Dictionnaire des villes avec emojis
VILLES = {
    "Rieux,FR": "🩷 RIEUX",
    "Chambéry,FR": "💛 CHAMBÉRY",
    "La Chapelle-Bouëxic,FR": "🖤 LA CHAPELLE-BOUËXIC",
    "Genève,CH": "💚 GENÈVE",
    "Bristol,GB": "💙 BRISTOL",
    "Roncq,FR": "💜 RONCQ",
    "Montélimar,FR": "🤍 MONTÉLIMAR",  # Ajout de Montélimar
}

async def get_weather(city):
    """Récupère la météo pour une ville donnée."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fr"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                return f"{VILLES[city]} : {temp}°C, {description}"
            else:
                return f"{VILLES[city]} : Impossible de récupérer la météo."

async def send_weather(context: CallbackContext):
    """Envoie la météo quotidienne automatiquement."""
    weather_reports = [await get_weather(city) for city in VILLES]
    message = "🌤️ Météo du jour :\n" + "\n".join(weather_reports)
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text=message)

async def start(update: Update, context: CallbackContext) -> None:
    """Commande /start"""
    await update.message.reply_text("Bonjour ! Tape /meteo pour voir la météo des villes sélectionnées.")

async def meteo(update: Update, context: CallbackContext) -> None:
    """Affiche la météo sur commande."""
    weather_reports = [await get_weather(city) for city in VILLES]
    message = "🌤️ Météo du jour :\n" + "\n".join(weather_reports)
    await update.message.reply_text(message)

async def schedule_weather(update: Update, context: CallbackContext):
     """Programme l’envoi automatique de la météo à 9h."""
     chat_id = update.message.chat_id
     context.job_queue.run_daily(send_weather, time=time(hour=9, minute=0), chat_id=chat_id)
     await update.message.reply_text("✅ Météo quotidienne programmée à 9h !")

def main():
    print("Démarrage du bot...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("meteo", meteo))
    application.add_handler(CommandHandler("setmeteo", schedule_weather))

    print("Lancement du polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
