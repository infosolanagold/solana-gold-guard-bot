import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION DU LOGGING (Pour voir ce qui se passe) ---
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
    """Répond à n'importe quel message texte (L'analyse du token)"""
    user_input = update.message.text
    
    # Message d'attente pour l'utilisateur
    await update.message.reply_text(f"🔍 Analyse en cours pour : `{user_input}`...", parse_mode='Markdown')
    
    # --- ICI TU AJOUTERAS TA LOGIQUE SOLANA (RPC, API, etc.) ---
    # Exemple : result = ta_fonction_de_scan(user_input)
    
    await update.message.reply_text("✅ Analyse terminée (Simulation).")

# --- 3. LE COEUR DU BOT (MAIN) ---

def main():
    # Récupération du Token (Variable d'environnement ou direct pour test)
    # Remplacer os.environ.get('BOT_TOKEN') par "TON_TOKEN" si tu testes en local sans variable d'env.
    token = os.environ.get('BOT_TOKEN') 

    if not token:
        logger.error("❌ ERREUR : Le BOT_TOKEN est introuvable. Vérifie tes variables d'environnement.")
        return

    # Création de l'application (Version 20+ de python-telegram-bot)
    application = ApplicationBuilder().token(token).build()

    # Ajout des commandes et des écouteurs de messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), scan_token))

    logger.info("=== LE BOT DÉMARRE ===")
    
    # Lancement du bot (Gère automatiquement la boucle asyncio)
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
