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
    "Montélimar,FR": "🤍 MONTÉLIMAR",
}

async def get_weather(city):
    """Récupère la météo actuelle pour une ville donnée."""
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

async def get_daily_forecast(city):
    """Récupère les prévisions générales pour la journée."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fr&cnt=8"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                # On prend la première prévision de la journée
                forecast = data["list"][0]
                temp = forecast["main"]["temp"]
                description = forecast["weather"][0]["description"]
                return f"{VILLES[city]} : {temp}°C, {description}"
            else:
                return f"{VILLES[city]} : Impossible de récupérer les prévisions."

async def send_daily_forecast(context: CallbackContext):
    """Envoie les prévisions quotidiennes automatiquement."""
    weather_reports = [await get_daily_forecast(city) for city in VILLES]
    message = "🌤️ Prévisions du jour :\n" + "\n".join(weather_reports) + "\n\nBonne journée !"
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text=message)

async def start(update: Update, context: CallbackContext) -> None:
    """Commande /start"""
    await update.message.reply_text("Bonjour ! Tape /meteo pour voir la météo actuelle des villes sélectionnées.")

async def meteo(update: Update, context: CallbackContext) -> None:
    """Affiche la météo en direct sur commande."""
    weather_reports = [await get_weather(city) for city in VILLES]
    message = "🔥 Météo en direct :\n" + "\n".join(weather_reports)
    await update.message.reply_text(message)

async def schedule_weather(update: Update, context: CallbackContext):
    """Programme l’envoi automatique des prévisions à 9h."""
    chat_id = update.message.chat_id
    context.job_queue.run_daily(send_daily_forecast, time=time(hour=8, minute=0), chat_id=chat_id)
    await update.message.reply_text("✅ Prévisions quotidiennes programmées à 9h !")

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
