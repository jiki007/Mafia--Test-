from telegram import InlineKeyboardButton, InlineKeyboardMarkup,Update
from telegram.ext import CallbackQueryHandler, ApplicationBuilder, CommandHandler, ContextTypes
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
import random,asyncio

# Bot setup
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

# Globals
join_message_info = {
    "chat_id":None,
    "message_id":None

}
player_list = {}  # user_id: Player
MAX_PLAYERS = 10

game_engine = GameEngine()
phase_handler = PhaseHandler()
vote_manager = VoteManager()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to Mafia Bot.")

# /startgame
async def startgame(update:Update, context: ContextTypes.DEFAULT_TYPE):
    player_list.clear() #clears any previous session
    chat_id = update.effective_chat.id

    keyboard = [[InlineKeyboardButton("Join", callback_data="join_game")]]    
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await context.bot.send_message(
        chat_id = chat_id,
        text = "Game starting ! Waiting for players.....\n\n Joined Players:\n",
        reply_markup=reply_markup
    )

    
    join_message_info["chat_id"] = message.chat_id
    join_message_info["message_id"] = message.message_id
    phase_handler.set_phase("lobby")

    #waiting for 40 seconds before starting the game
    await asyncio.sleep(40)

    #Final list of all players who joined
    if player_list:
        joined_names = "\n".join(f"@{p.username}" for p in player_list.values())
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Players who joined: \n{joined_names}"
        )


    #Deleting button and list after time is up 40secs

    try:
        await context.bot.delete_message(
            chat_id=join_message_info['chat_id'],
            message_id=join_message_info["message_id"]
        )
    except:
        pass

    if len(player_list) < 5:
        await context.bot.send_message(chat_id=chat_id, text="Not enoguh players. Need at least 5 people to start!")
    else:
        await context.bot.send_message(chat_id=chat_id, text="✅ Enough players joined!\nUse /begin to start the game.")


#/join
async def handle_join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_id = user.id
    username = user.username or user.full_name

    try:
        if user_id in player_list:
            await query.answer("You already joined.")
            return
        if len(player_list) >= MAX_PLAYERS:
            await query.answer("Player limit reached")
            return
    
        player = Player(user_id, username)
        player_list[user_id] = player
        log(f"@{username} joined the game.")

        joined_names = "\n".join(f"• {p.username}" for p in player_list.values())
        new_text = f"🎮 Game starting! Waiting for players...\n\n👥 Joined Players:\n{joined_names}"

        await context.bot.edit_message_text(
            chat_id = join_message_info["chat_id"],
            message_id = join_message_info["message_id"],
            text = new_text,
            reply_markup = query.message.reply_markup
        )

        await query.answer("You joined the game.")
    
    except Exception as e:
        print(f"[ERROR] Failed to procces join: {e}")
        await query.answer("Something went wrong. Please try again!")



#/beging Here Game Starts
async def begin(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if len(player_list) < 5:
        await update.message.reply_text("Nedd at least 5 players to start game")
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
    phase_handler.set_phase("night")
    await update.message.reply_text(NIGHT_START)
    

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

     #Counting remaining roles
    mafia_count = sum(1 for p in player_list.values() if p.alive and p.role.name == "Mafia")
    doctor_count = sum(1 for p in player_list.values() if p.alive and p.role.name == "Doctor")
    detective_count = sum(1 for p in player_list.values() if p.alive and p.role.name == "Detective")
    civilian_count = sum(1 for p in player_list.values() if p.alive and p.role.name == "Civilian")


    #List as a message
    status_message = (
    "📊 Players Remaining:\n"
    f"• 🕵️ Mafia: {mafia_count}\n"
    f"• 🧑 Civilians: {civilian_count}\n"
    f"• 🩺 Doctor: {doctor_count}\n"
    f"• 🔍 Detective: {detective_count}"
    )

    await update.message.reply_text(status_message)
  

    winner = game_engine.check_win_condition()
    if winner:
        await update.message.reply_text(WIN_MESSAGE.format(team=winner))
        return
    
   
  
    phase_handler.set_phase("day")
    await update.message.reply_text(DAY_START)


# /endday
async def endday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not phase_handler.is_day():
        await update.message.reply_text("It's not daytime!")
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
                InlineKeyboardButton(f"Target {p.username}",callback_data=f"night_{user_id}_{p.user_id}")
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
app.add_handler(CallbackQueryHandler(handle_join_button, pattern="^join_game$"))
app.add_handler(CommandHandler("startgame", startgame))
app.add_handler(CommandHandler("action", action))
app.add_handler(CommandHandler("endnight", endnight))
app.add_handler(CommandHandler("vote", vote))
app.add_handler(CommandHandler("endday", endday))
app.add_handler(CommandHandler("actionbuttons", actionbuttons))
app.add_handler(CallbackQueryHandler(handle_night_action_button))
app.add_handler(CommandHandler("begin", begin))

