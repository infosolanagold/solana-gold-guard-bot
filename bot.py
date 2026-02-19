import asyncio

def main():
    # Crée explicitement un event loop pour éviter le RuntimeError
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_token))

    print("=== BOT STARTING ===")
    print(f"Token loaded: {BOT_TOKEN[:10]}... (hidden)")
    logging.info("Application built")

    # Lance polling dans l'event loop
    try:
        loop.run_until_complete(app.initialize())
        loop.run_until_complete(app.start())
        loop.run_until_complete(app.updater.start_polling())
        print("=== POLLING STARTED ===")
        # Garde le loop vivant
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(app.updater.stop())
        loop.run_until_complete(app.stop())
        loop.run_until_complete(app.shutdown())
        loop.close()

if __name__ == '__main__':
    main()
