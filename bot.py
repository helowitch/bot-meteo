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
    "Villaroger,FR": "💛 VILLAROGER",
    "La Chapelle-Bouëxic,FR": "🖤 LA CHAPELLE-BOUËXIC",
    "Genève,CH": "💚 GENÈVE",
    "Bristol,GB": "💙 BRISTOL",
    "Roncq,FR": "💜 RONCQ",
    "Montélimar,FR": "🤍 MONTÉLIMAR",
}

# Dictionnaire de correspondance entre les codes météo et les emojis
WEATHER_EMOJIS = {
    # Group 2xx: Thunderstorm
    "200": "⛈️",  # thunderstorm with light rain
    "201": "⛈️",  # thunderstorm with rain
    "202": "⛈️",  # thunderstorm with heavy rain
    "210": "🌩️",  # light thunderstorm
    "211": "🌩️",  # thunderstorm
    "212": "🌩️",  # heavy thunderstorm
    "221": "🌩️",  # ragged thunderstorm
    "230": "⛈️",  # thunderstorm with light drizzle
    "231": "⛈️",  # thunderstorm with drizzle
    "232": "⛈️",  # thunderstorm with heavy drizzle
    
    # Group 3xx: Drizzle
    "300": "🌧️",  # light intensity drizzle
    "301": "🌧️",  # drizzle
    "302": "🌧️",  # heavy intensity drizzle
    "310": "🌧️",  # light intensity drizzle rain
    "311": "🌧️",  # drizzle rain
    "312": "🌧️",  # heavy intensity drizzle rain
    "313": "🌧️",  # shower rain and drizzle
    "314": "🌧️",  # heavy shower rain and drizzle
    "321": "🌧️",  # shower drizzle
    
    # Group 5xx: Rain
    "500": "🌦️",  # light rain
    "501": "🌧️",  # moderate rain
    "502": "🌧️",  # heavy intensity rain
    "503": "🌧️",  # very heavy rain
    "504": "🌧️",  # extreme rain
    "511": "🌨️",  # freezing rain
    "520": "🌦️",  # light intensity shower rain
    "521": "🌧️",  # shower rain
    "522": "🌧️",  # heavy intensity shower rain
    "531": "🌧️",  # ragged shower rain
    
    # Group 6xx: Snow
    "600": "❄️",  # light snow
    "601": "❄️",  # snow
    "602": "❄️",  # heavy snow
    "611": "🌨️",  # sleet
    "612": "🌨️",  # light shower sleet
    "613": "🌨️",  # shower sleet
    "615": "🌨️",  # light rain and snow
    "616": "🌨️",  # rain and snow
    "620": "🌨️",  # light shower snow
    "621": "🌨️",  # shower snow
    "622": "🌨️",  # heavy shower snow
    
    # Group 7xx: Atmosphere
    "701": "🌫️",  # mist
    "711": "🌫️",  # smoke
    "721": "🌫️",  # haze
    "731": "🌪️",  # sand/dust whirls
    "741": "🌁",  # fog
    "751": "🌫️",  # sand
    "761": "🌫️",  # dust
    "762": "🌋",  # volcanic ash
    "771": "🌬️",  # squalls
    "781": "🌪️",  # tornado
    
    # Group 800: Clear
    "800": "☀️",  # clear sky
    
    # Group 80x: Clouds
    "801": "🌤️",  # few clouds: 11-25%
    "802": "⛅",  # scattered clouds: 25-50%
    "803": "🌥️",  # broken clouds: 51-84%
    "804": "☁️",  # overcast clouds: 85-100%
}

async def get_weather(city):
    """Récupère la météo actuelle pour une ville donnée."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fr"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = round(data["main"]["temp"], 1)
                description = data["weather"][0]["description"].capitalize()
                weather_code = str(data["weather"][0]["id"])
                emoji = WEATHER_EMOJIS.get(weather_code, "🌍")
                return f"{VILLES[city]} : {temp}°C, {description} {emoji}"
            else:
                return f"{VILLES[city]} : Impossible de récupérer la météo ❌"

async def get_daily_forecast(city):
    """Récupère les prévisions générales pour la journée."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fr&cnt=8"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                forecast = data["list"][0]
                temp = round(forecast["main"]["temp"], 1)
                description = forecast["weather"][0]["description"].capitalize()
                weather_code = str(forecast["weather"][0]["id"])
                emoji = WEATHER_EMOJIS.get(weather_code, "🌍")
                return f"{VILLES[city]} : {temp}°C, {description} {emoji}"
            else:
                return f"{VILLES[city]} : Impossible de récupérer les prévisions ❌"

async def send_daily_forecast(context: CallbackContext):
    """Envoie les prévisions quotidiennes automatiquement."""
    weather_reports = [await get_daily_forecast(city) for city in VILLES]
    message = "📅 Prévisions du jour :\n" + "\n".join(weather_reports) + "\n\nBonne journée ! 🌈"
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text=message)

async def start(update: Update, context: CallbackContext) -> None:
    """Commande /start"""
    await update.message.reply_text("Bonjour ! 🌤️ Tape /meteo pour voir la météo actuelle des villes sélectionnées.")

async def meteo(update: Update, context: CallbackContext) -> None:
    """Affiche la météo en direct sur commande."""
    weather_reports = [await get_weather(city) for city in VILLES]
    message = "🌦️ Météo en direct :\n" + "\n".join(weather_reports)
    await update.message.reply_text(message)

async def schedule_weather(update: Update, context: CallbackContext):
    """Programme l'envoi automatique des prévisions à 9h."""
    chat_id = update.message.chat_id
    context.job_queue.run_daily(send_daily_forecast, time=time(hour=7, minute=0), chat_id=chat_id)
    await update.message.reply_text("✅ Prévisions quotidiennes programmées à 9h ! ⏰")

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