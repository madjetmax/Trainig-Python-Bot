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

def confirm_setup() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data=callback_filters.UserConfirmSetup(data="confirm").pack())],
        [InlineKeyboardButton(text="No", callback_data=callback_filters.UserConfirmSetup(data="cancel").pack())],
    ])

    return kb

# *setup training on start
def get_setup_start(**kwargs) -> Any:
    selected_days = kwargs.get("selected_days")
    return get_week_days(selected_days, 0)

def get_week_days(seleted_days, kb_num) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    week_days = user_texts.days_of_week

    if seleted_days == None:
        seleted_days_names = []
    else:
        seleted_days_names = [name for name, data in seleted_days.items()]

    for day in week_days:
        name = day
        if day in seleted_days_names:
            name += " ✅"

        kb.row(InlineKeyboardButton(text=name, callback_data=callback_filters.UserChooseDay(day=day).pack()))

    kb.row(InlineKeyboardButton(text="Next", callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=kb_num+1).pack()))

    return kb.as_markup() 

def get_selected_day(day):
    text = day

    kb = InlineKeyboardBuilder()
    
    kb.row(InlineKeyboardButton(text="workout body part", callback_data=callback_filters.UserSettingDay(day=day, setting="workout_body_part").pack()))
    kb.row(InlineKeyboardButton(text="Reps", callback_data=callback_filters.UserSettingDay(day=day, setting="reps").pack()))

        
    return (text, kb.as_markup())

def get_selected_days_list(selected_days):
    for day, data in selected_days.items():
        yield get_selected_day(day)

    # navigation
    kb = InlineKeyboardBuilder()
    text = "Navigation"


    kb_num = 1
    kb.row(InlineKeyboardButton(text="Back", callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=kb_num-1).pack()))
    kb.row(InlineKeyboardButton(text="Next", callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=kb_num+1).pack()))


    yield (text, kb.as_markup())

    

all_body_parts = [
    "legs", "chest", "back", "arms"
]

def get_body_parts(selected_part, day):
    max_in_row = 3
    rows = []

    current_row = []
    collumn = 0
    
    for part in all_body_parts:
        if collumn >= max_in_row:
            rows.append(deepcopy(current_row))
            current_row = []
            collumn = 0

        text = part
        if part == selected_part:
            text += " ✅"
        current_row.append(
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserSettingDay(body_part=part, day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)
        

    return rows

def get_text_from_reps(reps, day):
    text = f"Reps for {day}\n"

    for rep in reps:
        
        
        if rep["name"] == "break":
            minutes = str(rep["minutes"])
            seconds = str( rep["seconds"])

            if len(minutes) == 1:
                minutes = "0" + minutes

            if len(seconds) == 1:
                seconds = "0" + seconds

            text += f"break, time: {minutes}:{seconds}\n"
        else:
            text += rep["name"] + "\n"
    return text

all_reps_names = [
    "horizontal bar",
    "push ups",
    "brusya",
]

def get_reps(day):
    max_in_row = 3
    rows = []

    current_row = []
    collumn = 0
    
    for rep in all_reps_names:
        if collumn >= max_in_row:
            rows.append(deepcopy(current_row))
            current_row = []
            collumn = 0

        text = rep
        current_row.append(
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserSettingDay(rep_name=rep, day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)

    return rows

def get_rep_name_setting(day):
    kb = InlineKeyboardBuilder()
    text = "select rep name"

    rows = get_reps(day)

    for row in rows:
        kb.row(*row)
    
    return text, kb.as_markup()


def get_day_setting_by_name(setting, day, day_data) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    text = day

    if setting == "workout_body_part":
        text = f"Select body part for {day}"

        rows = get_body_parts(day_data.get("selected_part"), day)
        for row in rows:
            kb.row(*row)

    if setting == "reps":
        reps = day_data.get("reps")

        if reps:
            text = get_text_from_reps(reps, day)
        else:
            text = "No reps added, tap bellow to add"

        kb.row(InlineKeyboardButton(text="Add rep", callback_data=callback_filters.UserSettingDay(reps_action="add_rep", day=day).pack()))

        if reps:
            kb.row(InlineKeyboardButton(text="Delete last rep", callback_data=callback_filters.UserSettingDay(reps_action="del_last_rep", day=day).pack()))
            kb.row(InlineKeyboardButton(text="Add 1 min to last break", callback_data=callback_filters.UserSettingDay(reps_action="add_1m_to_last_break", day=day).pack()))
            kb.row(InlineKeyboardButton(text="Remove 1 min from last break", callback_data=callback_filters.UserSettingDay(reps_action="remove_1m_to_last_break", day=day).pack()))

    kb.row(InlineKeyboardButton(text="Back", callback_data=callback_filters.UserConfirmSetupNavigate(to="selected_days_list", day=day).pack()))

    return (text, kb.as_markup())

def get_back_to_days_settings() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=1).pack())]
    ])

    return kb

# *edit user training
def get_user_edit_training_confirm() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Confirm", callback_data=callback_filters.UserEditTrainingConfirm(data="confirm").pack())],
        [InlineKeyboardButton(text="Cancel", callback_data=callback_filters.UserEditTrainingConfirm(data="cancel").pack())],
    ])

    return kb
