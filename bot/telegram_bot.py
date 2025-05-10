from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from game.player import Player
import random

#Defining the bot
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

#List of players
player_list = {} # key: user_id, value: Player object
MAX_PLAYERS = 10

#Roles
ROLES = ['Mafia','Detective','Doctor']



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


async def startgame(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if len(player_list) < 5:
        await update.message.reply_text("Need at least 5 players to start the game!")
        return
    
    players = list(player_list.values())
    random.shuffle(players)

    #Assigning roles
    players[0].assign_role('Mafia')
    players[1].assign_role('Detective')
    players[2].assign_role('Doctor')

    #Others are civilians
    for player in players[3:]:
        player.assign_role('Civilian')

    #Notifying players privately
    for player in players:
        try:
            await context.bot.send_message(chat_id=player.user_id, text=f"Your role is: {player.role} 🤫🤫🤫")
        except:
            await update.message.reply_text(f"Could not message {player.username}. They must message the bpt first!")

    await update.meesage.reply_text("Game has started! All roles have been assigned.")

#Command Handlers
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("join",join))
app.add_handler(CommandHandler("startgame",startgame))

