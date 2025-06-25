import datetime
from zoneinfo import ZoneInfo
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import *

from .. import callback_filters
from texts import user as user_texts


# *user training
def get_start_training(lang, can_cancel=True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # start training buttons
    text1 = user_texts.start_training_confirm_btn[lang]
    confirm_data = callback_filters.UserStartTraining(data="start").pack()
    kb.row(
        InlineKeyboardButton(text=text1, callback_data=confirm_data)
    )

    if can_cancel:
        text2 = user_texts.not_today_btn[lang]
        cancel_data = callback_filters.UserStartTraining(data="not_today").pack()
        kb.row(
            InlineKeyboardButton(text=text2, callback_data=cancel_data)
        )
    return kb.as_markup()

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

def get_start_other_day_training(lang) -> tuple[str, InlineKeyboardMarkup]:
    kb = InlineKeyboardBuilder() 

    text = user_texts.start_other_day_training_plan_titile[lang]

    # confirm
    confirm_text = user_texts.yes_btn[lang]
    confirm_calldata = callback_filters.UserStartOtherDayPlanTraining(data="confirm").pack()
    kb.row(
        InlineKeyboardButton(text=confirm_text, callback_data=confirm_calldata)
    )

    # cancel
    cancel_text = user_texts.no_btn[lang]
    cancel_calldata = callback_filters.UserStartOtherDayPlanTraining(data="cancel").pack()
    kb.row(
        InlineKeyboardButton(text=cancel_text, callback_data=cancel_calldata)
    )

    return text, kb.as_markup()

# *training status message with text and buttons
def get_clear_time(hours, minutes, seconds):

    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)

    return f"{hours}:{minutes}.{seconds}"

def get_clear_minutes_and_seconds(minutes, seconds) -> tuple[int, int]:
        """returns minutes ans seconds"""

        if len(str(minutes)) == 1:
            minutes = "0" + str(minutes)

        if len(str(seconds)) == 1:
            seconds = "0" + str(seconds)

        return minutes, seconds



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

    # find body part on user lang in state_data
    for body_part1 in state_data["user_body_parts_names"]:
        if body_part1["name"] == body_part:
            body_part = body_part1[lang]
            break

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

# get list of selected days to get_training_plan
def get_selected_days_training_plans(days_data: dict, lang) -> tuple[str, list[tuple[str, InlineKeyboardMarkup]]]:
    text = user_texts.choose_day_trainig_plan_title[lang]
    messages = []

    for day_name in days_data.keys():
        day_text, day_kb = get_day_select_training_plan(day_name, lang)
        messages.append((day_text, day_kb))

    return text, messages

def get_day_select_training_plan(day_name: str, lang) -> tuple[str, InlineKeyboardMarkup]:
    day_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton( # select button
            text=user_texts.select_btn[lang],
            callback_data=callback_filters.UserSelectDayPlanTrainig(day_name=day_name).pack()
        )],
        [InlineKeyboardButton( # view plan button
            text=user_texts.get_training_plan_btn[lang],
            callback_data=callback_filters.UserSelectDayPlanTrainig(day_name=day_name, get_plan=True).pack()
        )]
    ])

    day_text = user_texts.trans_days_of_week[lang][day_name]
    return day_text, day_kb


def get_day_training_plan_text(day_data, day_name, all_body_parts, all_reps_names, lang) -> str:
    selected_part = day_data["selected_part"]
    # fing part on user lang
    for part in all_body_parts:
        if part["name"] == selected_part:
            selected_part = part[lang]
            break

    text = user_texts.day_selected_part_title[lang].format(day_name=user_texts.trans_days_of_week[lang][day_name], selected_part=selected_part)
    text += user_texts.reps_title[lang]

    for rep in day_data["reps"]:
        if rep["name"] == "break":
            minutes, seconds = get_clear_minutes_and_seconds(minutes=rep["minutes"], seconds=rep["seconds"])
            text += user_texts.break_title[lang].format(minutes=minutes, seconds=seconds)
            text += "\n"
        else:
            rep_name = rep["name"]
            # fing rep name on user lang
            for _rep_name in all_reps_names:
                if _rep_name["name"] == rep_name:
                    rep_name = _rep_name[lang]
                    break

            text += rep_name
            text += "\n"
    return text


def get_day_training_plan(day_data: dict, all_body_parts: list, all_reps_names: list, day_name, lang) -> tuple[str, InlineKeyboardMarkup]:
    
    back_btn_calldata = callback_filters.UserSelectDayPlanTrainig(back_to_day=day_name).pack()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.back_btn[lang], callback_data=back_btn_calldata)]
    ])

    text = get_day_training_plan_text(day_data, day_name, all_body_parts, all_reps_names, lang)
    return text, kb


# *finished training
async def get_add_more_f_t(start, offset, lang) -> InlineKeyboardMarkup:
    text = user_texts.add_more_btn[lang]

    calldata = callback_filters.UserAddMoreFT(offset=offset, start=start).pack()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=calldata)]

    ])

    return kb