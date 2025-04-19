import os, time
from threading import Thread
import app, bot

# 1) Start Flask in background
Thread(
    target=lambda: app.app.run(
        host="0.0.0.0", port=int(os.getenv("PORT", 8080))
    ),
    daemon=True
).start()

# 2) Start Telegram bot (blocks)
bot.start_bot()

# 3) Keep alive if bot ever exits
while True:
    time.sleep(10)