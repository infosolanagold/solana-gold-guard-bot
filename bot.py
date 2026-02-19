import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION DES LOGS ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. FONCTIONS DU BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue en anglais"""
    await update.message.reply_text(
        "🚀 *Solana Scanner Bot Active!*\n\n"
        "Send me a token mint address (CA) to analyze its market data.",
        parse_mode='Markdown'
    )

async def scan_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Va chercher les vraies données sur DexScreener"""
    token_address = update.message.text.strip()
    
    # Message de chargement
    status_message = await update.message.reply_text(
        f"🔎 *Scanning address:* `{token_address}`...", 
        parse_mode='Markdown'
    )

    try:
        # Interrogation de l'API DexScreener
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Si le token n'existe pas ou n'a pas de liquidité
        if not data.get('pairs') or len(data['pairs']) == 0:
            await status_message.edit_text("❌ *Token not found.* Make sure the address is correct and has liquidity on DEX.")
            return

        # On prend la paire principale (la première)
        pair = data['pairs'][0]
        base_token = pair.get('baseToken', {})
        
        name = base_token.get('name', 'Unknown')
        symbol = base_token.get('symbol', '???')
        price = pair.get('priceUsd', '0.00')
        mcap = pair.get('fdv', 0) 
        liquidity = pair.get('liquidity', {}).get('usd', 0)
        change_24h = pair.get('priceChange', {}).get('h24', 0)

        # Construction du rapport en ANGLAIS
        report = (
            f"📊 *Token Report: {name} ({symbol})*\n\n"
            f"💰 *Price:* ${price}\n"
            f"📈 *24h Change:* {change_24h}%\n"
            f"💎 *Market Cap:* ${mcap:,.0f}\n"
            f"💧 *Liquidity:* ${liquidity:,.0f}\n\n"
            f"🛡️ [RugCheck](https://rugcheck.xyz/tokens/{token_address})\n"
            f"🔗 [DexScreener]({pair.get('url')})"
        )

        await status_message.edit_text(report, parse_mode='Markdown', disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Error during scan: {e}")
        await status_message.edit_text("⚠️ *Error:* Could not fetch data. Please try again later.")

# --- 3. LANCEMENT DU BOT (FIX PYTHON 3.14) ---

async def run_bot():
    token = os.environ.get('BOT_TOKEN')
    
    if not token:
        logger.error("❌ BOT_TOKEN manquant dans les variables d'environnement")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), scan_token))

    logger.info("=== BOT STARTED (REAL DATA MODE) ===")

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
