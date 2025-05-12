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
from game.flow_controller import begin_game, start_day_phase


# Bot setup
app = ApplicationBuilder().token("7490724483:AAEy3khPwbQ_U0BQgS65gcn15TptOgRz-Nc").build()

# Globals
join_message_info = {
    "chat_id":None,
    "message_id":None

}
player_list = {}  # user_id: Player
voted_players = set()
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
        joined_names = "\n".join(f"@{p.username}" for p in game_engine.players)
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

    if len(player_list) < 3:
        await context.bot.send_message(chat_id=chat_id, text="Not enough players. Need at least 5 players to start a game!")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Enough players joined!\n Starting the game....")
        await begin_game(chat_id,context)
        
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
        joined_names = "\n".join(f"• {p.username}" for p in game_engine.players)
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



#start night automaticaly
async def start_night_phase(chat_id, context):
    phase_handler.set_phase("night")
    await context.bot.send_message(chat_id=chat_id, text=NIGHT_START)

    for player in game_engine.players:
        if player.alive and hasattr(player.role, "night_action"):
            await send_night_action_buttons(context, player)

    await asyncio.sleep(40)
    await end_night_phase(chat_id, context)


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
    for p in game_engine.players:
        if p.alive and p.user_id != player.user_id:
            keyboard.append([
                InlineKeyboardButton(f"{p.username}", callback_data=f"night_{player.user_id}_{p.user_id}")
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
    

#vote_timer
async def vote_timer(context):
    await context.bot.send_message(
            chat_id=join_message_info["chat_id"],
            text="You have 40 seconds to vote"
        )
    await asyncio.sleep(30)
    await context.bot.send_message(
            chat_id=join_message_info["chat_id"],
            text="You have 10 seconds to vote"
        )
    await asyncio.sleep(10)

    # If not all voted, resolve with current votes
    alive_count = sum(1 for p in game_engine.players if p.alive)
    if len(voted_players) < alive_count:
        await context.bot.send_message(
            chat_id=join_message_info["chat_id"],
            text="⏰ Voting time is over. Resolving votes..."
        )
        await finish_voting(context)




#Handling vote button
async def handle_vote_button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if not data.startswith("vote_"):
        return
    
    voter_id, target_id = map(int,data.split("_")[1:])
    voter = player_list.get(voter_id)
    target = player_list.get(target_id)

    if voter_id in voted_players:
        await query.edit_message_text("You already voted.")
        return
    
    if not voter or not voter.alive or not target or not target.alive:
        await query.edit_message_text("Invalid vote.")
        return
    
    vote_manager.cast_vote(voter_id, target_id)
    voted_players.add(voter_id)
    await query.edit_message_text(f"You voted for {target.username}.")
    
    alive_count = sum(1 for p in game_engine.players if p.alive)
    if len(voted_players) == alive_count:
        await finish_voting(context)

#/finish_voting
async def finish_voting(context:ContextTypes.DEFAULT_TYPE):
    chat_id = join_message_info['chat_id']
    vote_map = vote_manager.get_vote_map()

    summary = "\n".join(f"@{player_list[v].username} voted for @{player_list[t].username}" for v,t in vote_map.items())

    await context.bot.send_message(chat_id=chat_id, text=f"📊 Voting Summary:\n{summary}")

    result = vote_manager.get_vote_result()
    vote_manager.clear_votes()
    voted_players.clear()

    if result == "tie":
        await context.bot.send_message(chat_id=chat_id, text="It's a tie nobody is eliminated.")
    else:
        target = player_list.get(result)
        if target and target.alive:
            target.eliminate()
            await context.bot.send_message(chat_id=chat_id,text=f"@{target.username} was voted out.\n They were: {target.role.name}.")
   
    # Move to night
    phase_handler.set_phase("night")
    await context.bot.send_message(chat_id=chat_id, text=NIGHT_START)

    for player in game_engine.players:
        if player.alive and hasattr(player.role, "night_action"):
            await send_night_action_buttons(context, player) 

    winner = game_engine.check_win_condition()
    if winner:
        await context.bot.send_message(chat_id=chat_id, text=WIN_MESSAGE.format(team=winner))
        return

    await start_night_phase(chat_id, context)


#Handling night acntion buttons
async def handle_night_action_button(update:Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("night_"):
        return
    
    parts = data.split("_")
    if len(parts) !=3:
        await query.edit_message_text("Invalid button data") 
        return
    
    try:
        actor_id = int(parts[1])
        target_id = int(parts[2])
    except ValueError:
        await query.edit_message_text("Invalid User's ID")
        return
    
    actor = player_list.get(actor_id)
    target = player_list.get(target_id)

    if not actor or not actor.alive or not target or not target.alive:
        await query.edit_message_text(" Invalid or dead target. ")
        return
    
    if hasattr(actor.role, "night_action"):
        actor.role.night_action(game_engine,actor,target)
        await query.edit_message_text(f"You targeted: {target.username}.")
    else:
        await query.edit_message_text(f"You don't have a night action.")

# /endnight
async def end_night_phase(chat_id, context):
    killed_name, investigation = game_engine.resolve_night()

    message = NIGHT_END_KILL.format(name=killed_name) if killed_name else NIGHT_END_SAFE
    await context.bot.send_message(chat_id=chat_id, text=message)

    if investigation:
        detective, target = investigation
        is_mafia = target.role.name == 'Mafia'
        try:
            await context.bot.send_message(
                chat_id=detective.user_id,
                text=f"🔍 You investigated {target.username}. They are {'🕵️ Mafia' if is_mafia else '✅ Not Mafia'}."
            )
        except Exception as e:
            log(f"❌ Could not send investigation result to {detective.username}: {e}")

    await show_remaining_roles(chat_id, context)

    winner = game_engine.check_win_condition()
    if winner:
        await context.bot.send_message(chat_id=chat_id, text=WIN_MESSAGE.format(team=winner))
        return

    await start_day_phase(chat_id, context)


#Remaing roles
async def show_remaining_roles(chat_id, context):
    mafia_count = sum(1 for p in game_engine.players if p.alive and p.role.name == "Mafia")
    doctor_count = sum(1 for p in game_engine.players if p.alive and p.role.name == "Doctor")
    detective_count = sum(1 for p in game_engine.players if p.alive and p.role.name == "Detective")
    civilian_count = sum(1 for p in game_engine.players if p.alive and p.role.name == "Civilian")

    status_message = (
        "📊 Players Remaining:\n"
        f"• 🕵️ Mafia: {mafia_count}\n"
        f"• 🧑 Civilians: {civilian_count}\n"
        f"• 🩺 Doctor: {doctor_count}\n"
        f"• 🔍 Detective: {detective_count}"
    )

    await context.bot.send_message(chat_id=chat_id, text=status_message)


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
    for player in game_engine.players:
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

#Basic Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startgame", startgame))
app.add_handler(CommandHandler("endgame", endgame))  # Optional emergency stop

#Callback Buttons
app.add_handler(CallbackQueryHandler(handle_join_button, pattern="^join_game$"))
app.add_handler(CallbackQueryHandler(handle_vote_button, pattern="^vote_"))
app.add_handler(CallbackQueryHandler(handle_night_action_button, pattern="^night_"))


