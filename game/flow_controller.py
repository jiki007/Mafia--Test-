from game.game_engine import GameEngine
from game.mafia import Mafia
from game.detective import Detective
from game.doctor import Doctor
from game.civilian import Civilian
from bot.message_templates import*
from game.phase_handler import PhaseHandler
from game.vote_manager import VoteManager
from bot.telegram_bot import finish_voting,start_night_phase,voted_players
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import random,asyncio

game_engine = GameEngine()
phase_handler = PhaseHandler()
vote_manager = VoteManager()
#/beging Here Game Starts
async def begin_game(chat_id, context):
    players = list(game_engine.players)
    game_engine.players = players
    random.shuffle(players)

    # Assign roles
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
            await context.bot.send_message(chat_id=chat_id, text=PRIVATE_MESSAGE_FAIL.format(username=player.username))

    await context.bot.send_message(chat_id=chat_id, text=GAME_STARTED)
    print("Game started and roles assigned.")
    
    # Start the first night phase
    await start_night_phase(chat_id, context)




#starting of day automaticaly
async def start_day_phase(chat_id, context):
    phase_handler.set_phase("day")
    await context.bot.send_message(chat_id=chat_id, text=DAY_START)

    vote_manager.clear_votes()
    voted_players.clear()

    for voter in game_engine.players:
        if not voter.alive:
            continue

        keyboard = []
        for target in game_engine.players:
            if target.alive and target.user_id != voter.user_id:
                keyboard.append([InlineKeyboardButton(f"{target.username}", callback_data=f"vote_{voter.user_id}_{target.user_id}")])

        if not keyboard:
            continue

        try:
            await context.bot.send_message(
                chat_id=voter.user_id,
                text="🗳️ Choose someone to vote out:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Couldn't DM @{voter.username}")

    await asyncio.sleep(40)
    await finish_voting(context)
