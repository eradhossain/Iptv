import os
import base64
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

BOT_TOKEN      = os.getenv("BOT_TOKEN")
API_ID         = int(os.getenv("API_ID"))
API_HASH       = os.getenv("API_HASH")
BIN_CHANNEL_ID = int(os.getenv("BIN_CHANNEL_ID"))
ALLOWED_USERS  = [int(x) for x in os.getenv("ALLOWED_USER_IDS").split(",")]
BASE_URL       = os.getenv("BASE_URL")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

app = Client("video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def encrypt_filename(name: str) -> str:
    data = f"{name}:{ENCRYPTION_KEY}".encode()
    return base64.urlsafe_b64encode(data).decode().strip("=")

def is_allowed(uid: int) -> bool:
    return uid in ALLOWED_USERS or uid == int(os.getenv("OWNER_ID"))

@app.on_message(filters.command("start") & filters.private)
async def start(_, msg: Message):
    await msg.reply("Send me a MP4/MKV file to get multi‑quality streaming links.")

@app.on_message(filters.private & (filters.video | filters.document))
async def handle_video(client: Client, msg: Message):
    if not is_allowed(msg.from_user.id):
        return await msg.reply("❌ Access Denied.")
    status = await msg.reply("📥 Downloading...")
    file_path = await msg.download()
    fname = os.path.basename(file_path)
    base = os.path.splitext(fname)[0]

    # Transcode into qualities
    qualities = {
        "480p": (854, 480, f"downloads/{base}_480p.mp4", 28),
        "720p": (1280, 720, f"downloads/{base}_720p.mp4", 23),
        "1080p": (1920, 1080, f"downloads/{base}_1080p.mp4", 20),
    }
    await status.edit("⚙️ Converting qualities...")
    for label, (w, h, out, crf) in qualities.items():
        subprocess.run([
            "ffmpeg", "-i", file_path,
            "-vf", f"scale={w}:{h}",
            "-c:v", "libx264", "-crf", str(crf),
            "-preset", "fast", "-c:a", "aac", out
        ])
    await status.edit("⬆️ Uploading to BIN channel...")
    links = []
    for label, (_, _, out, _) in qualities.items():
        doc = await app.send_document(BIN_CHANNEL_ID, out, caption=label)
        enc = encrypt_filename(os.path.basename(out))
        links.append(f"**{label}**: `{BASE_URL}/stream/{enc}.mp4`")
    await status.edit("✅ Here are your links:\n\n" + "\n".join(links))

def run_bot():
    app.run()

if __name__ == "__main__":
    run_bot()