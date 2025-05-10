from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from game.player import Player
from game.game_engine import GameEngine
from game.phase_handler import PhaseHandler
from game.vote_manager import VoteManager
from game.mafia import Mafia
from game.detective import Detective
from game.doctor import Doctor
from game.civilian import Civilian
from bot.message_templates import *
from game.logger import log
import random

# Bot setup
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

# Globals
player_list = {}  # user_id: Player
MAX_PLAYERS = 10

game_engine = GameEngine()
phase_handler = PhaseHandler()
vote_manager = VoteManager()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to Mafia Bot.")

# /join
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.full_name

    if user_id in player_list:
        await update.message.reply_text(ALREADY_JOINED.format(username=username))
    elif len(player_list) >= MAX_PLAYERS:
        await update.message.reply_text(PLAYER_LIMIT)
    else:
        player = Player(user_id, username)
        player_list[user_id] = player
        await update.message.reply_text(JOIN_SUCCESS.format(username=username, count=len(player_list), max=MAX_PLAYERS))
        log(f"{username} joined the game.")

# /startgame
async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(player_list) < 5:
        await update.message.reply_text("Need at least 5 players to start the game!")
        return

    players = list(player_list.values())
    random.shuffle(players)

    players[0].assign_role(Mafia())
    players[1].assign_role(Detective())
    players[2].assign_role(Doctor())
    for player in players[3:]:
        player.assign_role(Civilian())

    for player in players:
        try:
            await context.bot.send_message(
                chat_id=player.user_id,
                text=ROLE_ANNOUNCEMENT.format(role=player.role.name, description=player.role.description())
            )
        except:
            await update.message.reply_text(PRIVATE_MESSAGE_FAIL.format(username=player.username))

    await update.message.reply_text(GAME_STARTED)
    log("Game started and roles assigned.")

# /action
async def action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = player_list.get(user_id)

    if not player:
        await update.message.reply_text(NOT_IN_GAME)
        return
    if not phase_handler.is_night():
        await update.message.reply_text(NIGHT_ONLY_ACTION)
        return
    if not hasattr(player.role, "night_action"):
        await update.message.reply_text(NO_NIGHT_ACTION)
        return
    if not context.args:
        await update.message.reply_text(INVALID_ACTION_FORMAT)
        return

    target_name = context.args[0]
    target = next((p for p in player_list.values() if p.username == target_name and p.alive), None)

    if not target:
        await update.message.reply_text(INVALID_TARGET)
        return

    player.role.night_action(game_engine, player, target)
    await update.message.reply_text(f"You targeted {target.username}.")
    log(f"{player.username} used action on {target.username}.")

# /endnight
async def endnight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not phase_handler.is_night():
        await update.message.reply_text("It's not night time!")
        return

    killed = game_engine.resolve_night()
    message = NIGHT_END_KILL.format(name=killed) if killed else NIGHT_END_SAFE
    await update.message.reply_text(message)

    winner = game_engine.check_win_condition()
    if winner:
        await update.message.reply_text(WIN_MESSAGE.format(team=winner))
        return

    phase_handler.set_phase("day")
    await update.message.reply_text(DAY_START)

# /vote
async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not phase_handler.is_day():
        await update.message.reply_text(NOT_DAYTIME)
        return

    voter = player_list.get(update.effective_user.id)
    if not voter or not voter.alive:
        await update.message.reply_text(NOT_ALLOWED_TO_VOTE)
        return

    if not context.args:
        await update.message.reply_text(INVALID_VOTE_FORMAT)
        return

    target_name = context.args[0]
    target = next((p for p in player_list.values() if p.username == target_name and p.alive), None)

    if not target:
        await update.message.reply_text(INVALID_TARGET)
        return

    vote_manager.cast_vote(voter.user_id, target.user_id)
    await update.message.reply_text(VOTE_CONFIRM.format(target=target.username))
    log(f"{voter.username} voted for {target.username}.")

# /endday
async def endday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not phase_handler.is_day():
        await update.message.reply_text(NOT_DAYTIME)
        return

    target_id = vote_manager.get_vote_result()
    if not target_id:
        await update.message.reply_text(NO_VOTES)
    else:
        target = player_list.get(target_id)
        if target and target.alive:
            target.eliminate()
            await update.message.reply_text(VOTE_RESULT.format(name=target.username))
            log(f"{target.username} was eliminated by vote.")
        else:
            await update.message.reply_text("The voted player was already dead or invalid.")

    winner = game_engine.check_win_condition()
    if winner:
        await update.message.reply_text(WIN_MESSAGE.format(team=winner))
        return

    vote_manager.clear_votes()
    phase_handler.set_phase("night")
    await update.message.reply_text(NIGHT_START)

#buttons
async def actionbuttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = player_list.get(user_id)

    if not player:
        await update.message.reply_text(NOT_IN_GAME)
        return
    
    if not phase_handler.is_night():
        await update.message.reply_text(NIGHT_ONLY_ACTION)
        return
    
    if not hasattr(player.role, "night_action"):
        await update.message.reply_text(NO_NIGHT_ACTION)
        return
    
    keyboard = []
    for p in player_list.values():
        if p.alive and p.user_id != user_id:
            keyboard.append([
                InlineKeyboardButton(f"Target {p.usernmae}",callback_data=f"night_{user_id}_{p.user_id}")
            ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌙 Choose your target:", reply_markup=reply_markup)

async def handle_night_action_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("night_"):
        return
    
    actor_id, target_id = map(int, data.split("_")[1:])

    actor = player_list.get(actor_id)
    target = player_list.get(target_id)

    if not actor or not actor.alive or not target or not target.alive:
        await query.edit_message_text("Invalid action")
        return
    
    actor.role.night_action(game_engine,actor,target)
    await query.edit_message_text(f"✅ You targeted {target.username}.")
    log(f"{actor.username} ({actor.role.name}) targeted {target.username}.")


# Command Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("startgame", startgame))
app.add_handler(CommandHandler("action", action))
app.add_handler(CommandHandler("endnight", endnight))
app.add_handler(CommandHandler("vote", vote))
app.add_handler(CommandHandler("endday", endday))
app.add_handler(CommandHandler("actionbuttons", actionbuttons))
app.add_handler(CallbackQueryHandler(handle_night_action_button))
