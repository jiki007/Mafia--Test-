from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from game.player import Player
import random
from game.game_engine import GameEngine
from game.phase_handler import PhaseHandler


#Defining the bot
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

#List of players
player_list = {} # key: user_id, value: Player object
MAX_PLAYERS = 10

#Global instances
game_engine = GameEngine()
phase_handler = PhaseHandler()

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

async def action(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = player_list.get(user_id)

    if not player:
        await update.message.reply_text("You are not in the game.")
        return
    
    if not phase_handler.is_night():
        await update.message.reply_text("You can only act at night.")
        return
    if not hasattr(player.role, "night_action"):
        await update.message.reply_text("You have no night action.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /action <username>")
        return
    
    target_name = context.args[0]
    for p in player_list.values():
        if p.username == target_name and p.alive:
            target = p
            break
    
    if not target:
        await update.message.reply_text("Invalid or dead target.")

    #Calling nihgt actions
    player.role.night_action(game_engine, player, target)
    await update.message.reply_text(f"You targeted {target.username}.")

async def endnight(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not phase_handler.is_night():
        await update.message.reply_text("It is not night time!")
        return

    #End of the night
    killed = game_engine.resolve_night()

    message = ""
    if killed:
        message += f"Night is over.\n {killed} was killed during the previous night."
    else:
        message += "Night is over.\n No one died tonight!"
    
    #Setting phase to day
    phase_handler.set_phase("day")

    await update,message.reply_text(message)
    

#Command Handlers
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("join",join))
app.add_handler(CommandHandler("action",action))
app.add_handler(CommandHandler("endnight",endnight))

