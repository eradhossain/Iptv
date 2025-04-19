import os
from threading import Thread
import app

Thread(target=lambda: app.app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080))), daemon=True).start()
