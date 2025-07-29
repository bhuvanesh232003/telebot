import os
import asyncio
import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

nest_asyncio.apply()

BOT_TOKEN = '8263130399:AAEAXbk90nTGreBxMVToaPNS2sp4ZIi-gnY'
DOWNLOAD_DIR = "downloads"
MAX_TELEGRAM_FILE_SIZE = 49 * 1024 * 1024  # 49 MB

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Helper: Download video using yt_dlp
def download_video(url: str, output_path: str) -> str:
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an Instagram or YouTube video URL, and I will download it for you.")

# Message: URL handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not any(domain in url for domain in ['instagram.com', 'youtu.be', 'youtube.com']):
        await update.message.reply_text("Please send a valid Instagram or YouTube video link.")
        return

    await update.message.reply_text("📥 Downloading, please wait broo    git init...")

    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        filename_base = os.path.join(DOWNLOAD_DIR, "video.%(ext)s")
        downloaded_path = download_video(url, filename_base)

        if os.path.getsize(downloaded_path) > MAX_TELEGRAM_FILE_SIZE:
            await update.message.reply_text("⚠️ The video is larger than 50MB and cannot be sent over Telegram.")
        else:
            with open(downloaded_path, "rb") as f:
                await update.message.reply_video(f)

        os.remove(downloaded_path)

    except Exception as e:
        logging.error("Download failed:", exc_info=True)
        await update.message.reply_text("❌ Failed to download video. It might be private or blocked.")

# Main function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
