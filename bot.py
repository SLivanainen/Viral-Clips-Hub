from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import yt_dlp
import requests
import os

BOT_TOKEN = "8700106612:AAFCYdyO7wnrhYFKROm3qmaxlzARvuoqGiA"

videos = []
user_index = {}

# Fetch videos
def fetch_videos():
    global videos
    url = "https://www.youtube.com/feed/trending"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

    vids = []
    parts = html.split("shorts/")

    for p in parts[1:]:
        vid = p.split('"')[0]
        vids.append(f"https://www.youtube.com/shorts/{vid}")

    videos = vids[:20]

# Download
def download(url):
    ydl_opts = {'outtmpl': 'video.mp4', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Send video
async def send_video(update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not videos:
        fetch_videos()

    index = user_index.get(user_id, 0)

    if index >= len(videos):
        user_index[user_id] = 0
        index = 0

    url = videos[index]
    download(url)

    keyboard = [[InlineKeyboardButton("▶️ Next", callback_data="next")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("video.mp4", "rb") as vid:
        await context.bot.send_video(
            chat_id=user_id,
            video=vid,
            caption="🔥 Viral Feed\n👉 Your Link",
            reply_markup=reply_markup
        )

    os.remove("video.mp4")

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_index[user_id] = 0
    fetch_videos()
    await send_video(update, context, user_id)

# Next
async def next_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat_id
    user_index[user_id] += 1

    await send_video(update, context, user_id)

# Run
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(next_video, pattern="next"))

    print("🔥 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
