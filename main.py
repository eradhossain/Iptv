import os, time
from threading import Thread
import app, bot

# Start Flask in background
Thread(
    target=lambda: app.app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    ),
    daemon=True
).start()

# Start Telegram bot (blocks) 1
bot.start_bot()

# Failsafe so container stays alive
while True:
    time.sleep(3600)