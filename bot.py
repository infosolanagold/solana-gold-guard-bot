import asyncio
import logging
import os

# Assure-toi que ces imports sont déjà présents en haut de ton fichier
# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
# import requests
# from solana.rpc.api import Client

# ... (tes autres imports et fonctions start() et scan_token() restent inchangés)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

def main():
    # Configuration logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN non trouvé dans les variables d'environnement !")
        return

    logger.info("=== BOT STARTING ===")
    logger.info(f"Token loaded: {BOT_TOKEN[:10]}... (hidden)")

    # Création de l'event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Création de l'application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Ajout des handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_token))

    logger.info("Application built - handlers ajoutés")

    try:
        # Séquence recommandée pour polling sur Render / headless
        loop.run_until_complete(application.initialize())
        logger.info("Application initialized")

        loop.run_until_complete(application.start())
        logger.info("Application started")

        # Lance le polling
        loop.run_until_complete(application.updater.start_polling(
            drop_pending_updates=True,  # Ignore les messages en attente au démarrage
            allowed_updates=Update.ALL_TYPES
        ))
        logger.info("Polling démarré avec succès")

        # Garde le programme vivant
        loop.run_forever()

    except KeyboardInterrupt:
        logger.info("Arrêt par KeyboardInterrupt")

    except Exception as e:
        logger.error(f"Erreur critique pendant polling: {e}", exc_info=True)

    finally:
        # Nettoyage propre
        logger.info("Nettoyage final...")
        try:
            loop.run_until_complete(application.updater.stop())
            loop.run_until_complete(application.stop())
            loop.run_until_complete(application.shutdown())
        except Exception as cleanup_error:
            logger.warning(f"Erreur pendant cleanup: {cleanup_error}")
        finally:
            loop.close()
            logger.info("Event loop fermé - fin du bot")

if __name__ == '__main__':
    main()
