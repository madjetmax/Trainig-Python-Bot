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
def get_start_training(lang) -> InlineKeyboardMarkup:
    confirm_data = callback_filters.UserStartTraining(data="start").pack()
    cancel_data = callback_filters.UserStartTraining(data="not_today").pack()

    # start training buttons
    text1 = user_texts.start_training_confirm_btn[lang]
    text2 = user_texts.not_today_btn[lang]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text1, callback_data=confirm_data)],
        [InlineKeyboardButton(text=text2, callback_data=cancel_data)],
    ])

    return kb

def get_break(lang) -> InlineKeyboardMarkup:
    calldata = callback_filters.UserNavigateTrainingStates(data="break").pack()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.take_break_btn[lang], callback_data=calldata)]
    ])

    return kb

def get_break_controll(lang) -> InlineKeyboardMarkup:
    calldata = callback_filters.UserBreakControll(action="add_30_seconds").pack()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.add_30_seconds[lang], callback_data=calldata)]
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


def get_training_control(state_data: dict, lang) -> tuple[str, InlineKeyboardMarkup]:
    # kb
    pause = [InlineKeyboardButton(text=user_texts.pause_training_btn[lang], callback_data=callback_filters.UserControlTraining(data="pause").pack())]
    if state_data["stopped"]:
        pause = [InlineKeyboardButton(text=user_texts.resume_training_btn[lang], callback_data=callback_filters.UserControlTraining(data="resume").pack())]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        pause, # row
        [InlineKeyboardButton(text=user_texts.finish_training_btn[lang], callback_data=callback_filters.UserControlTraining(data="finish").pack())],
        [InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserControlTraining(data="back").pack())],
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

    text = user_texts.training_status[lang].format(
        body_part=body_part,
        clear_training_time=clear_training_time,
        clear_time_start=clear_time_start,
        reps_finished=reps_finished,
        reps_left=reps_left,
    )
    
    return text, kb

# finish and pause confirm
def get_confirm_finish_training(lang) -> InlineKeyboardMarkup:
    text1 = user_texts.finish_training_confirm_btn[lang]
    text2 = user_texts.cancel_btn[lang]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text1, callback_data=callback_filters.UserControlTraining(data="confirm_finish").pack())],
        [InlineKeyboardButton(text=text2, callback_data=callback_filters.UserControlTraining(data="back_to_menu").pack())],
    ])

    return kb

def get_confirm_pause_training(lang) -> InlineKeyboardMarkup:
    text1 = user_texts.pause_training_confirm_btn[lang]
    text2 = user_texts.cancel_btn[lang]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text1, callback_data=callback_filters.UserControlTraining(data="confirm_pause").pack())],
        [InlineKeyboardButton(text=text2, callback_data=callback_filters.UserControlTraining(data="back_to_menu").pack())],
    ])

    return kb


async def get_add_more_f_t(start, offset, lang) -> InlineKeyboardMarkup:
    text = user_texts.add_more_btn[lang]

    calldata = callback_filters.UserAddMoreFT(offset=offset, start=start).pack()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=calldata)]

    ])

    return kb