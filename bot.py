from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import yt_dlp
import requests
import os

BOT_TOKEN = "8700106612:AAFCYdyO7wnrhYFKROm3qmaxlzARvuoqGiA"

videos = []
user_index = {}
USED_FILE = "used.txt"

# 📁 Create used file
if not os.path.exists(USED_FILE):
    open(USED_FILE, "w").close()

def is_used(video_id):
    with open(USED_FILE, "r") as f:
        return video_id in f.read()

def save_used(video_id):
    with open(USED_FILE, "a") as f:
        f.write(video_id + "\n")

# 🔍 AUTO FETCH YouTube Shorts
def fetch_videos():
    global videos
    url = "https://www.youtube.com/feed/trending"
    html = requests.get(url).text

    vids = []
    parts = html.split("shorts/")

    for p in parts[1:]:
        vid = p.split('"')[0]

        if not is_used(vid):
            vids.append(f"https://www.youtube.com/shorts/{vid}")
            save_used(vid)

    videos = vids[:20]  # store 20 videos

# ⬇️ Download video
def download(url):
    ydl_opts = {
        'outtmpl': 'video.mp4',
        'format': 'mp4',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 📤 Send video
def send_video(update, context: CallbackContext, user_id):
    if not videos:
        fetch_videos()

    index = user_index.get(user_id, 0)

    if index >= len(videos):
        user_index[user_id] = 0
        index = 0

    url = videos[index]

    try:
        download(url)

        keyboard = [[InlineKeyboardButton("▶️ Next", callback_data="next")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open("video.mp4", "rb") as vid:
            context.bot.send_video(
                chat_id=user_id,
                video=vid,
                caption="🔥 Viral Feed\n👉 Your Link",
                reply_markup=reply_markup
            )

        os.remove("video.mp4")

    except Exception as e:
        print("Error:", e)

# ▶️ Start
def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_index[user_id] = 0
    fetch_videos()
    send_video(update, context, user_id)

# ▶️ Next
def next_video(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.message.chat_id
    user_index[user_id] += 1

    send_video(update, context, user_id)

# 🚀 Run
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(next_video, pattern="next"))

    print("🔥 Auto Feed Bot Running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
