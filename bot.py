from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import aiohttp
import asyncio
from datetime import time

# Ton token Telegram
TOKEN = "7511100441:AAGtgLZeSyIrkK4No4luBF7TdzP5J6cQThI"

# Clé API MeteoConcept
METEO_CONCEPT_API_KEY = "cc0ee5d2b8f4459421ea9076c6e514cd8368587588ce3a38f7de9ca6a998b6f6"

# Dictionnaire des villes avec codes INSEE (FR) ou coordonnées (autres)
VILLES = {
    "56194": "🩷 RIEUX",          # INSEE pour Rieux, FR
    "73065": "💛 CHAMBÉRY",       # INSEE pour Chambéry, FR
    "35057": "🖤 LA CHAPELLE-BOUËXIC", 
    "46.204,6.143": "💚 GENÈVE",          # Coordonnées pour Genève
    "51.454,-2.587": "💙 BRISTOL",  # Coordonnées pour Bristol
    "59508": "💜 RONCQ",          # INSEE pour Roncq, FR
    "26198": "🤍 MONTÉLIMAR"      # INSEE pour Montélimar, FR
}

async def fetch_meteo_data(params):
    """Fonction générique pour interroger l'API MeteoConcept"""
    base_url = "https://api.meteo-concept.com/api/"
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return None

async def get_weather(city_key):
    """Récupère la météo actuelle"""
    params = {
        'token': METEO_CONCEPT_API_KEY,
        'insee': city_key if city_key.isdigit() else None,
        'lat': city_key.split(',')[0] if ',' in city_key else None,
        'lon': city_key.split(',')[1] if ',' in city_key else None
    }
    data = await fetch_meteo_data({**params, **{'hourly': 'false'}})
    
    if data and 'forecast' in data:
        temp = data['forecast'][0]['temp']
        desc = data['forecast'][0]['weather']['desc']
        return f"{VILLES[city_key]} : {temp}°C, {desc.capitalize()}"
    return f"{VILLES[city_key]} : Données indisponibles"

async def get_daily_forecast(city_key):
    """Récupère les prévisions quotidiennes"""
    params = {
        'token': METEO_CONCEPT_API_KEY,
        'insee': city_key if city_key.isdigit() else None,
        'lat': city_key.split(',')[0] if ',' in city_key else None,
        'lon': city_key.split(',')[1] if ',' in city_key else None,
        'daily': 'true'
    }
    data = await fetch_meteo_data(params)
    
    if data and 'forecast' in data:
        temp = data['forecast'][0]['tmax']
        desc = data['forecast'][0]['weather']['desc']
        return f"{VILLES[city_key]} : {temp}°C max, {desc.capitalize()}"
    return f"{VILLES[city_key]} : Prévisions indisponibles"

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