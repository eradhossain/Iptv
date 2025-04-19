import os, base64
from flask import Flask, send_file, abort
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

def decrypt_filename(token: str) -> str | None:
    """Base64‑URL decode and verify ENCRYPTION_KEY suffix."""
    if token.endswith(".mp4"):
        token = token[:-4]
    try:
        data = base64.urlsafe_b64decode(token + "==").decode()
        name, key = data.rsplit(":", 1)
        return name if key == ENCRYPTION_KEY else None
    except:
        return None

@app.route("/stream/<token>.mp4")
def stream(token):
    real_name = decrypt_filename(token)
    if not real_name:
        return abort(404, "Invalid or tampered link.")
    path = os.path.join("downloads", real_name)
    if not os.path.isfile(path):
        return abort(404, "File not found.")
    return send_file(path, mimetype="video/mp4")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)