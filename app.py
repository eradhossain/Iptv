from flask import Flask, request, redirect, send_file, abort
import os
import base64

app = Flask(__name__)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "secret_key")

def encrypt_filename(name: str) -> str:
    encoded = base64.urlsafe_b64encode(name.encode()).decode()
    return f"{encoded}.mp4"

def decrypt_filename(encoded: str) -> str:
    try:
        encoded = encoded.replace(".mp4", "")
        return base64.urlsafe_b64decode(encoded.encode()).decode()
    except:
        return None

@app.route('/')
def home():
    return "<h2>Telegram Video Bot is Online</h2>"

@app.route('/stream/<filename>')
def stream_file(filename):
    original = decrypt_filename(filename)
    if not original or not os.path.exists(f"downloads/{original}"):
        return abort(404)
    return send_file(f"downloads/{original}", as_attachment=False)

@app.route('/generate')
def generate():
    filename = request.args.get("file")
    if not filename:
        return "Missing ?file= parameter"
    encrypted = encrypt_filename(filename)
    return f"https://your-koyeb-app.koyeb.app/stream/{encrypted}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)