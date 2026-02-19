import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Configurer les logs pour voir les erreurs réelles
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. Tes fonctions DOIVENT être async avec ces arguments
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot connecté et fonctionnel !")

async def scan_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Exemple de logique simple pour tester la réception
    user_text = update.message.text
    await update.message.reply_text(f"🔍 Analyse du token : {user_text}")

def main():
    # Remplace par ton token si os.environ ne fonctionne pas en local
    token = os.environ.get('BOT_TOKEN') 
    
    if not token:
        print("❌ ERREUR : Le token est vide !")
        return

    # Construction de l'app (v20+)
    app = ApplicationBuilder().token(token).build()

    # Ajout des handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), scan_token))

    print("🚀 Le bot démarre... Appuie sur CTRL+C pour arrêter.")
    
    # La méthode standard qui gère la boucle asyncio pour toi
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
