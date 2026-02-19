import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from solana.rpc.api import Client

# Logging pour debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# BOT_TOKEN depuis variable d'environnement Render (pas en dur dans le code !)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# RPC Solana (public gratuit, ou change pour Helius si tu as une clé)
RPC_URL = "https://api.mainnet-beta.solana.com"
client = Client(RPC_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salut ! Je suis Solana Gold Guard Bot 🛡️\n"
        "Envoie-moi une adresse mint de token Solana pour un scan rug-check rapide.\n"
        "Exemple : 4cYExfzqXoSG4R1kTUnuyBGpvJaEdrW79gAPqeAnmoon"
    )

async def scan_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token_address = update.message.text.strip()
    if len(token_address) != 44:  # Validation basique Solana address
        await update.message.reply_text("Envoie une adresse mint valide (44 caractères).")
        return

    try:
        # Basics via Solana RPC
        supply_info = client.get_token_supply(token_address)
        supply = supply_info.value.ui_amount if supply_info.value else "Inconnu"

        # Dexscreener API (gratuit, limite ~60 req/min)
        dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(dex_url, timeout=10)
        data = response.json() if response.status_code == 200 else {}

        if data.get("pairs"):
            pair = data["pairs"][0]
            liquidity_usd = pair.get("liquidity", {}).get("usd", "N/A")
            fdv = pair.get("fdv", "N/A")
            price_usd = pair.get("priceUsd", "N/A")

            liq_status = "Correcte / Locked ?" if liquidity_usd and liquidity_usd > 10000 else "Faible ou suspicious (risque rug !)"

            msg = f"**Scan rapide de {token_address}** 🛡️\n\n"
            msg += f"Supply total : {supply} tokens\n"
            msg += f"Prix actuel : ${price_usd}\n"
            msg += f"Liquidity : ${liquidity_usd} ({liq_status})\n"
            msg += f"FDV : ${fdv}\n\n"
            msg += "Pour plus : Rugcheck.xyz / Birdeye.so\n"
            msg += "DYOR – Pas de garantie ! 🚨"
        else:
            msg = "Pas de paire trouvée sur Dexscreener. Token mort ou pas listé ?"

        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Erreur scan : {str(e)}\nRéessaie ou envoie une adresse valide.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_token))

    app.run_polling()

if __name__ == '__main__':
    main()
