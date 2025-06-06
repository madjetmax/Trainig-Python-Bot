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



# *user menu and edit data
user_menu = {
    # To get page, set 'get' at the begining
    0: [ # kb num  
        { 
            "text": "My Data",
            "to": "get_data",
        }, # button
        { 
            "text": "Edit training",
            "to": "get_edit_trainings",
        },
    ],  
    "get_data": [   
        { 
            "text": "Back <<",
            "to": "main",
        },
    ],  
    "get_edit_trainings": [   
        { 
            "text": "Edit Trainings Days",
            "to": "get_edit_trainings_days",
        },
        { 
            "text": "Edit Reps",
            "to": "get_edit_reps",
        },
        { 
            "text": "Edit Start Time",
            "to": "get_edit_start_time",
        },
        { 
            "text": "Back <<",
            "to": "main",
        },
    ],   
}  

def get_selected_days(selected_days):
    """returns text and list on buttons of week days '✅' - day selected and added to db"""
    week_days = user_texts.days_of_week

    if selected_days == None:
        seleted_days_names = []
    else:
        seleted_days_names = selected_days

    for day in week_days:
        name = day
        if day in seleted_days_names:
            name += " ✅"
        # send already ready button
        yield InlineKeyboardButton(text=name, callback_data=callback_filters.UserEditData(switch_day=day).pack())

    yield InlineKeyboardButton(text="Back <<", callback_data=callback_filters.UserEditData(to="get_edit_trainings").pack())


def get_selected_day(day):
    """returns settings for selected day 'workout body part' and 'reps'"""
    text = day

    kb = InlineKeyboardBuilder()
    
    kb.row(InlineKeyboardButton(text="workout body part", callback_data=callback_filters.UserEditDay(day=day, setting="workout_body_part").pack()))
    kb.row(InlineKeyboardButton(text="Reps", callback_data=callback_filters.UserEditDay(day=day, setting="reps").pack()))

    return (text, kb.as_markup())

all_body_parts = [
    "legs", "chest", "back", "arms"
]

def get_body_parts(selected_part, day):
    """returns list of rows of InlineKeyboardButton consists of all_body_parts"""
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
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserEditDay(body_part=part, day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)
        

    return rows

def get_text_from_reps(reps, day):
    """returns text from reps data and day"""
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


# reps
all_reps_names = [
    "horizontal bar",
    "push ups",
    "brusya",
]
def get_reps(day):
    """returns list of rows of InlineKeyboardButton consists of all_reps_names"""
    
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
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserEditDay(rep_name=rep, day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)

    return rows

def get_rep_name_setting(day):
    """returns text and buttons of all_reps_names"""
    kb = InlineKeyboardBuilder()
    text = "select rep name"

    rows = get_reps(day)

    for row in rows:
        kb.row(*row)
    
    return text, kb.as_markup()

def get_day_setting_by_name(setting, day, day_data) -> InlineKeyboardMarkup:
    """returns setting from its name, takes day and day_data"""
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

        kb.row(InlineKeyboardButton(text="Add rep", callback_data=callback_filters.UserEditDay(reps_action="add_rep", day=day).pack()))

        if reps:
            kb.row(InlineKeyboardButton(text="Delete last rep", callback_data=callback_filters.UserEditDay(reps_action="del_last_rep", day=day).pack()))
            kb.row(InlineKeyboardButton(text="Add 1 min to last break", callback_data=callback_filters.UserEditDay(reps_action="add_1m_to_last_break", day=day).pack()))
            kb.row(InlineKeyboardButton(text="Remove 1 min from last break", callback_data=callback_filters.UserEditDay(reps_action="remove_1m_to_last_break", day=day).pack()))

    kb.row(InlineKeyboardButton(text="Back <<", callback_data=callback_filters.UserEditData(to="selected_days_list", back_to_day=day).pack()))

    return (text, kb.as_markup())

# help command to get clean hours and minutes 
def get_clean_hours_and_minutes(hours, minutes) -> tuple[int, int]:
    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    return hours, minutes

async def get_user_menu(kb_num, to=None, user_data=None, **kwargs) -> tuple[str, InlineKeyboardMarkup, list]:
    """returns text, kb, messages (list) from kb_num or 'page name' takes additional args to get specific data, also gets user from database"""
    
    kb = InlineKeyboardBuilder()
    text = ""
    messages = []
    
    if kb_num == 0 or to == "main":
        buttons = user_menu[0]
        text = "Main menu"

        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.UserEditData(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"], callback_data=calldata)
            )
    # get and manage data
    if to == "get_data":
        user = await db.get_user(user_data.id)

        text = str(user)
        buttons = user_menu["get_data"]
        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.UserEditData(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"], callback_data=calldata)
            )

    # edit trainings
    if to == "get_edit_trainings":
        text = "Choose what you want to edit"
        buttons = user_menu["get_edit_trainings"]
        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.UserEditData(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"], callback_data=calldata)
            )

    if to == "get_edit_trainings_days":
        text = "Select Days"

        # getting list of days names from **kwargs, if not found, from User.trainings.days_data
        selected_days = kwargs.get("selected_days")
        if selected_days == None:
            user = await db.get_user(user_data.id)
            selected_days = list(user.trainings.days_data.keys())

        buttons = get_selected_days(selected_days)
        # add buttons to kb
        for button in buttons:
            kb.row(button)

    if to == "get_edit_reps":
        text = "Edit Reps"
        # getting list of days names from **kwargs, if not found, from User.trainings.days_data
        selected_days = kwargs.get("selected_days")
        if selected_days == None:
            user = await db.get_user(user_data.id)
            selected_days = user.trainings.days_data

        for day in selected_days.keys():
            day_data = selected_days[day]

            day_text, day_kb = get_selected_day(day)
            messages.append((day_text, day_kb))

        # back button
        calldata = callback_filters.UserEditData(to="get_edit_trainings").pack()
        
        back_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back <<", callback_data=calldata)]
        ])
        messages.append(("Navigation", back_kb))
    
    if to == "selected_days_list":
        day_text, day_kb = get_selected_day(kwargs["day"])
        return day_text, day_kb, []
    
    # edit trainings start time
    if to == "get_edit_start_time":
        user = await db.get_user(user_data.id)

        hours, minutes = get_clean_hours_and_minutes(user.trainings.time_start_hours, user.trainings.time_start_minutes)
        
        text = f"Enter new time for trainings start, current: {hours}:{minutes}"

        # add back button
        calldata = callback_filters.UserEditData(to="get_edit_trainings").pack()
        kb.row(InlineKeyboardButton(text="Back <<", callback_data=calldata))

    return text, kb.as_markup(), messages