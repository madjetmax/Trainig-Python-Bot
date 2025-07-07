from copy import deepcopy
import datetime
from zoneinfo import ZoneInfo
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User, UserTrainings, FinishedUserTraining

from config import *
from . import training as trainings_kbs

import database as db
from .. import callback_filters
from texts import user as user_texts


# *user menu and edit data
user_menu = {
    # To get page, set 'get' at the begining
    "main": [ # kb num  
        { 
            "text": {
                "en": "My Data",
                "uk": "Мої Дані",
            },
            "to": "get_data",
        }, # button
        { 
            "text": {
                "en": "Edit training",
                "uk": "Наліштування тренувань"
            },
            "to": "get_edit_trainings",
        },
        { 
            "text": {
                "en": "Edit Lang",
                "uk": "Змінити мову"
            },
            "to": "edit_lang",
        },
        { 
            "text": {
                "en": "Finished Trainings",
                "uk": "Заверешкені Тренування"
            },
            "to": "get_f_t",
        },
    ],  
    "get_data": [   
        { 
            "text": {
                "en": "Back <<",
                "uk": "Назад <<",
            },
            "to": "main",
        },
    ],  
    "get_edit_trainings": [   
        { 
            "text": {
                "en": "Edit Trainings Days",
                "uk": "Налаштування днів тренування",
            },
            "to": "get_edit_trainings_days",
        },
        { 
            "text":{
                "en": "Edit Reps and Breaks",
                "uk": "Налаштувати підходи та перерви",
            },
            "to": "get_edit_reps",
        },
        { 
            "text": {
                "en": "Edit Start Time",
                "uk": "Змінити час початку тренування",
            },
            "to": "get_edit_start_time",
        },
        { 
            "text": {
                "en": "Back <<",
                "uk": "Назад <<",
            },
            "to": "main",
        },
    ], 
}  

async def get_user_menu(to=None, user_data=None, lang="", **kwargs) -> tuple[str, InlineKeyboardMarkup, list]:
    """returns text, kb, messages (list) from to (page name)  takes additional args to get specific data, user from database"""
    
    kb = InlineKeyboardBuilder()
    text = ""
    messages = []
    
    if to == "main":
        buttons = user_menu["main"]
        text = user_texts.main_menu[lang]

        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.UserEditData(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"][lang], callback_data=calldata)
            )
    # get and manage data
    if to == "get_data":
        user: User = kwargs["user"]

        text = str(user)
        buttons = user_menu["get_data"]
        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.UserEditData(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"][lang], callback_data=calldata)
            )

    # edit trainings
    if to == "get_edit_trainings":
        text = user_texts.edit_trainings_menu[lang]

        buttons = user_menu["get_edit_trainings"]
        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.UserEditData(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"][lang], callback_data=calldata)
            )

    if to == "get_edit_trainings_days":
        text = user_texts.edit_selected_days_menu[lang]

        # getting list of days names from **kwargs, if not found, from User.trainings.days_data
        selected_days = kwargs.get("selected_days")
        if selected_days == None:
            user: User = kwargs["user"]
            selected_days = list(user.trainings.days_data.keys())

        buttons = get_selected_days(selected_days, lang)
        # add buttons to kb
        for button in buttons:
            kb.row(button)

    if to == "get_edit_reps":
        text = user_texts.edit_reps_menu[lang]
        # getting list of days names from **kwargs, if not found, from User.trainings.days_data
        selected_days = kwargs.get("selected_days")
        if selected_days == None:
            user: User = kwargs["user"]
            selected_days = user.trainings.days_data

        for day in selected_days.keys():
            day_data = selected_days[day]

            day_text, day_kb = get_selected_day(day, lang)
            messages.append((day_text, day_kb))

        # back button
        calldata = callback_filters.UserEditData(to="get_edit_trainings").pack()
        
        back_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=calldata)]
        ])
        messages.append((user_texts.navigation_title[lang], back_kb))
    
    # body part and reps
    if to == "day_setting":
        day_text, day_kb = get_selected_day(kwargs["day"], lang)
        return day_text, day_kb, []

    if to == "day_reps_setting":
        # get day data
        user: User = kwargs["user"]
        selected_days = user.trainings.days_data

        day = kwargs["day"]
        day_data = selected_days[day]

        # return data
        day_text, day_kb = get_day_setting_by_name("reps", day, day_data, lang)
        return day_text, day_kb, []
    
    # edit trainings start time
    if to == "get_edit_start_time":
        user: User = kwargs["user"]

        hours, minutes = get_clean_hours_and_minutes(user.trainings.time_start_hours, user.trainings.time_start_minutes)
        
        text = user_texts.new_trainings_start_time[lang].format(hours=hours, minutes=minutes)

        # add back button
        calldata = callback_filters.UserEditData(to="get_edit_trainings").pack()
        kb.row(InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=calldata))
    # lang 
    if to == "edit_lang":
        user: User = kwargs["user"]

        text = user_texts.edit_lang_menu[lang]
        for lang_code in user_texts.all_lengs_codes:
            btn_text = user_texts.trans_leng_codes[lang_code]
            if lang_code == lang:
                btn_text += " ✅"

            calldata = callback_filters.UserEditData(set_lang=lang_code).pack()
            kb.row(InlineKeyboardButton(text=btn_text, callback_data=calldata))

        calldata = callback_filters.UserEditData(to="main").pack()
        kb.row(InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=calldata))
    
    # finished trainings
    if to == "get_f_t":
        user: User = kwargs["user"]

        offset = 5

        # sort trainins by date
        finished_trainings = sorted(user.finished_trainings[:offset], key=sort_finished_trainings)
        for i, f_t in enumerate(finished_trainings):
            f_t_kb = None
            # add keyboard if message is the last
            if i + 1 == len(finished_trainings) and i + 1 < len(user.finished_trainings):
                start = offset
                f_t_kb = await trainings_kbs.get_add_more_f_t(start, offset)
            # add message in messages list
            f_t_text = get_training_result(f_t, user.lang, user.trainings.all_body_parts)
            messages.append(
                (f_t_text, f_t_kb)
            )

    return text, kb.as_markup(), messages

