import os
from threading import Thread
import app
import bot
import time

# Start Flask server in a thread
Thread(target=lambda: app.app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080))), daemon=True).start()

# Start Telegram bot (this should block and keep running)
bot.start_bot()

# Optional fallback (won’t be reached unless bot exits)
while True:
    time.sleep(10)