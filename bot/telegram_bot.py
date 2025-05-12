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
    phase_handler.set_phase("night")

    #Background waiting for 40 secs before starting the game
    context.application.create_task(wait_and_start_game(chat_id,context))

#backgroudn waiting for 40 secs
async def wait_and_start_game(chat_id, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=chat_id, text="40 seconds before game starts")
    await asyncio.sleep(20)
    await context.bot.send_message(chat_id=chat_id, text="20 seconds before game starts")
    await asyncio.sleep(10)
    await context.bot.send_message(chat_id=chat_id, text="10 seconds before game starts")
    await asyncio.sleep(10)

    #Final list of all players who joined
    if player_list:
        joined_names = "\n".join(f"@{p.username}" for p in player_list.values())
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Players who joined: \n{joined_names}"
        )

    #Deleting the join message wiht the button
    try:
        await context.bot.delete_message(
            chat_id=join_message_info["chat_id"],
            message_id=join_message_info["message_id"]
        )
    except:
        pass

    if len(player_list) < 4:
        await context.bot.send_message(chat_id=chat_id, text="Not enough players. Need at least 5 players to start a game!")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Enough players joined! type /begin to start the game!")

#/join
async def handle_join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        # Immediately acknowledge the button press
        await query.answer("Processing...")
        
        user = query.from_user
        user_id = user.id
        username = user.username or user.full_name
        print(f"DEBUG: Join button pressed by {username} (ID: {user_id})")  # Debug log

        # Check if user already joined
        if user_id in player_list:
            print(f"DEBUG: User {username} already in game")  # Debug log
            await query.answer("You already joined!")
            return

        # Check player limit
        if len(player_list) >= MAX_PLAYERS:
            print("DEBUG: Player limit reached")  # Debug log
            await query.answer("🚫 Player limit reached!")
            return

        # Add new player
        player = Player(user_id, username)
        player_list[user_id] = player
        print(f"DEBUG: Added {username} to player_list")  # Debug log

        # Verify join_message_info is set
        if not join_message_info.get("chat_id") or not join_message_info.get("message_id"):
            print("ERROR: join_message_info not properly set!")
            await query.answer("Game setup error. Please try again.")
            return

        # Update the join message
        joined_names = "\n".join(f"• {p.username}" for p in player_list.values())
        new_text = f"🎮 Game starting! Waiting for players...\n\n👥 Joined Players:\n{joined_names}"
        
        print(f"DEBUG: Attempting to edit message {join_message_info['message_id']}")  # Debug log
        await context.bot.edit_message_text(
            chat_id=join_message_info["chat_id"],
            message_id=join_message_info["message_id"],
            text=new_text,
            reply_markup=query.message.reply_markup
        )
        print("DEBUG: Message edited successfully")  # Debug log

        await query.answer(f"✅ {username} joined the game!")
        
    except Exception as e:
        print(f"ERROR in handle_join_button: {str(e)}")  # Detailed error logging
        await query.answer("❌ Failed to join. Please try again.")


#/beging Here Game Starts
async def begin(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if len(player_list) < 4:
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

    #Sends buttons to all players who can act at night
    for player in player_list.values():
        if player.alive:
            await send_night_action_buttons(context, player)
    

#Sending actions privaately
async def send_night_action_buttons(context,player):
    if not hasattr(player.role, "night_action"):
        return
    
    #Role specific action promt
    if player.role.name == "Mafia":
        promt = " Choose someone to KILL: "
    elif player.role.name == "Doctor":
        promt = "Choose someone to SAVE: "
    elif player.role.name == "Detective":
        promt = " Choose someone to INVESTIGATE "
    else:
        return

    keyboard = []
    for p in player_list.values():
        if p.alive and p.user_id != player.user_id:
            keyboard.append([
                InlineKeyboardButton(f"Target {p.username}", callback_data=f"night_{player.user_id}_{p.user_id}")
            ])

    markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_message(
            chat_id = player.user_id,
            text = promt,
            reply_markup = markup
        )
    except Exception as e:
        log(f"❌ Could not send night action to {player.username}: {e}")

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


#/endgame 
async def endgame(update:Update, context:ContextTypes.DEFAULT_TYPE):
    #No game avalialbe
    if not player_list:
        await update.message.reply_text("No game is currently in progress.")
        return
    
    await update.message.reply_text("The game is ending immediately:")

    winner = game_engine.check_win_condition()
    if winner:
        await update.message.reply_text(WIN_MESSAGE.format(team=winner))
    else:
        await update.message.reply_text("No winners!")

    #Notifying all members
    for player in player_list.values():
        try:
            await context.bot.send_message(
                chat_id=player.user_id,
                text="The game has ended! Thank you for playing."
            )
        except Exception as e:
            log(f"Could not notify {player.username}: {e}")

    player_list.clear()
    phase_handler.set_phase(None)
    vote_manager.clear_votes()

    log("Game has been ended!")


# Command Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startgame", startgame))
app.add_handler(CommandHandler("endgame", endgame))
app.add_handler(CommandHandler("endnight", endnight))
app.add_handler(CommandHandler("endday", endday))



# Butto Handlers
app.add_handler(CallbackQueryHandler(handle_join_button, pattern="^join_game$"))

