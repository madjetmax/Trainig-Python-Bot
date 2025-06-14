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

# *choose lang on start
def get_choose_lang():
    kb = InlineKeyboardBuilder()
    all_lengs = user_texts.all_lengs_codes

    for lang in all_lengs:
        text = user_texts.trans_leng_codes[lang]
        calldata = callback_filters.UserChooseLang(lang=lang).pack()

        kb.row(
            InlineKeyboardButton(text=text, callback_data=calldata)
        )

    return kb.as_markup()


def confirm_setup(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.yes_btn[lang], callback_data=callback_filters.UserConfirmSetup(data="confirm").pack())],
        [InlineKeyboardButton(text=user_texts.no_btn[lang], callback_data=callback_filters.UserConfirmSetup(data="cancel").pack())],
    ])

    return kb

# *setup training on start
def get_days_choice(**kwargs) -> Any:
    selected_days = kwargs.get("selected_days")
    return get_week_days(selected_days, 0, kwargs["lang"])

def get_week_days(seleted_days, kb_num, lang) -> InlineKeyboardMarkup:
    """returns text and list on buttons of week days '✅' - day selected and added to db"""
    kb = InlineKeyboardBuilder()
    week_days = user_texts.days_of_week

    if seleted_days == None:
        seleted_days_names = []
    else:
        seleted_days_names = seleted_days.keys()

    for day in week_days:
        text = user_texts.trans_days_of_week[lang][day]
        if day in seleted_days_names:
            text += " ✅"

        kb.row(InlineKeyboardButton(text=text, callback_data=callback_filters.UserChooseDay(day=day).pack()))

    kb.row(InlineKeyboardButton(text=user_texts.next_btn[lang], callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=kb_num+1).pack()))

    return kb.as_markup() 

def get_selected_day(day, lang):
    """returns settings for selected day 'workout body part' and 'reps'"""
    text = user_texts.trans_days_of_week[lang][day]

    kb = InlineKeyboardBuilder()
    
    # all settings
    kb.row(InlineKeyboardButton(text=user_texts.workout_body_part_setting_btn[lang], callback_data=callback_filters.UserSettingDay(day=day, setting="workout_body_part").pack()))
    kb.row(InlineKeyboardButton(text=user_texts.reps_setting_btn[lang], callback_data=callback_filters.UserSettingDay(day=day, setting="reps").pack()))
        
    return (text, kb.as_markup())

def get_selected_days_list(selected_days, lang):
    for day in selected_days.keys():
        yield get_selected_day(day, lang)

    # navigation
    kb = InlineKeyboardBuilder()
    text = user_texts.navigation_title[lang]

    kb_num = 1
    kb.row(InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=kb_num-1).pack()))
    kb.row(InlineKeyboardButton(text=user_texts.next_btn[lang], callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=kb_num+1).pack()))

    yield (text, kb.as_markup())


def get_body_parts(selected_part, day, all_body_parts, lang):
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

        text = part[lang]
        if part["name"] == selected_part:
            text += " ✅"
        current_row.append(
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserSettingDay(body_part=part["name"], day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)
    
    # add custom body_part button
    rows.append(
        [InlineKeyboardButton(text=user_texts.custom_btn[lang], callback_data=callback_filters.UserSettingDay(add_custom_body_part=True, day=day).pack())]
    )

    return rows

def get_text_from_reps(reps, day, lang):
    """returns text from reps data and day"""
    
    day = user_texts.trans_days_of_week[lang][day]
    text = user_texts.reps_list_title[lang].format(day=day)

    for rep in reps:
        if rep["name"] == "break":
            # get time 
            minutes = str(rep["minutes"])
            seconds = str( rep["seconds"])

            if len(minutes) == 1:
                minutes = "0" + minutes

            if len(seconds) == 1:
                seconds = "0" + seconds

            # add to text
            text += user_texts.break_in_list[lang].format(
                minutes=minutes, seconds=seconds
            )
            
        else:
            rep_name = rep["name"]

            # find rep name on translare or left it in oroginal
            for _rep in ALL_REPS_NAMES:
                if _rep["name"] == rep_name:
                    rep_name = _rep[lang]
                    break

            text += rep_name + "\n"
    return text


def get_reps(day, all_reps_names, lang):
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

        text = rep[lang]
        current_row.append(
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserSettingDay(rep_name=rep["name"], day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)

    # add custom rep_name button
    rows.append(
        [InlineKeyboardButton(text=user_texts.custom_btn[lang], callback_data=callback_filters.UserSettingDay(add_custom_rep_name=True, day=day).pack())]
    )

    # add back button
    rows.append(
        [InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserConfirmSetupNavigate(to="day_reps_setting", day=day).pack())]
    )

    return rows

def get_rep_name_setting(day, all_reps_names, lang) -> tuple[str, InlineKeyboardMarkup]:
    """returns text and buttons of all_reps_names"""
    
    kb = InlineKeyboardBuilder()
    text = user_texts.select_rep_name_title[lang]

    rows = get_reps(day, all_reps_names, lang)

    for row in rows:
        kb.row(*row)
    
    return text, kb.as_markup()


def get_day_setting_by_name(setting, day, day_data, state_data, lang) -> tuple[str, InlineKeyboardMarkup]:
    """returns setting from its name, takes day and day_data"""
    kb = InlineKeyboardBuilder()
    text = day

    if setting == "workout_body_part":
        text = user_texts.select_body_part_title[lang].format(day=user_texts.trans_days_of_week[lang][day])

        rows = get_body_parts(day_data.get("selected_part"), day, state_data["all_body_parts"], lang)
        for row in rows:
            kb.row(*row)

    if setting == "reps":
        reps = day_data.get("reps")

        kb.row(InlineKeyboardButton(text=user_texts.add_rep[lang], callback_data=callback_filters.UserSettingDay(reps_action="add_rep", day=day).pack()))

        if reps: # set text as a list of reps
            text = get_text_from_reps(reps, day, lang)

            kb.row(InlineKeyboardButton(text=user_texts.del_rep[lang], callback_data=callback_filters.UserSettingDay(reps_action="del_last_rep", day=day).pack()))
            kb.row(InlineKeyboardButton(text=user_texts.add_1_min_break[lang], callback_data=callback_filters.UserSettingDay(reps_action="add_1m_to_last_break", day=day).pack()))
            kb.row(InlineKeyboardButton(text=user_texts.remove_1_min_break[lang], callback_data=callback_filters.UserSettingDay(reps_action="remove_1m_to_last_break", day=day).pack()))

        else: # set default empty reps texts
            text = user_texts.empty_reps_title[lang]

    # add back button            
    kb.row(InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserConfirmSetupNavigate(to="day_setting", day=day).pack()))

    return (text, kb.as_markup())

def get_back_to_days_settings(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserConfirmSetupNavigate(kb_num=1).pack())]
    ])

    return kb

# *edit user training
def get_user_edit_training_confirm() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Confirm", callback_data=callback_filters.UserEditTrainingConfirm(data="confirm").pack())],
        [InlineKeyboardButton(text="Cancel", callback_data=callback_filters.UserEditTrainingConfirm(data="cancel").pack())],
    ])

    return kb
