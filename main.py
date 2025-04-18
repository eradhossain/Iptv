import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import subprocess
from flask import Flask, send_from_directory

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask for file serving
app = Flask(__name__)

# Path for storing MP4 and HLS files
UPLOAD_FOLDER = './uploads'
HLS_FOLDER = './hls'

# Create necessary directories
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(HLS_FOLDER):
    os.makedirs(HLS_FOLDER)

# Command to convert MP4 to HLS using FFmpeg
def convert_to_hls(mp4_file):
    output_dir = os.path.join(HLS_FOLDER, os.path.splitext(os.path.basename(mp4_file))[0])
    os.makedirs(output_dir, exist_ok=True)

    command = [
        'ffmpeg', '-i', mp4_file, '-preset', 'fast', '-g', '48', '-sc_threshold', '0',
        '-map', '0:v:0', '-map', '0:a:0', '-b:v:0', '800k', '-s:v:0', '854x480',
        '-b:v:1', '1400k', '-s:v:1', '1280x720', '-b:v:2', '2500k', '-s:v:2', '1920x1080',
        '-f', 'hls', '-var_stream_map', 'v:0,a:0 v:1,a:0 v:2,a:0', '-master_pl_name', 'master.m3u8',
        '-hls_time', '6', '-hls_list_size', '0', '-hls_segment_filename', os.path.join(output_dir, "stream_%v_%03d.ts"),
        os.path.join(output_dir, "stream_%v.m3u8")
    ]
    subprocess.run(command, check=True)
    return os.path.join(output_dir, "master.m3u8")

# Start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! Send me an MP4 file and I will convert it to HLS!")

# Handle file upload
def handle_video(update: Update, context: CallbackContext) -> None:
    file = update.message.video or update.message.document
    if file:
        file_id = file.file_id
        new_file = context.bot.get_file(file_id)
        file_name = f"{file.file_id}.mp4"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        # Download file
        new_file.download(file_path)
        update.message.reply_text("File received, converting to HLS...")

        # Convert MP4 to HLS
        master_m3u8 = convert_to_hls(file_path)

        # Send the HLS link
        update.message.reply_text(f"Your HLS stream is ready: \n\n{master_m3u8}")

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Flask route to serve the HLS stream
@app.route('/static/hls/<path:filename>')
def serve_file(filename):
    return send_from_directory(HLS_FOLDER, filename)

def main() -> None:
    # Start the bot
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))

    # Handle file upload
    dispatcher.add_handler(MessageHandler(Filters.video | Filters.document.mime_type("video/mp4"), handle_video))

    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the Flask app for serving files
    updater.start_polling()
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