def sort_finished_trainings(x: FinishedUserTraining) -> int:
    # getting seconds from datetime to sort
    seconds = x.time_start.timestamp()
    return -seconds

# like help commands for handlers
def set_timezone(date: datetime.datetime) -> datetime.datetime:
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    return date.astimezone(tz)

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

    text = user_texts.finished_training_text[lang].format(
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


def get_selected_days(selected_days, lang):
    """returns text and list on buttons of week days '✅' - day selected and added to db"""
    week_days = user_texts.days_of_week

    if selected_days == None:
        seleted_days_names = []
    else:
        seleted_days_names = selected_days

    for day in week_days:
        text = user_texts.trans_days_of_week[lang][day]

        if day in seleted_days_names:
            text += " ✅"
        # send already ready button
        yield InlineKeyboardButton(text=text, callback_data=callback_filters.UserEditData(switch_day=day).pack())

    yield InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserEditData(to="get_edit_trainings").pack())


def get_selected_day(day, lang) -> tuple[str, InlineKeyboardMarkup]:
    """returns settings for selected day 'workout body part' and 'reps'"""
    text = user_texts.trans_days_of_week[lang][day]

    kb = InlineKeyboardBuilder()
    
    kb.row(InlineKeyboardButton(text=user_texts.workout_body_part_setting_btn[lang], callback_data=callback_filters.UserEditDay(day=day, setting="workout_body_part").pack()))
    kb.row(InlineKeyboardButton(text=user_texts.reps_setting_btn[lang], callback_data=callback_filters.UserEditDay(day=day, setting="reps").pack()))

    return (text, kb.as_markup())


def get_body_parts(selected_part, day, all_body_parts, lang):
    """returns list of rows of InlineKeyboardButton consists of all_body_parts"""
    max_in_row = 3
    rows = []

    current_row = []
    collumn = 0
    
    for ind, part in enumerate(all_body_parts):
        if collumn >= max_in_row:
            rows.append(deepcopy(current_row))
            current_row = []
            collumn = 0

        text = part[lang]
        if part["name"] == selected_part:
            text += " ✅"
        current_row.append(
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserEditDay(body_part_ind=ind, day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)

    if selected_part is not None:
        # add use for all days button
        rows.append(
            [InlineKeyboardButton(text=user_texts.use_for_all_days_btn[lang], callback_data=callback_filters.UserEditDay(use_body_part_for_all_days=True, day=day).pack())]
        )
    
    # add custom body_part button
    rows.append(
        [InlineKeyboardButton(text=user_texts.custom_btn[lang], callback_data=callback_filters.UserEditDay(add_custom_body_part=True, day=day).pack())]
    )

    return rows

def get_confirm_use_body_part_for_all_days(day, part, lang) -> tuple[str, InlineKeyboardMarkup]:
    text = user_texts.confirm_use_body_part_for_all_days[lang]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.yes_btn[lang], callback_data=callback_filters.UserEditDay(day=day, confirm_use_body_part_for_all_days="1", body_part=part).pack())],
        [InlineKeyboardButton(text=user_texts.no_btn[lang], callback_data=callback_filters.UserEditDay(day=day, confirm_use_body_part_for_all_days="0").pack())]
    ])

    return text, kb

