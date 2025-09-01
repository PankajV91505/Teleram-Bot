import os
import yt_dlp
import subprocess
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

TOKEN = "BOT TOKEN"

ASK_QUALITY, ASK_THUMB = range(2)
user_links = {}
last_download = {"link": None, "quality": None}

# ----------------------------- Video Download -----------------------------

def download_video(link, quality):
    out_dir = "downloads"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": f"bestvideo[height={quality}]+bestaudio/best[height<={quality}]",
        "outtmpl": out_file,
        "merge_output_format": "mp4",
        "continuedl": True,
        "noplaylist": True,
        "ignoreerrors": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        file_path = ydl.prepare_filename(info)
    return file_path

# ----------------------------- Thumbnail Helpers -----------------------------

def get_default_thumbnail(link, out_name="default_thumbnail.jpg"):
    thumb_dir = "thumb_downloads"
    os.makedirs(thumb_dir, exist_ok=True)
    out_path = os.path.join(thumb_dir, out_name)

    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        if "thumbnails" in info and len(info["thumbnails"]) > 0:
            url = info["thumbnails"][-1]["url"]
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            return out_path
    return None

def extract_thumbnail(video_path, timestamp, out_name="custom_thumbnail.jpg"):
    thumb_dir = "thumb_downloads"
    os.makedirs(thumb_dir, exist_ok=True)
    out_path = os.path.join(thumb_dir, out_name)

    # Convert seconds to HH:MM:SS 
    if timestamp.isdigit():
        seconds = int(timestamp)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        timestamp = f"{h:02}:{m:02}:{s:02}"

    cmd = [
        "ffmpeg",
        "-ss", timestamp,
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        out_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

# ----------------------------- Telegram Bot Functions -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome!\n\nCommands:\n"
        "/download <YouTube_Link> → Download a video\n"
        "/resume → Resume last download\n"
        "/formats <YouTube_Link> → Show available qualities\n"
        "/thumbnail <YouTube_Link> [timestamp] → Get default/custom thumbnail\n"
        "/cancel → Cancel current action"
    )

async def formats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /formats <YouTube_Link>")
        return
    link = context.args[0]

    ydl_opts = {"listformats": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = [f"{f['format_id']} - {f['height']}p - {f.get('ext')}" for f in info["formats"] if f.get("height")]
            msg = "Available Formats:\n" + "\n".join(formats[:20])
            await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def thumbnail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /thumbnail <YouTube_Link> [timestamp]")
        return

    link = context.args[0]
    timestamp = context.args[1] if len(context.args) > 1 else None

    try:
        if not timestamp:
            thumb_path = get_default_thumbnail(link)
            if thumb_path:
                await update.message.reply_photo(photo=open(thumb_path, "rb"), caption="Default Thumbnail")
            else:
                await update.message.reply_text("No thumbnail found.")
        else:
            temp_file = download_video(link, 360)
            safe_name = f"thumb_{timestamp.replace(':','-')}.jpg"
            thumb_path = extract_thumbnail(temp_file, timestamp, out_name=safe_name)
            await update.message.reply_photo(photo=open(thumb_path, "rb"), caption=f"Thumbnail at {timestamp}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /download <YouTube_Link>")
        return ConversationHandler.END

    link = context.args[0]
    user_links[update.effective_chat.id] = {"link": link, "quality": None}
    await update.message.reply_text("Enter quality (360, 480, 720, 1080):")
    return ASK_QUALITY

async def ask_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    quality = update.message.text.strip()
    if chat_id not in user_links:
        await update.message.reply_text("No link found. Start again with /download <link>")
        return ConversationHandler.END

    user_links[chat_id]["quality"] = quality
    link = user_links[chat_id]["link"]

    try:
        await update.message.reply_text(f"Downloading video in {quality}p... Please wait!")
        file_path = download_video(link, quality)

        if os.path.getsize(file_path) < 50 * 1024 * 1024:
            await update.message.reply_video(video=open(file_path, "rb"))
        else:
            await update.message.reply_text("File too large for Telegram. Saved locally in 'downloads/' folder.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# -------------------------------- Terminal Mode ----------------------------------------

def download_from_terminal():
    global last_download
    link = input("Enter YouTube link: ")
    quality = input("Enter quality (360 / 480 / 720 / 1080): ")
    try:
        last_download = {"link": link, "quality": quality}
        file_path = download_video(link, quality)
        print(f"Download complete! File saved at: {file_path}")

        choice = input("Thumbnail? (1=Default, 2=Custom Timestamp, 3=Skip): ")
        if choice == "1":
            thumb_path = get_default_thumbnail(link)
            print(f"Default thumbnail saved at: {thumb_path}")
        elif choice == "2":
            ts = input("Enter timestamp (in seconds or HH:MM:SS): ")
            safe_name = f"thumb_{ts.replace(':','-')}.jpg"
            thumb_path = extract_thumbnail(file_path, ts, out_name=safe_name)
            print(f"Custom thumbnail saved at: {thumb_path}")
        else:
            print("Skipped thumbnail.")
    except Exception as e:
        print(f"Error: {str(e)}")

# -------------------------------- MAIN Function ----------------------------------------

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("download", download_command)],
        states={
            ASK_QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_quality)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("formats", formats))
    app.add_handler(CommandHandler("thumbnail", thumbnail_command))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    choice = input("Run mode? (1=Telegram Bot, 2=Terminal Downloader): ")
    if choice == "1":
        main()
    elif choice == "2":
        download_from_terminal()
