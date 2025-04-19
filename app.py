import os
import base64
from flask import Flask, send_file, abort
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

def encrypt_filename(name: str) -> str:
    data = f"{name}:{ENCRYPTION_KEY}".encode()
    return base64.urlsafe_b64encode(data).decode() + ".mp4"

def decrypt_filename(enc: str) -> str:
    if enc.endswith(".mp4"):
        enc = enc[:-4]
    try:
        name_key = base64.urlsafe_b64decode(enc.encode()).decode()
        name, key = name_key.split(":")
        return name if key == ENCRYPTION_KEY else None
    except:
        return None

@app.route("/stream/<enc>")
def stream(enc):
    fname = decrypt_filename(enc)
    if not fname:
        return abort(404)
    path = os.path.join("downloads", fname)
    if not os.path.isfile(path):
        return abort(404)
    return send_file(path, as_attachment=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)