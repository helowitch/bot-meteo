from telegram import Update
from telegram.ext import Application, CommandHandler
import asyncio

TOKEN = "TON_BOT_TOKEN"

async def start(update: Update, context) -> None:
    await update.message.reply_text("Bonjour! Je suis votre bot.")

def main():
    print("Démarrage du bot...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Lancement du polling...")
    application.run_polling()

if __name
