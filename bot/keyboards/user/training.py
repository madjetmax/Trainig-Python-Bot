from copy import deepcopy
import datetime
from zoneinfo import ZoneInfo
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Generator, Any

from config import *

import database as db
from .. import callback_filters
from texts import user as user_texts





# *user training
def get_start_training() -> InlineKeyboardMarkup:
    confirm_data = callback_filters.UserStartTraining(data="start").pack()
    cancel_data = callback_filters.UserStartTraining(data="not_today").pack()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start", callback_data=confirm_data)],
        [InlineKeyboardButton(text="Not Today", callback_data=cancel_data)],
    ])

    return kb

def get_break() -> InlineKeyboardMarkup:
    calldata = callback_filters.UserNavigateTrainingStates(data="break").pack()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Take a Break", callback_data=calldata)]
    ])

    return kb

def get_break_controll():
    calldata = callback_filters.UserBreakControll(action="add_30_seconds").pack()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Add 30 Seconds", callback_data=calldata)]
    ])

    return kb    


# *training status message with text and buttons
def get_clear_time(hours, minutes, seconds):

    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)

    return f"{hours}:{minutes}.{seconds}"


def get_training_control(state_data: dict) -> tuple[str, InlineKeyboardMarkup]:
    # kb
    pause = [InlineKeyboardButton(text="Pause training", callback_data=callback_filters.UserControlTraining(data="pause").pack())]
    if state_data["stopped"]:
        pause = [InlineKeyboardButton(text="Resume training", callback_data=callback_filters.UserControlTraining(data="resume").pack())]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        pause, # row
        [InlineKeyboardButton(text="Finish training", callback_data=callback_filters.UserControlTraining(data="finish").pack())],
        [InlineKeyboardButton(text="Back <<", callback_data=callback_filters.UserControlTraining(data="back").pack())],
    ])

    # text
    time_start: datetime = state_data["time_start"]

    tz = ZoneInfo(DATETIME_TIME_ZONE)
    now = datetime.datetime.now(tz)

    # get clear time start
    start_hours = time_start.time().hour
    start_minutes = time_start.time().minute
    start_seconds = time_start.time().second

    clear_time_start = get_clear_time(start_hours, start_minutes, start_seconds)

    # calculatin training time
    training_time: datetime.timedelta = now - time_start
    
    training_hours = int(training_time.total_seconds() // 3600)
    training_minutes = int((training_time.total_seconds() % 3600) // 60)
    training_seconds = int(training_time.total_seconds() % 60)
    
    clear_training_time = get_clear_time(training_hours, training_minutes, training_seconds)

    # calculating finished reps        
    reps_finished = state_data["reps_finished"]
    reps_left = state_data["all_reps_count"] - reps_finished

    # getting body_part
    body_part = state_data["full_training_data"]["selected_part"]


    text = f"""
Current Body part: {body_part}\n
training time: {clear_training_time}
started at: {clear_time_start}\n
finished reps: {reps_finished}
reps left: {reps_left}
    """

    return text, kb

# finish and pause confirm
def get_confirm_finish_training() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Finish", callback_data=callback_filters.UserControlTraining(data="confirm_finish").pack())],
        [InlineKeyboardButton(text="Cancel", callback_data=callback_filters.UserControlTraining(data="back_to_menu").pack())],
    ])

    return kb

def get_confirm_pause_training() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Pause", callback_data=callback_filters.UserControlTraining(data="confirm_pause").pack())],
        [InlineKeyboardButton(text="Cancel", callback_data=callback_filters.UserControlTraining(data="back_to_menu").pack())],
    ])

    return kb


async def get_add_more_f_t(start, offset) -> InlineKeyboardMarkup:
    calldata = callback_filters.UserAddMoreFT(offset=offset, start=start).pack()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Add more", callback_data=calldata)]

    ])

    return kb