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
    "46.204,6.143": "💚 GENÈVE",  # Coordonnées pour Genève
    "51.454,-2.587": "💙 BRISTOL",  # Coordonnées pour Bristol
    "59508": "💜 RONCQ",          # INSEE pour Roncq, FR
    "26198": "🤍 MONTÉLIMAR"      # INSEE pour Montélimar, FR
}

# Dictionnaire pour mapper les codes météo aux descriptions
WEATHER_CODES = {
    0: "Soleil",
    1: "Peu nuageux",
    2: "Ciel voilé",
    3: "Nuageux",
    4: "Très nuageux",
    5: "Couvert",
    6: "Brouillard",
    7: "Brouillard givrant",
    10: "Pluie faible",
    11: "Pluie modérée",
    12: "Pluie forte",
    13: "Pluie faible verglaçante",
    14: "Pluie modérée verglaçante",
    15: "Pluie forte verglaçante",
    20: "Neige faible",
    21: "Neige modérée",
    22: "Neige forte",
    30: "Pluie et neige mêlées faibles",
    31: "Pluie et neige mêlées modérées",
    32: "Pluie et neige mêlées fortes",
    40: "Averses de pluie locales et faibles",
    41: "Averses de pluie locales",
    42: "Averses locales et fortes",
    60: "Averses de neige locales et faibles",
    61: "Averses de neige locales",
    62: "Averses de neige locales et fortes",
    70: "Averses de pluie et neige mêlées locales et faibles",
    71: "Averses de pluie et neige mêlées locales",
    72: "Averses de pluie et neige mêlées locales et fortes",
    100: "Orages faibles",
    101: "Orages",
    102: "Orages forts",
    120: "Orages faibles et localisés",
    121: "Orages localisés",
    122: "Orages forts et localisés"
}

async def fetch_meteo_data(params):
    """Fonction générique pour interroger l'API MeteoConcept"""
    # Filtrer les paramètres None
    filtered_params = {k: v for k, v in params.items() if v is not None}
    base_url = "https://api.meteo-concept.com/api/forecast/daily"
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=filtered_params) as response:
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

    # Vérifiez que les paramètres nécessaires sont définis
    if not any(params.values()):
        return f"{VILLES[city_key]} : Paramètres de requête invalides"

    data = await fetch_meteo_data(params)

    if data and 'forecast' in data and len(data['forecast']) > 0:
        forecast = data['forecast'][0]
        temp = forecast.get('tmax')  # Utilisez get pour éviter KeyError
        weather_code = forecast.get('weather')
        desc = WEATHER_CODES.get(weather_code, "Description indisponible")
        return f"{VILLES[city_key]} : {temp}°C, {desc}"
    return f"{VILLES[city_key]} : Données indisponibles"

async def get_daily_forecast(city_key):
    """Récupère les prévisions quotidiennes"""
    params = {
        'token': METEO_CONCEPT_API_KEY,
        'insee': city_key if city_key.isdigit() else None,
        'lat': city_key.split(',')[0] if ',' in city_key else None,
        'lon': city_key.split(',')[1] if ',' in city_key else None
    }

    # Vérifiez que les paramètres nécessaires sont définis
    if not any(params.values()):
        return f"{VILLES[city_key]} : Paramètres de requête invalides"

    data = await fetch_meteo_data(params)

    if data and 'forecast' in data:
        forecast = data['forecast'][0]
        temp = forecast.get('tmax')  # Température maximale
        weather_code = forecast.get('weather')
        desc = WEATHER_CODES.get(weather_code, "Description indisponible")
        return f"{VILLES[city_key]} : {temp}°C max, {desc}"
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
    context.job_queue.run_daily(send_daily_forecast, time=time(hour=9, minute=0), chat_id=chat_id)
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
