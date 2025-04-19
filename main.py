# main.py

import os, time
from threading import Thread
import app     # your Flask app module
import bot     # your Telegram bot module

# 1) Start Flask in background
Thread(
    target=lambda: app.app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    ),
    daemon=True
).start()

# 2) Start Telegram bot (this blocks — keeps the container alive)
bot.run_bot()

# 3) Fallback loop (in case bot.run_bot ever returns)
while True:
    time.sleep(3600)