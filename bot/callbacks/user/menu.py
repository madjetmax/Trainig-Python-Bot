from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from zoneinfo import ZoneInfo

from config import *

# states
from aiogram.fsm.context import FSMContext
from states import user as states

from keyboards import callback_filters
from keyboards.user import menu as kbs
from texts import user as texts
import database as db
from database.models import User, FinishedUserTraining, UserTrainings

router = Router()


async def delete_messages(bot: Bot, chat_id, messages):
    if messages:
        await bot.delete_messages(chat_id, messages)


# *user menu and edit data
@router.callback_query(callback_filters.UserEditData.filter(F.switch_day != " "))
async def user_menu_switch_day(call: CallbackQuery, callback_data: callback_filters.UserEditData):
    message = call.message
    user_data = call.from_user

    switch_day = callback_data.switch_day
    
    user = await db.get_user(user_data.id)

    # get and update selected days
    selected_days = user.trainings.days_data # getting list from dict

    if switch_day in selected_days:
        if len(selected_days) > 1:
            selected_days.pop(switch_day)
        else:
            await call.answer("At least one day should be selected")
            return
    else:
        selected_days[switch_day] = {"selected_part": "legs", "reps": []}

    await db.udpate_user_trainings(user_data.id, {"days_data": selected_days})

    # edit message
    text, kb, messages = await kbs.get_user_menu(-1, "get_edit_trainings_days", user_data, selected_days=selected_days)

    await message.edit_text(text=text, reply_markup=kb)

@router.callback_query(callback_filters.UserEditData.filter(F.back_to_day != " "))
async def back_to_day_setting(call: CallbackQuery, callback_data: callback_filters.UserEditData, state: FSMContext):
    message = call.message
    user_data = call.from_user
    state_data = await state.get_data()

    kb_num = callback_data.kb_num
    to = callback_data.to
    back_to_day = callback_data.back_to_day

    text, kb, messages = await kbs.get_user_menu(kb_num, to, user_data, day=back_to_day)

    await message.edit_text(text, reply_markup=kb)

@router.callback_query(callback_filters.UserEditData.filter())
async def user_menu(call: CallbackQuery, callback_data: callback_filters.UserEditData, state: FSMContext):
    message = call.message
    user_data = call.from_user
    state_data = await state.get_data()

    kb_num = callback_data.kb_num
    to = callback_data.to

    text, kb, messages = await kbs.get_user_menu(kb_num, to, user_data)

    if to == "get_edit_start_time":
        await state.set_state(states.UserEditData.time_start)
    else:
        await state.set_state(states.UserEditData)

    if messages: # send messages if != []
        messages_to_delete = []
        await message.delete()
        for text, kb in messages:
            msg = await message.answer(text=text, reply_markup=kb)
            messages_to_delete.append(msg.message_id)

        await state.update_data(messages_to_delete=messages_to_delete)
    else: 
        messages_to_delete = state_data.get("messages_to_delete")
        if messages_to_delete: # send new message and delete messages_to_delete from state
            await message.answer(text=text, reply_markup=kb)
            await delete_messages(message.bot, user_data.id, messages_to_delete)
            await state.update_data(
                messages_to_delete=[]
            )
        else: # just answer
            await message.edit_text(text=text, reply_markup=kb)


# *day settings, body part, reps
@router.callback_query(callback_filters.UserEditDay.filter(F.setting != " "))
async def setting_day_setting(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user

    day = callback_data.day
    setting = callback_data.setting

    user = await db.get_user(user_data.id)

    day_data = user.trainings.days_data[day]

    text, kb = kbs.get_day_setting_by_name(setting, day, day_data)
    await message.edit_text(text=text, reply_markup=kb)

@router.callback_query(callback_filters.UserEditDay.filter(F.body_part != " "))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user

    part = callback_data.body_part
    day = callback_data.day

    user = await db.get_user(user_data.id)
    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    day_data = days[day]

    days[day]["selected_part"] = part

    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data)

    await message.edit_text(text, reply_markup=kb)

    await db.udpate_user_trainings(user_data.id, {"days_data": days})

@router.callback_query(callback_filters.UserEditDay.filter(F.reps_action != " "))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user

    action = callback_data.reps_action
    day = callback_data.day

    user = await db.get_user(user_data.id)
    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    
    day_data = days[day]
    reps = day_data["reps"]

    if action == "add_rep":
        text, kb = kbs.get_rep_name_setting(day)
        await message.edit_text(text, reply_markup=kb)

    else:
        if action == "del_last_rep":
            reps.pop()
            reps.pop()

        if action == "add_1m_to_last_break":
            if reps[-1]["name"] == "break":
                reps[-1]["minutes"] += 1
        
        if action == "remove_1m_to_last_break":
            if reps[-1]["name"] == "break":
                reps[-1]["minutes"] -= 1
            
        text, kb = kbs.get_day_setting_by_name("reps", day, day_data)
        await message.edit_text(text, reply_markup=kb)
        await db.udpate_user_trainings(user_data.id, {'days_data': days})
        
@router.callback_query(callback_filters.UserEditDay.filter(F.rep_name != " "))
async def setting_rep_name(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user

    day = callback_data.day
    rep_name = callback_data.rep_name

    user = await db.get_user(user_data.id)
    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    
    day_data = days[day]
    reps = day_data["reps"]

    reps.append(
        {"name": rep_name}
    )
    reps.append(
        {
            "name": "break",
            "minutes": 3,
            "seconds": 0
        }
    )  

    text, kb = kbs.get_day_setting_by_name("reps", day, day_data)
    await message.edit_text(text, reply_markup=kb)

    await db.udpate_user_trainings(user_data.id, {'days_data': days})