import os, subprocess, base64
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# Initialize
BOT = Client(
    "video_bot",
    bot_token=os.getenv("BOT_TOKEN"),
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH")
)

OWNER_ID        = int(os.getenv("OWNER_ID"))
ALLOWED_IDS     = {int(x) for x in os.getenv("ALLOWED_USER_IDS").split(",")}
BIN_CHANNEL_ID  = int(os.getenv("BIN_CHANNEL_ID"))
BASE_URL        = os.getenv("BASE_URL")
ENCRYPTION_KEY  = os.getenv("ENCRYPTION_KEY")

def is_allowed(uid: int) -> bool:
    return uid == OWNER_ID or uid in ALLOWED_IDS

def encrypt(name: str) -> str:
    """Encode filename with key suffix, then Base64‑URL (no padding)."""
    payload = f"{name}:{ENCRYPTION_KEY}".encode()
    token = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return token

@BOT.on_message(filters.command("start") & filters.private)
async def cmd_start(_, msg: Message):
    if not is_allowed(msg.from_user.id):
        return await msg.reply("❌ You are not allowed.")
    await msg.reply("👋 Send me a video (MP4/MKV). I'll give direct streaming links in 480p, 720p & 1080p.")

@BOT.on_message(filters.command("help") & filters.private)
async def cmd_help(_, msg: Message):
    if not is_allowed(msg.from_user.id):
        return await msg.reply("❌ You are not allowed.")
    await msg.reply("1️⃣ Send MP4/MKV video\n2️⃣ Receive 3 encrypted `.mp4` links\n3️⃣ Play in VLC/MX Player")

@BOT.on_message(filters.private & (filters.video | filters.document))
async def handle_upload(_, msg: Message):
    uid = msg.from_user.id
    if not is_allowed(uid):
        return await msg.reply("❌ Access denied.")

    status = await msg.reply("📥 Downloading…")
    path = await msg.download()  # saves to local path
    fname = os.path.basename(path)
    base, _ = os.path.splitext(fname)

    qualities = {
        "480p": (854, 480, f"downloads/{base}_480p.mp4", 28),
        "720p": (1280, 720, f"downloads/{base}_720p.mp4", 23),
        "1080p": (1920, 1080, f"downloads/{base}_1080p.mp4", 20),
    }

    await status.edit("⚙️ Converting to multiple qualities…")
    for label, (w,h,out,crf) in qualities.items():
        subprocess.run([
            "ffmpeg", "-i", path,
            "-vf", f"scale={w}:{h}",
            "-c:v", "libx264", "-crf", str(crf),
            "-preset", "fast", "-c:a", "aac", out
        ], check=True)

    await status.edit("⬆️ Uploading to BIN channel…")
    links = []
    for label, (_,_,out,_) in qualities.items():
        sent = await BOT.send_document(
            BIN_CHANNEL_ID,
            document=out,
            caption=f"{label} | uploaded by {uid}"
        )
        # get local filename (we re‑use our encoded name, not Telegram file_id)
        enc = encrypt(os.path.basename(out))
        links.append(f"**{label}**: `{BASE_URL}/stream/{enc}.mp4`")

    await status.edit("✅ Here are your streaming links:\n\n" + "\n".join(links))
    # cleanup
    for _,_,out,_ in qualities.items():
        try: os.remove(out)
        except: pass
    try: os.remove(path)
    except: pass

def start_bot():
    BOT.run()