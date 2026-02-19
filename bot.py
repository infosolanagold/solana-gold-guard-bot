import asyncio
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Ton BOT_TOKEN récupéré depuis les variables d'environnement
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def main():
    # 1. Configuration du logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN non trouvé !")
        return

    # 2. Création de l'application
    # On utilise directement .run_polling() qui gère tout (asyncio, start, stop)
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # 3. Ajout des handlers (Assure-toi que start et scan_token sont définis)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_token))

    logger.info("=== BOT STARTING VIA RUN_POLLING ===")

    # 4. Lancement du bot
    # Cette commande est bloquante et gère parfaitement l'initialisation
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
