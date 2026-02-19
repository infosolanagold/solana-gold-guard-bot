import os
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. LOGIQUE DE SÉCURITÉ (SAFETY CHECK) ---

def check_honeypot(token_address):
    """Vérifie si le token semble être un honeypot via l'API RugCheck ou similaire"""
    try:
        # On interroge RugCheck pour un résumé rapide
        rc_url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report/summary"
        response = requests.get(rc_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            score = data.get('score', 0)
            if score > 5000: return "⚠️ HIGH RISK"
            if score > 1000: return "🟡 MEDIUM RISK"
            return "✅ SAFE"
    except:
        return "❓ UNKNOWN"
    return "❓ UNKNOWN"

# --- 3. FONCTIONS DU BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *Solana Sentinel Bot Active*\n\n"
        "Send me any Token Address (CA) to get a professional report.",
        parse_mode='Markdown'
    )

async def scan_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token_address = update.message.text.strip()
    
    # Message de chargement avec animation simple
    status_message = await update.message.reply_text(f"📡 *Analyzing* `{token_address[:6]}...{token_address[-4:]}`...", parse_mode='Markdown')

    try:
        # Données Marché (DexScreener)
        dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        dex_data = requests.get(dex_url, timeout=10).json()

        if not dex_data.get('pairs'):
            await status_message.edit_text("❌ *Token not found or no liquidity.*")
            return

        pair = dex_data['pairs'][0]
        base = pair.get('baseToken', {})
        
        # Sécurité
        safety_status = check_honeypot(token_address)

        # Rapport en Anglais Raffiné
        report = (
            f"📊 *{base.get('name')} ({base.get('symbol')}) Report*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ *Safety:* {safety_status}\n"
            f"💰 *Price:* ${pair.get('priceUsd', '0.00')}\n"
            f"📈 *24h:* {pair.get('priceChange', {}).get('h24', 0)}%\n"
            f"💎 *MCap:* ${pair.get('fdv', 0):,.0f}\n"
            f"💧 *Liq:* ${pair.get('liquidity', {}).get('usd', 0):,.0f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 *Created:* {pair.get('pairCreatedAt', 'N/A')}"
        )

        # Boutons d'action
        keyboard = [
            [
                InlineKeyboardButton("🚀 Buy on Jupiter", url=f"https://jup.ag/swap/SOL-{token_address}"),
                InlineKeyboardButton("🦅 DexScreener", url=pair.get('url'))
            ],
            [
                InlineKeyboardButton("🛡️ RugCheck Full Report", url=f"https://rugcheck.xyz/tokens/{token_address}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await status_message.edit_text(report, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_message.edit_text("⚠️ *Analysis failed.* The API might be down.")

# --- 4. RUNNER ---

async def run_bot():
    token = os.environ.get('BOT_TOKEN')
    if not token: return
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), scan_token))

    logger.info("=== BOT REFINED & STARTED ===")
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except:
        pass
