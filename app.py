from flask import Flask, request, send_file, abort
import os
import base64

app = Flask(__name__)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "secret_key")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")  # fallback for local testing

# Simple base64 encryption with .mp4 extension
def encrypt_filename(name: str) -> str:
    encoded = base64.urlsafe_b64encode(name.encode()).decode()
    return f"{encoded}.mp4"

# Decrypt and get original filename
def decrypt_filename(encoded: str) -> str:
    try:
        encoded = encoded.replace(".mp4", "")
        return base64.urlsafe_b64decode(encoded.encode()).decode()
    except Exception:
        return None

@app.route('/')
def home():
    return "<h2>Telegram Video Bot is Live on Koyeb!</h2>"

@app.route('/stream/<filename>')
def stream_file(filename):
    original = decrypt_filename(filename)
    if not original:
        return abort(400, description="Invalid link.")
    
    path = os.path.join("downloads", original)
    if not os.path.isfile(path):
        return abort(404, description="File not found.")
    
    return send_file(path, as_attachment=False)

@app.route('/generate')
def generate_link():
    filename = request.args.get("file")
    if not filename:
        return "Missing ?file= parameter"
    
    encrypted = encrypt_filename(filename)
    link = f"{BASE_URL}/stream/{encrypted}"
    return f"Encrypted MP4 Link:\n{link}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # important for Koyeb
    app.run(host='0.0.0.0', port=port)