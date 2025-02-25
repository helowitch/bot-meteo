import asyncio
import aiohttp
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ApplicationBuilder, JobQueue

# Ton token Telegram
TOKEN = "7511100441:AAGtgLZeSyIrkK4No4luBF7TdzP5J6cQThI"
# Ta clé API OpenWeatherMap
WEATHER_API_KEY = "b7627b3f7c126fbb649a846c7953ff21"
# ID du groupe Telegram
CHAT_ID = "-1001267100130"

# Dictionnaire des villes avec emojis
VILLES = {
    "Rieux": "🩷 RIEUX",
    "Chambéry": "💛 CHAMBÉRY",
    "La Chapelle-Bouëxic": "🖤 LA CHAPELLE-BOUËXIC",
    "Genève": "💚 GENÈVE",
    "Bristol": "💙 BRISTOL",
    "Roncq": "💜 RONCQ",
}

# Coordonnées des villes (nécessaire pour OpenWeatherMap)
CITY_COORDS = {
    "Rieux": {"lat": 47.826, "lon": -2.002},
    "Chambéry": {"lat": 45.564, "lon": 5.911},
    "La Chapelle-Bouëxic": {"lat": 47.827, "lon": -1.707},
    "Genève": {"lat": 46.2044, "lon": 6.1432},
    "Bristol": {"lat": 51.4545, "lon": -2.5879},
    "Roncq": {"lat": 50.6472, "lon": 3.1111}
}

async def get_weather(city):
    """Récupère la météo d'une ville via OpenWeatherMap."""
    if city not in CITY_COORDS:
        return "❌ Ville non trouvée"
    
    lat, lon = CITY_COORDS[city]["lat"], CITY_COORDS[city]["lon"]
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=fr"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "❌ Météo indisponible"

            data = await response.json()
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"{weather}, {temp}°C"

async def send_weather(update: Update, context: CallbackContext):
    """Répond à la commande /meteo en affichant la météo en temps réel."""
    message = "🌤️ *Météo du jour :*\n"
    
    for city, emoji in VILLES.items():
        meteo = await get_weather(city)
        message += f"{emoji} *{city.upper()}* : {meteo}\n"

    await update.message.reply_text(message, parse_mode="Markdown")

async def send_daily_weather(context: CallbackContext):
    """Envoie automatiquement la météo tous les matins à 9h."""
    message = "🌤️ *Météo du jour :*\n"

    for city, emoji in VILLES.items():
        meteo = await get_weather(city)
        message += f"{emoji} *{city.upper()}* : {meteo}\n"
    
    message += "\nBonne journée !"

    await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

async def start(update: Update, context: CallbackContext):
    """Répond à la commande /start."""
    await update.message.reply_text("Salut ! 🌤️ Je t'enverrai la météo tous les jours à 9h.")

async def main():
    """Initialisation du bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Ajout des commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("meteo", send_weather))

    # Configuration du JobQueue
    job_queue = application.job_queue
    job_queue.run_daily(send_daily_weather, time=datetime.strptime("09:00", "%H:%M").time())

    # Lancer le bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
