import os
import logging
import subprocess
import requests

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from flask import Flask, send_from_directory, request
from threading import Thread

# Set Telegram Bot Token (set as env var or hardcode it)
BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_TELEGRAM_BOT_TOKEN_HERE"

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Directories
UPLOAD_FOLDER = './uploads'
HLS_FOLDER = './hls'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HLS_FOLDER, exist_ok=True)

# Max 2 GB upload limit for Flask
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB

# Convert MP4 to HLS
def convert_to_hls(mp4_file):
    base_name = os.path.splitext(os.path.basename(mp4_file))[0]
    output_dir = os.path.join(HLS_FOLDER, base_name)
    os.makedirs(output_dir, exist_ok=True)

    command = [
        'ffmpeg', '-y', '-threads', '2', '-i', mp4_file,
        '-preset', 'veryfast', '-g', '48', '-sc_threshold', '0',
        '-map', '0', '-map', '0', '-map', '0',
        '-s:v:0', '854x480', '-b:v:0', '800k',
        '-s:v:1', '1280x720', '-b:v:1', '1400k',
        '-s:v:2', '1920x1080', '-b:v:2', '2500k',
        '-c:v', 'libx264', '-c:a', 'aac', '-ar', '48000',
        '-f', 'hls', '-var_stream_map', 'v:0,a:0 v:1,a:0 v:2,a:0',
        '-master_pl_name', 'master.m3u8',
        '-hls_time', '6', '-hls_list_size', '0',
        '-hls_segment_filename', os.path.join(output_dir, 'stream_%v_%03d.ts'),
        os.path.join(output_dir, 'stream_%v.m3u8')
    ]

    subprocess.run(command, check=True)
    return f"https://{request.host}/static/hls/{base_name}/master.m3u8"

# Telegram: /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me an MP4 video file (up to 2 GB) and I will convert it to HLS stream.")

# Telegram: Handle MP4
def handle_video(update: Update, context: CallbackContext):
    file = update.message.video or update.message.document
    if file:
        file_id = file.file_id
        file_name = f"{file_id}.mp4"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        update.message.reply_text("Downloading your file...")

        try:
            file_obj = context.bot.get_file(file_id)
            file_url = file_obj.file_path

            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_url}"
            response = requests.get(download_url, stream=True)

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            update.message.reply_text("Converting video to HLS format. Please wait...")

            hls_link = convert_to_hls(file_path)
            update.message.reply_text(f"✅ Your stream is ready:\n{hls_link}")

        except Exception as e:
            logger.error(f"Error: {e}")
            update.message.reply_text("❌ Failed to process video. Check file size and try again.")

# Flask: Serve HLS
@app.route('/static/hls/<path:filename>')
def serve_file(filename):
    return send_from_directory(HLS_FOLDER, filename)

# Run Flask
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Main Bot
def main():
    Thread(target=run_flask).start()

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video | Filters.document.mime_type("video/mp4"), handle_video))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
