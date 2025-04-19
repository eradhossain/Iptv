import os
import base64
import subprocess
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# Bot configuration from environment
BOT_TOKEN      = os.getenv("BOT_TOKEN")
API_ID         = int(os.getenv("API_ID"))
API_HASH       = os.getenv("API_HASH")
OWNER_ID       = int(os.getenv("OWNER_ID"))
ALLOWED_IDS    = {int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",")}
BIN_CHANNEL_ID = int(os.getenv("BIN_CHANNEL_ID"))
BASE_URL       = os.getenv("BASE_URL")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Initialize Pyrogram client
bot = Client(
    "video_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

def is_allowed(uid: int) -> bool:
    """Check if a user is allowed to use the bot."""
    return uid == OWNER_ID or uid in ALLOWED_IDS  # 0

def encrypt_filename(name: str) -> str:
    """Encrypts filename by appending key and base64-url encoding without padding."""
    payload = f"{name}:{ENCRYPTION_KEY}".encode()
    token = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return token  # 1

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    """Handle /start command."""
    if not is_allowed(message.from_user.id):
        return await message.reply("❌ Access Denied.")
    await message.reply("👋 Hi! Send me a MP4 or MKV video and I'll return multi-quality streaming links.")

@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    """Handle /help command."""
    if not is_allowed(message.from_user.id):
        return await message.reply("❌ Access Denied.")
    help_text = (
        "📖 **How to use:**\n"
        "1. Send a MP4/MKV video.\n"
        "2. The bot will convert it to 480p, 720p & 1080p.\n"
        "3. Receive encrypted .mp4 links for each quality.\n"
        "4. Play links in VLC or MX Player."
    )
    await message.reply(help_text)

@bot.on_message(filters.private & (filters.video | filters.document))
async def handle_video(client: Client, message: Message):
    """Download, convert to multiple qualities, upload, and reply with links."""
    user_id = message.from_user.id
    if not is_allowed(user_id):
        return await message.reply("❌ Access Denied.")

    status = await message.reply("📥 Downloading...")
    # Download to a temporary file
    downloaded = await message.download()  # 2
    filename = os.path.basename(downloaded)
    base, ext = os.path.splitext(filename)

    # Ensure downloads folder exists
    os.makedirs("downloads", exist_ok=True)

    # Define quality settings: (width, height, output path, ffmpeg CRF)
    qualities = {
        "480p": ("854", "480", f"downloads/{base}_480p.mp4", "28"),
        "720p": ("1280", "720", f"downloads/{base}_720p.mp4", "23"),
        "1080p":("1920", "1080",f"downloads/{base}_1080p.mp4","20"),
    }

    # Convert to each quality using FFmpeg scale filter 
    await status.edit("⚙️ Converting to multiple qualities...")
    for label, (w, h, out_path, crf) in qualities.items():
        subprocess.run([
            "ffmpeg", "-i", downloaded,
            "-vf", f"scale={w}:{h}",
            "-c:v", "libx264",
            "-crf", crf,
            "-preset", "fast",
            "-c:a", "aac",
            out_path
        ], check=True)

    await status.edit("⬆️ Uploading to Telegram BIN channel...")
    links = []
    # Upload each converted file and generate encrypted link
    for label, (_,_, out_path, _) in qualities.items():
        sent_msg = await bot.send_document(
            BIN_CHANNEL_ID,
            document=out_path,
            caption=f"{label} | uploaded by {user_id}"
        )  # 4
        encrypted = encrypt_filename(os.path.basename(out_path))
        link = f"{BASE_URL}/stream/{encrypted}.mp4"
        links.append(f"**{label}**: `{link}`")

    # Send all links in one message
    await status.edit("✅ Conversion complete!\n\n" + "\n".join(links))

    # Cleanup temp files
    try:
        os.remove(downloaded)
        for _,(_,_,out_path,_) in qualities.items():
            os.remove(out_path)
    except Exception:
        pass

def start_bot():
    """Run the bot (blocking)."""
    bot.run()  # 5

if __name__ == "__main__":
    start_bot()