import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION DU LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. TES FONCTIONS (DOIVENT ÊTRE ASYNC) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Répond quand l'utilisateur tape /start"""
    await update.message.reply_text(
        "🚀 Bot Solana Scan activé !\n"
        "Envoie-moi l'adresse d'un token pour l'analyser."
    )

async def scan_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Répond à l'adresse du token envoyée"""
    user_input = update.message.text
    await update.message.reply_text(f"🔍 Analyse en cours pour : `{user_input}`...", parse_mode='Markdown')
    
    # Simule une attente de scan
    await asyncio.sleep(1) 
    await update.message.reply_text("✅ Scan terminé. (Logique Solana à insérer ici)")

# --- 3. LA LOGIQUE DE LANCEMENT (CORRIGÉE POUR PYTHON 3.14) ---

async def run_bot():
    """Fonction principale asynchrone"""
    token = os.environ.get('BOT_TOKEN')
    
    if not token:
        logger.error("❌ ERREUR : Le BOT_TOKEN est introuvable dans les variables d'environnement.")
        return

    # Construction de l'application
    application = ApplicationBuilder().token(token).build()

    # Ajout des handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), scan_token))

    logger.info("=== LE BOT DÉMARRE (MODE ASYNC) ===")

    # Initialisation et démarrage manuel pour éviter le bug de boucle sur Render/Python 3.14
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        # Cette boucle maintient le bot en vie indéfiniment
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        # On lance la boucle asyncio proprement
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot arrêté proprement.")
    except Exception as e:
        logger.critical(f"Erreur fatale lors du lancement : {e}", exc_info=True)