def get_text_from_reps(reps, day, lang):
    """returns text from reps data and day"""
    day = user_texts.trans_days_of_week[lang][day]
    text = user_texts.reps_list_title[lang].format(day=day)

    for rep in reps:
        if rep["name"] == "break":
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


# reps
def get_reps(day, all_reps_names, lang):
    """returns list of rows of InlineKeyboardButton consists of all_reps_names"""
    
    max_in_row = 3
    rows = []

    current_row = []
    collumn = 0
    
    for ind, rep in enumerate(all_reps_names):
        if collumn >= max_in_row:
            rows.append(deepcopy(current_row))
            current_row = []
            collumn = 0

        text = rep[lang]
        current_row.append(
            InlineKeyboardButton(text=text, callback_data=callback_filters.UserEditDay(rep_name_ind=ind, day=day).pack())
        )
        collumn += 1
    if current_row:
        rows.append(current_row)

    # add custom rep_name button
    rows.append(
        [InlineKeyboardButton(text=user_texts.custom_btn[lang], callback_data=callback_filters.UserEditDay(add_custom_rep_name=True, day=day).pack())]
    )

    # add back button
    rows.append(
        [InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserEditData(to="day_reps_setting", back_to_day=day).pack())]
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

def get_confirm_use_reps_for_all_days(day, lang) -> tuple[str, InlineKeyboardMarkup]:
    text = user_texts.confirm_use_reps_for_all_days[lang]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.yes_btn[lang], callback_data=callback_filters.UserEditDay(day=day, confirm_use_reps_for_all_days="1").pack())],
        [InlineKeyboardButton(text=user_texts.no_btn[lang], callback_data=callback_filters.UserEditDay(day=day, confirm_use_reps_for_all_days="0").pack())]
    ])

    return text, kb


def get_day_setting_by_name(setting, day, day_data, lang, **kwargs) -> InlineKeyboardMarkup:
    """returns setting from its name, takes day and day_data"""
    kb = InlineKeyboardBuilder()
    text = day

    if setting == "workout_body_part":
        text = user_texts.select_body_part_title[lang].format(day=user_texts.trans_days_of_week[lang][day])

        rows = get_body_parts(day_data.get("selected_part"), day, kwargs["all_body_parts"], lang)
        for row in rows:
            kb.row(*row)

    if setting == "reps":
        reps = day_data.get("reps")

        kb.row(InlineKeyboardButton(text=user_texts.add_rep[lang], callback_data=callback_filters.UserEditDay(reps_action="add_rep", day=day).pack()))

        if reps: # set text as a list of reps
            text = get_text_from_reps(reps, day, lang)

            kb.row(InlineKeyboardButton(text=user_texts.del_rep[lang], callback_data=callback_filters.UserEditDay(reps_action="del_last_rep", day=day).pack()))
            kb.row(InlineKeyboardButton(text=user_texts.add_1_min_break[lang], callback_data=callback_filters.UserEditDay(reps_action="add_1m_to_last_break", day=day).pack()))
            kb.row(InlineKeyboardButton(text=user_texts.remove_1_min_break[lang], callback_data=callback_filters.UserEditDay(reps_action="remove_1m_to_last_break", day=day).pack()))
            kb.row(InlineKeyboardButton(text=user_texts.copy_last_break[lang], callback_data=callback_filters.UserEditDay(reps_action="copy_last_rep", day=day).pack()))
            kb.row(InlineKeyboardButton(text=user_texts.use_for_all_days_btn[lang], callback_data=callback_filters.UserEditDay(reps_action="user_for_all_days", day=day).pack()))

        else: # set default empty reps texts
            text = user_texts.empty_reps_title[lang]

    # add back button for all settings
    kb.row(InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=callback_filters.UserEditData(to="day_setting", back_to_day=day).pack()))

    return (text, kb.as_markup())

# help command to get clean hours and minutes 
def get_clean_hours_and_minutes(hours, minutes) -> tuple[int, int]:
    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    return hours, minutes



