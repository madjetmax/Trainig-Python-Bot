from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from config import *
from aiogram.exceptions import TelegramBadRequest

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
async def user_menu_switch_day(call: CallbackQuery, callback_data: callback_filters.UserEditData, state: FSMContext):
    message = call.message
    user_data = call.from_user

    state_data = await state.get_data()

    user = await db.get_user(user_data.id)

    if user == None:
        await call.answer()

    lang = user.lang
    if state_data.get('timer'):

        await call.answer(texts.cant_edit_at_training[lang])
        return

    switch_day = callback_data.switch_day
    

    # get and update selected days
    selected_days = user.trainings.days_data

    if switch_day in selected_days:
        if len(selected_days) > 1:
            selected_days.pop(switch_day)
        else:
            await call.answer(texts.at_least_one_day_answer[lang])
            return
    else:
        selected_days[switch_day] = {"selected_part": "legs", "reps": []}

    await db.udpate_user_trainings(user_data.id, {"days_data": selected_days})

    # edit message
    text, kb, _ = await kbs.get_user_menu("get_edit_trainings_days", user_data, lang=user.lang, selected_days=selected_days, user=user)

    await message.edit_text(text=text, reply_markup=kb)
    

@router.callback_query(callback_filters.UserEditData.filter(F.back_to_day != " "))
async def back_to_day_setting(call: CallbackQuery, callback_data: callback_filters.UserEditData, state: FSMContext):
    message = call.message
    chat_id = message.chat.id
    user_data = call.from_user

    state_data = await state.get_data()
    user = await db.get_user(user_data.id)

    if user == None:
        await call.answer()

    lang = user.lang

    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    to = callback_data.to
    back_to_day = callback_data.back_to_day

    text, kb, _ = await kbs.get_user_menu(to, user_data, lang=lang, day=back_to_day, user=user)

    await message.edit_text(text, reply_markup=kb)

    # setting state to days
    await state.set_state(states.UserEditData.days)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 

# set new lang 
@router.callback_query(callback_filters.UserEditData.filter(F.set_lang != " "))
async def set_lang(call: CallbackQuery, callback_data: callback_filters.UserEditData, state: FSMContext):
    message = call.message
    chat_id = message.chat.id
    user_data = call.from_user

    # updating_lang
    lang = callback_data.set_lang
    user = await db.update_user(user_data.id, {
        "lang": lang
    })
    if user == None:
        await call.answer()
    
    try: # if current lang == set_lang, avoid errors
        # edit message
        text, kb, _ = await kbs.get_user_menu("edit_lang", user_data, lang, user=user)
        await message.edit_text(text, reply_markup=kb)

    except TelegramBadRequest:
        await call.answer()

@router.callback_query(callback_filters.UserEditData.filter())
async def user_menu(call: CallbackQuery, callback_data: callback_filters.UserEditData, state: FSMContext):
    message = call.message
    chat_id = message.chat.id
    user_data = call.from_user
    
    state_data = await state.get_data()
    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer()

    lang = user.lang
    
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    to = callback_data.to

    text, kb, messages = await kbs.get_user_menu(to, user_data, lang, user=user)

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

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 


# *day settings, body part, reps
@router.callback_query(callback_filters.UserEditDay.filter(F.setting != " "))
async def setting_day_setting(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user
    chat_id = message.chat.id

    state_data = await state.get_data()

    # user
    user = await db.get_user(user_data.id)   
    if user == None:
        await call.answer() 
    lang = user.lang
    
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    day = callback_data.day
    setting = callback_data.setting

    user = await db.get_user(user_data.id)
    day_data = user.trainings.days_data[day]
    all_body_parts = user.trainings.all_body_parts

    text, kb = kbs.get_day_setting_by_name(setting, day, day_data, lang=user.lang, all_body_parts=all_body_parts, user=user)
    await message.edit_text(text=text, reply_markup=kb)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        

@router.callback_query(callback_filters.UserEditDay.filter(F.body_part != " "))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user
    chat_id = message.chat.id

    part = callback_data.body_part
    day = callback_data.day

    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 

    all_body_parts = user.trainings.all_body_parts

    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    day_data = days[day]

    if days[day]["selected_part"] == part:

        await call.answer("")
        return

    days[day]["selected_part"] = part
    day_data["selected_part"] = part

    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data,  lang=user.lang, all_body_parts=all_body_parts, user=user)

    await message.edit_text(text, reply_markup=kb)

    await db.udpate_user_trainings(user_data.id, {"days_data": days})

    state_data = await state.get_data()

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        

@router.callback_query(callback_filters.UserEditDay.filter(F.add_custom_body_part)) # check if True
async def setting_custom_body_part(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user
    chat_id = message.chat.id

    selected_day = callback_data.day

    state_data = await state.get_data()

    # user
    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
    lang = user.lang

    msg = await message.answer(texts.new_body_part_name[lang])

    # get and add message to delete
    messages_to_delete: list = state_data["messages_to_delete"]
    messages_to_delete.append(msg.message_id)

    # set state
    await state.set_state(states.UserEditData.new_body_part)
    
    # update state 
    await state.update_data(
        selected_day=selected_day,
        message_to_update=message.message_id,
        message_title_to_delete=msg.message_id
    )

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        

# *resp
@router.callback_query(callback_filters.UserEditDay.filter(F.reps_action != " "))
async def setting_reps(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    user_data = call.from_user

    action = callback_data.reps_action
    day = callback_data.day

    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
    all_reps_names = user.trainings.all_reps_names

    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    
    day_data = days[day]
    reps = day_data["reps"]

    if action == "add_rep":
        text, kb = kbs.get_rep_name_setting(day, all_reps_names, user.lang)
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
            
        text, kb = kbs.get_day_setting_by_name("reps", day, day_data, lang=user.lang)
        await message.edit_text(text, reply_markup=kb)
        await db.udpate_user_trainings(user_data.id, {'days_data': days})
    
    state_data = await state.get_data()
    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        
        
@router.callback_query(callback_filters.UserEditDay.filter(F.rep_name != " "))
async def setting_rep_name(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    user_data = call.from_user

    day = callback_data.day
    rep_name = callback_data.rep_name

    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
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

    text, kb = kbs.get_day_setting_by_name("reps", day, day_data, lang=user.lang)
    await message.edit_text(text, reply_markup=kb)

    await db.udpate_user_trainings(user_data.id, {'days_data': days})

    state_data = await state.get_data()
    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        

@router.callback_query(callback_filters.UserEditDay.filter(F.add_custom_rep_name)) # check if True
async def setting_custom_rep_name(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user
    chat_id = message.chat.id
    
    selected_day = callback_data.day

    state_data = await state.get_data()

    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
    lang = user.lang

    msg = await message.answer(texts.new_rep_name[lang])

    # get and add message to delete
    messages_to_delete: list = state_data["messages_to_delete"]
    messages_to_delete.append(msg.message_id)

    # set state
    await state.set_state(states.UserEditData.new_rep_name)
    
    # update state 
    await state.update_data(
        selected_day=selected_day,
        message_to_update=message.message_id,
        message_title_to_delete=msg.message_id
    )

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        