import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
ALLOWED_USER_IDS = [int(i) for i in os.getenv("ALLOWED_USER_IDS", "").split(",")]
BIN_CHANNEL_ID = int(os.getenv("BIN_CHANNEL_ID"))
BASE_URL = os.getenv("BASE_URL", "https://your-koyeb-app.koyeb.app")

from app import encrypt_filename

app = Client("video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

# Access control
def is_allowed(user_id):
    return user_id == OWNER_ID or user_id in ALLOWED_USER_IDS

@app.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    if not is_allowed(message.from_user.id):
        return await message.reply("Access Denied.")
    await message.reply("Welcome! Send me a video file (MP4/MKV) to get direct stream links.")

@app.on_message(filters.private & filters.command("help"))
async def help_cmd(client, message: Message):
    if not is_allowed(message.from_user.id):
        return await message.reply("Access Denied.")
    await message.reply("/start - Welcome\n/help - Help\nSend video to get direct link.")

@app.on_message(filters.private & filters.video)
async def handle_video(client, message: Message):
    if not is_allowed(message.from_user.id):
        return await message.reply("Access Denied.")

    msg = await message.reply("Uploading to storage...")

    file_name = message.video.file_name or "video.mp4"
    file_path = f"downloads/{file_name}"

    await message.download(file_path)

    sent = await client.send_document(
        BIN_CHANNEL_ID,
        document=file_path,
        caption=f"Uploaded by bot from: {message.from_user.id}",
        file_name=file_name
    )

    encrypted = encrypt_filename(file_name)
    link = f"{BASE_URL}/stream/{encrypted}"

    await msg.edit_text(
        f"**Your Direct Streaming Link:**\n\n"
        f"`{link}`\n\n"
        f"Play in VLC / MX Player."
    )

if __name__ == "__main__":
    app.run()