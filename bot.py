from pyrogram import Client, filters
import os
from app import encrypt_filename

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USER_IDS", "").split(",")))

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.user(ALLOWED_USERS))
async def get_video(client, message):
    if message.video or message.document:
        file = await message.download(file_name=f"downloads/{message.video.file_name}")
        encrypted_name = encrypt_filename(message.video.file_name)
        url = f"https://your-koyeb-app.koyeb.app/stream/{encrypted_name}"
        await message.reply(f"Direct Link (MP4):\n{url}\n\nPlayable in VLC/MX Player.")
    else:
        await message.reply("Send a video or file.")

@app.on_message(filters.command("help") & filters.private)
async def help_msg(client, message):
    await message.reply("Send a video file and get a direct streaming MP4 link.")

app.run()