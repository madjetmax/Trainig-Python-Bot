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
from utils.training_timer import Timer, timers

router = Router()


# *handlers while training

# get training data: status, time, etc
@router.message(Command("training_status"))
async def get_training_status(message: Message, state: FSMContext):
    user_data = message.from_user
    state_data = await state.get_data()
    user = await db.get_user(user_data.id)
    lang = user.lang

    if state_data.get("training_state"): # check if state is UserTraining and not other like UserSetUp

        text, kb = kbs.get_training_control(state_data, lang)

        await message.answer(text, reply_markup=kb)
    else:
        await message.answer(texts.start_training[lang])

# get rep or break timer if somehow message with it was deleted
@router.message(Command("rep"))
async def get_current_rep(message: Message, state: FSMContext):
    user_data = message.from_user
    state_data = await state.get_data()
    
    user = await db.get_user(user_data.id)
    lang = user.lang

    # all reps 
    training_data = state_data.get("full_training_data")
    if training_data == None: # check if state is UserTraining and not other like UserSetUp
        await message.answer(texts.start_training[lang])
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

    # checking what to send based on current training state
    if current_training_state == "break":
        timer: Timer = timers[state_data["timer"]]        
        minutes, seconds = timer.get_clear_time()

        # get kb and text, send message 
        kb = kbs.get_break_controll(lang)
        text = texts.break_timer_title[lang].format(
            minutes=minutes, seconds=seconds
        )

        msg = await message.answer(text, reply_markup=kb)

        await state.update_data(
            message=msg.message_id # setting new message for udpdate and delete
        )

    elif current_training_state == "warmup":
        timer: Timer = timers[state_data["timer"]]        
        minutes, seconds = timer.get_clear_time()

        # get kb and text, send message 
        kb = kbs.get_break_controll(lang)
        text = texts.warmup_title[lang].format(
            minutes=minutes, seconds=seconds
        )
        
        msg = await message.answer(text, reply_markup=kb)

        # update state
        await state.update_data(
            message=msg.message_id # setting new message for udpdate and delete
        )

    else:
        kb = kbs.get_break(lang)
        # find rep name on user lang in state_data
        for rep in state_data["user_reps_names"]:
            if rep["name"] == rep_name:
                rep_name = rep[lang]
                break

        text = texts.rep_title[lang].format(
            name=rep_name
        )
        msg = await message.answer(text, reply_markup=kb)

        # update state
        await state.update_data(
            message=msg.message_id # setting new message for udpdate and delete
        )
# get user reps in current training
def get_all_reps_text(state_data: dict, lang) -> str:
    text = ""
    reps = state_data["full_training_data"]["reps"]
    current_rep_ind = state_data["current_rep_ind"]

    for i, rep in enumerate(reps, 1):
        if rep["name"] == "break":
            minutes, seconds = get_clear_minites_and_seconds(rep["minutes"], rep["seconds"])
            rep_text = texts.break_title[lang].format(
                minutes=minutes, seconds=seconds
            )
        else:
            rep_text = rep["name"]
            # find rep name on user lang in state_data
            for rep1 in state_data["user_reps_names"]:
                if rep1["name"] == rep_text:
                    rep_text = rep1[lang]
                    break
        
        # mark if done
        if i < current_rep_ind:
            rep_text = "✅ " + rep_text
        
        # mark if current
        if i == current_rep_ind:
            rep_text = texts.curent_rep[lang].format(name=rep_text)
        text += rep_text + "\n"
    return text


@router.message(Command("reps"))
async def get_training_reps(message: Message, state: FSMContext):
    user_data = message.from_user
    state_data = await state.get_data()

    user = await db.get_user(user_data.id)
    lang = user.lang

    # all reps 
    training_data = state_data.get("full_training_data")
    if training_data == None: # check if state is UserTraining and not other like UserSetUp
        await message.answer(texts.start_training[lang])
        return
    
    text = get_all_reps_text(state_data, lang)

    await message.answer(text)

def set_timezone(date: datetime.datetime) -> datetime.datetime:
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    return date.astimezone(tz)

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
def get_training_result(f_t: FinishedUserTraining, lang, user_all_body_parts) -> str:
    """Takes :code:`f_t` to get data from it, returns text as :class:`str`"""
    time_start: datetime = set_timezone(f_t.time_start)
    time_end: datetime = set_timezone(f_t.time_end)

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
    date = time_start.date()
    # getting body_part
    body_part = f_t.full_training_data["selected_part"]

    for part in user_all_body_parts:
        if part["name"] == body_part:
            body_part = part[lang]
            break

    aura_got = f_t.aura_got

    text = texts.finished_training_text[lang].format(
        id=f_t.id,
        date=date,
        body_part=body_part,
        time_start=clear_time_start,
        time_end=clear_time_end,
        training_time=clear_training_time,
        reps_finished=reps_finished,
        all_reps=all_reps,
        aura_got=aura_got,
    )

    return text

def sort_finished_trainings(x: FinishedUserTraining) -> int:
    # getting seconds from datetime to sort
    seconds = x.time_start.timestamp()
    return -seconds

# *get list of user funished trainings
@router.message(Command(commands=["f_t"])) # todo test command
async def get_finished_trainings(message: Message):
    user_data = message.from_user

    user = await db.get_user(user_data.id)

    if user:
        offset = 5
        
        # sort trainins by date
        finished_trainings = sorted(user.finished_trainings[:offset], key=sort_finished_trainings)
        for i, f_t in enumerate(finished_trainings):
            kb = None
            # add keyboard if message is the last
            if i + 1 == len(finished_trainings) and i + 1 < len(user.finished_trainings):
                start = offset
                kb = await kbs.get_add_more_f_t(start, offset, user.lang)
            # send message
            text = get_training_result(f_t, user.lang, user.trainings.all_body_parts)
            await message.answer(text, reply_markup=kb)

# *start training
def check_training_is_done_today(user: User) -> bool:
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    today = datetime.datetime.now(tz)
    today_date = today.date()

    finished_trainings = user.finished_trainings

    for f_t in finished_trainings:
        f_t_date = set_timezone(f_t.time_start).date()
        # check if dates are the same
        if f_t_date == today_date:
            return True
    return False

@router.message(Command("start_training"))
async def start_training(message: Message, state: FSMContext):
    user_data = message.from_user
    chat_id = message.chat.id
    state_data = await state.get_data()

    user = await db.get_user(user_data.id)
    lang = user.lang

    if state_data.get("timer"): # check if user on training
        return 

    done = check_training_is_done_today(user)

    text = texts.on_start_trainin_title[lang]
    if done:
        text = texts.already_trained_title[lang]

    kb = kbs.get_start_training(lang, False)
    await message.answer(text, reply_markup=kb)