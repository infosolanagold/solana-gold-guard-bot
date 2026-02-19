import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. LOGGING CONFIGURATION ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. BOT FUNCTIONS (ASYNC) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers when the user types /start"""
    await update.message.reply_text(
        "🚀 *Solana Scanner Bot Active!*\n\n"
        "Send me a token mint address (CA) to analyze its market data.",
        parse_mode='Markdown'
    )

async def scan_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches real-time data from DexScreener API"""
    token_address = update.message.text.strip()
    
    # Send a waiting message
    status_message = await update.message.reply_text(
        f"🔎 *Scanning:* `{token_address}`...", 
        parse_mode='Markdown'
    )

    try:
        # Fetching data from DexScreener
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if not data.get('pairs'):
            await status_message.edit_text("❌ *Token not found.* Please check the address.")
            return

        # Extract the main pair (highest liquidity)
        pair = data['pairs'][0]
        base = pair.get('baseToken', {})
        
        name = base.get('name', 'Unknown')
        symbol = base.get('symbol', '???')
        price = pair.get('priceUsd', '0.00')
        mcap = pair.get('fdv', 0)
        liquidity = pair.get('liquidity', {}).get('usd', 0)
        change_24h = pair.get('priceChange', {}).get('h24', 0)

        # Build English report
        report = (
            f"📊 *Token Report: {name} ({symbol})*\n\n"
            f"💰 *Price:* ${price}\n"
            f"📈 *24h Change:* {change_24h}%\n"
            f"💎 *Market Cap:* ${mcap:,.0f}\n"
            f"💧 *Liquidity:* ${liquidity:,.0f}\n\n"
            f"🔗 [View on DexScreener]({pair.get('url')})"
        )

        await status_message.edit_text(report, parse_mode='Markdown', disable_web_page_preview=False)

    except Exception as e:
        logger.error(f"Scan error: {e}")
        await status_message.edit_text("⚠️ *Error:* Failed to fetch data from the blockchain.")

# --- 3. MAIN RUNNER (ASYNC) ---

async def run_bot():
    """Main async function to handle Python 3.14 event loop"""
    token = os.environ.get('BOT_TOKEN')
    
    if not token:
        logger.error("❌ ERROR: BOT_TOKEN not found in environment variables.")
        return

    application = ApplicationBuilder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), scan_token))

    logger.info("=== BOT STARTED SUCCESSFULLY ===")

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        # Keep the bot running
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
