from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from game.player import Player

#Defining the bot
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

#List of players
player_list = {} # key: user_id, value: Player object
MAX_PLAYERS = 10

#Command Funcitions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to Mafia Bot.")

async def join(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.full_name

    if user.id in player_list:
        await update.message.reply_text(f"@{username}, you already joined!")
    elif len(player_list) >= MAX_PLAYERS:
        await update.message.reply_text("Player limit reached. You can't join. Please wait until another game starts!")
    else:
        player = Player(user_id,username)
        player_list[user_id] = player
        await update.message.reply_text(f"@{username} joined the game! ({len(player_list)}/{MAX_PLAYERS})")


#Command Handlers
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("join",join))

