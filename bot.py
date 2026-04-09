from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8700106612:AAFCYdyO7wnrhYFKROm3qmaxlzARvuoqGiA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🔥 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
