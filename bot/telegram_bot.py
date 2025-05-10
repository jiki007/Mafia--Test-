from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

#Defining the bot
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

#Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to Mafia Bot.")

#Commands
app.add_handler(CommandHandler("start",start))

