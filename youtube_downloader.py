import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

TOKEN = "8143416167:AAHDdruKVUgmfzTkDefwKQTa1OLVfUqI-OM"

ASK_QUALITY = 1
user_links = {}

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

# ----------------------------- Telegram Bot Functions -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " Welcome!\n\nCommands:\n"
        "/download <YouTube_Link> → Download a video\n"
        "/resume → Resume last download\n"
        "/formats <YouTube_Link> → Show available qualities\n"
        "/cancel → Cancel current action"
    )

async def formats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a YouTube link.\nExample: /formats https://youtu.be/abc123")
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

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a YouTube link.\nExample: /download https://youtu.be/abc123")
        return ConversationHandler.END

    link = context.args[0]
    user_links[update.effective_chat.id] = {"link": link, "quality": None}
    await update.message.reply_text("Quality you want (360, 480, 720, 1080):")
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

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_links or not user_links[chat_id].get("link") or not user_links[chat_id].get("quality"):
        await update.message.reply_text("No previous download found. Use /download <link> first.")
        return

    link = user_links[chat_id]["link"]
    quality = user_links[chat_id]["quality"]

    try:
        await update.message.reply_text(f"Resuming download ({quality}p)... Please wait!")
        file_path = download_video(link, quality)

        if os.path.getsize(file_path) < 50 * 1024 * 1024:
            await update.message.reply_video(video=open(file_path, "rb"))
        else:
            await update.message.reply_text("File too large for Telegram. Saved locally in 'downloads/' folder.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# -------------------------------- MAIN Function ----------------------------------------

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("download", download_command)],
        states={ASK_QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_quality)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("formats", formats))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()


# ------------------------------- Terminal Mode -------------------------------------------------

last_download = {"link": None, "quality": None}

def download_from_terminal():
    global last_download
    link = input("Enter YouTube link: ")
    quality = input("Enter quality (360 / 480 / 720 / 1080): ")
    try:
        last_download = {"link": link, "quality": quality}
        file_path = download_video(link, quality)
        print(f"Download complete! File saved at: {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

def resume_from_terminal():
    if not last_download["link"] or not last_download["quality"]:
        print("No previous download found. Run a new download first.")
        return
    try:
        print(f"Resuming download ({last_download['quality']}p)... Please wait!")
        file_path = download_video(last_download["link"], last_download["quality"])
        print(f"Resume complete! File saved at: {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    choice = input("Run mode? (1=Telegram Bot, 2=Terminal Downloader): ")
    if choice == "1":
        main()
    elif choice == "2":
        download_from_terminal()
