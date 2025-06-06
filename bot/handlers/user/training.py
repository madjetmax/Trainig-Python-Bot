import datetime
from zoneinfo import ZoneInfo
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import *

from database.models import User, FinishedUserTraining
import database as db
from keyboards.user import training as kbs
from scheduler import user as schedule_manager

from texts import user as texts
from states import user as states
from training_timer import Timer

router = Router()


# *training

# get training data: status, time, etc
@router.message(Command(commands=["training_status"]))
async def get_training_status(message: Message, state: FSMContext):
    user_data = message.from_user
    state_data = await state.get_data()

    if state_data.get("training_state"): # check if state is UserTraining and not other like UserSetUp

        text, kb = kbs.get_training_control(state_data)

        await message.answer(text, reply_markup=kb)
    else:
        await message.answer(texts.start_training)

# get rep or break timer if somehow message with it was deleted
@router.message(Command(commands=["rep"]))
async def get_current_rep(message: Message, state: FSMContext):
    user_data = message.from_user
    state_data = await state.get_data()
    
    # all reps 
    training_data = state_data.get("full_training_data")
    if training_data == None: # check if state is UserTraining and not other like UserSetUp
        await message.answer(texts.start_training)
        return

    if state_data["stopped"]:
        return

    # get and update prep ind
    current_rep_ind = state_data.get("current_rep_ind")

    # get rep data on ind
    all_reps = training_data["reps"]

    rep_data = all_reps[current_rep_ind-1]
    rep_name = rep_data["name"]

    current_training_state = state_data["training_state"]

    # checking what send based on current training state
    if current_training_state == "break":
        timer: Timer = state_data["timer"]        
        minutes, seconds = timer.get_clear_time()

        text = f"Break, {minutes}:{seconds} left"
        msg = await message.answer(text)

        await state.update_data(
            message=msg # setting new message for udpdate and delete
        )

    elif current_training_state == "warmup":
        timer: Timer = state_data["timer"]        
        minutes, seconds = timer.get_clear_time()

        text = f"Warm Up, {minutes}:{seconds} left"
        msg = await message.answer(text)

        # update state
        await state.update_data(
            message=msg # setting new message for udpdate and delete
        )

    else:
        kb = kbs.get_break()
        text = f"Current rep: {rep_name}"
        msg = await message.answer(text, reply_markup=kb)

        # update state
        await state.update_data(
            message=msg, # setting new message for udpdate and delete
        )
# get user reps in current training
def get_all_reps_text(state_data: dict) -> str:
    text = ""
    reps = state_data["full_training_data"]["reps"]
    current_rep_ind = state_data["current_rep_ind"]

    for i, rep in enumerate(reps, 1):
        if rep["name"] == "break":
            minutes, seconds = get_clear_minites_and_seconds(rep["minutes"], rep["seconds"])
            rep_text = f"Break, {minutes}:{seconds}"
        else:
            rep_text = rep["name"]
        
        # mark if done
        if i < current_rep_ind:
            rep_text = "✅ " + rep_text
        
        # mark if current
        if i == current_rep_ind:
            rep_text = "Current: " + rep_text
        text += rep_text + "\n"
    return text


@router.message(Command(commands=["reps"]))
async def get_training_reps(message: Message, state: FSMContext):
    user_data = message.from_user
    state_data = await state.get_data()

    # all reps 
    training_data = state_data.get("full_training_data")
    if training_data == None: # check if state is UserTraining and not other like UserSetUp
        await message.answer(texts.start_training)
        return
    
    text = get_all_reps_text(state_data)

    await message.answer(text)

# like help commands for handlers
def get_clear_time(hours, minutes, seconds) -> str:

    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)

    return f"{hours}:{minutes}.{seconds}"

def get_clear_minites_and_seconds(minutes, seconds) -> tuple[str, str]:
    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)

    return minutes, seconds
# get text from data from database
def get_training_result(f_t: FinishedUserTraining) -> str:
    """Takes :code:`f_t` to get data from it, returns text as :class:`str`"""
    time_start: datetime = f_t.time_start
    time_end: datetime = f_t.time_end

    tz = ZoneInfo(DATETIME_TIME_ZONE)
    now = datetime.datetime.now(tz)

    # get clear time start
    start_hours = time_start.time().hour
    start_minutes = time_start.time().minute
    start_seconds = time_start.time().second

    clear_time_start = get_clear_time(start_hours, start_minutes, start_seconds)

    # get clear time end
    end_hours = time_end.time().hour
    end_minutes = time_end.time().minute
    end_seconds = time_end.time().second

    clear_time_end = get_clear_time(end_hours, end_minutes, end_seconds)

    # calculatin training time
    
    
    training_hours = f_t.full_training_time.split(":")[0]
    training_minutes = f_t.full_training_time.split(":")[1].split(".")[0]
    training_seconds = f_t.full_training_time.split(":")[1].split(".")[1]
    
    clear_training_time = get_clear_time(training_hours, training_minutes, training_seconds)

    # calculating finished reps        
    reps_finished = f_t.reps_finished
    all_reps = f_t.all_reps_count

    # getting data in format dd-mm-yy
    date = f_t.time_start.date()
    # getting body_part
    body_part = f_t.full_training_data["selected_part"]

    aura_got = 10 / (all_reps - reps_finished + 1) * (all_reps / 10) # aura based on finished and all reps count. PS maybe I will change it

    text = f"""
ID: {f_t.id}
Date: {date}
Body part: {body_part}\n
started at: {clear_time_start}
end at: {clear_time_end}
training time: {clear_training_time}\n
finished reps: {reps_finished}
reps all: {all_reps}\n
aura got: {aura_got}
    """

    return text

# get list of user funished trainings
@router.message(Command(commands=["f_t"])) # todo test command
async def get_finished_trainings(message: Message):
    user_data = message.from_user

    user = await db.get_user(user_data.id)

    if user:
        offset = 5
        finished_trainings = user.finished_trainings[:offset]
        for i, f_t in enumerate(finished_trainings):
            kb = None
            if i + 1 == len(finished_trainings) and i + 1 < len(user.finished_trainings):
                start = offset
                kb = await kbs.get_add_more_f_t(start, offset)
            text = get_training_result(f_t)
            await message.answer(text, reply_markup=kb)
