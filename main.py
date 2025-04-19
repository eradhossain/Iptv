from threading import Thread
import bot
import app

# Start Flask in background
Thread(target=lambda: app.app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080))), daemon=True).start()

# Start Telegram bot
bot.run_bot()