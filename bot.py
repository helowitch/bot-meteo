from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import aiohttp
import requests
import asyncio
from datetime import datetime, timedelta

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
}

# Fonction pour récupérer la météo en temps réel
def get_weather(city):
    # Remplace par les coordonnées correspondantes pour chaque ville
    city_coords = {
        "Rieux": {"lat": 47.826, "lon": -2.002},
        "Chambéry": {"lat": 45.564, "lon": 5.911},
        "La Chapelle-Bouëxic": {"lat": 47.827, "lon": -1.707},
        "Genève": {"lat": 46.2044, "lon": 6.1432},
        "Bristol": {"lat": 51.4545, "lon": -2.5879},
        "Roncq": {"lat": 50.6472, "lon": 3.1111}
    }

    lat, lon = city_coords[city]["lat"], city_coords[city]["lon"]
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=fr"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather}, {temp}°C"
    else:
        return "Données météo non disponibles."

# Fonction pour afficher la météo en temps réel
async def send_weather(update: Update, context: CallbackContext):
    message = "🌤️ Météo du jour :\n"
    for city, emoji in VILLES.items():
        weather = get_weather(city)
        message += f"{emoji} {city.upper()} : {weather}\n"
    await update.message.reply_text(message)

# Fonction pour envoyer la météo à 9h avec la météo la plus présente de la journée
async def send_daily_weather(application: Application):
    message = "🌤️ Météo du jour :\n"
    for city, emoji in VILLES.items():
        weather = get_weather(city)
        message += f"{emoji} {city.upper()} : {weather}\n"
    
    message += "\nBonne journée !"

    # Envoi du message à 9h à tous les utilisateurs
    # Adapter pour envoyer le message à un groupe ou à des utilisateurs spécifiques
    await application.bot.send_message(chat_id='-1001267100130', text=message)

# Fonction pour planifier l'envoi de la météo tous les matins à 9h
async def schedule_daily_weather(application: Application):
    now = datetime.now()
    first_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now > first_run:
        first_run += timedelta(days=1)  # Si on est déjà passé 9h, on planifie pour demain
    delay = (first_run - now).total_seconds()
    await asyncio.sleep(delay)
    await send_daily_weather(application)
    # Répéter tous les jours à 9h
    while True:
        await asyncio.sleep(86400)  # 24 heures
        await send_daily_weather(application)

# Fonction principale
async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Ajouter les gestionnaires
    application.add_handler(CommandHandler("meteo", send_weather))

    # Planifier l'envoi automatique à 9h
    application.job_queue.run_once(schedule_daily_weather, 0)

    # Lancer l'application
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
