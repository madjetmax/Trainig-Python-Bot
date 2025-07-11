from copy import deepcopy
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
        selected_days[switch_day] = {"selected_part": "arms", "reps": []}

    # sorting days by number of day in WEEK_DAYS_SORT
    selected_days = {k: d for k, d in sorted(selected_days.items(), key=lambda x: WEEK_DAYS_SORT[x[0]])}

    # edit message
    text, kb, _ = await kbs.get_user_menu("get_edit_trainings_days", user_data, lang=user.lang, selected_days=selected_days, user=user)
    await message.edit_text(text=text, reply_markup=kb)
    # save to database
    await db.udpate_user_trainings(user_data.id, {"days_data": selected_days})

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

    # edit message
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
        for msg_text, msg_kb in messages:
            msg = await message.answer(text=msg_text, reply_markup=msg_kb)
            messages_to_delete.append(msg.message_id)
        # delete message
        await message.delete()
        await state.update_data(messages_to_delete=messages_to_delete)
    else: 
        messages_to_delete = state_data.get("messages_to_delete")
        if messages_to_delete: # send new message and delete messages_to_delete from state
            await message.answer(text=text, reply_markup=kb)
            
            # delete messages
            await delete_messages(message.bot, user_data.id, messages_to_delete)
            await state.update_data(
                messages_to_delete=[]
            )
        else: # edit message
            try: # if user has no finished trainings
                await message.edit_text(text=text, reply_markup=kb)
            except TelegramBadRequest:
                await call.answer()
    
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

    day_data = user.trainings.days_data[day]
    all_body_parts = user.trainings.all_body_parts
    
    # edit message
    text, kb = kbs.get_day_setting_by_name(setting, day, day_data, lang=user.lang, all_body_parts=all_body_parts, user=user)
    await message.edit_text(text=text, reply_markup=kb)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass

# *body part
# to set body_part for all days
@router.callback_query(callback_filters.UserEditDay.filter(F.use_body_part_for_all_days)) # check if True
async def set_body_part_for_all_days(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id
    user_data = call.from_user

    selected_day = callback_data.day

    user = await db.get_user(user_data.id)
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    # get day data and selected part 
    days = user.trainings.days_data
    day_data = days[selected_day]
    part = day_data["selected_part"]

    if part != " ":
        # send confirm
        text, kb = kbs.get_confirm_use_body_part_for_all_days(selected_day, part, lang)
        await message.edit_text(text, reply_markup=kb)
    await call.answer()

# confirm
@router.callback_query(callback_filters.UserEditDay.filter(F.confirm_use_body_part_for_all_days != " ")) 
async def confirm_body_part_for_all_days(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id
    user_data = call.from_user

    selected_day = callback_data.day
    part_ind = callback_data.body_part_ind
    confirm = callback_data.confirm_use_body_part_for_all_days

    user = await db.get_user(user_data.id)
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    days: dict = user.trainings.days_data
    all_body_parts = user.trainings.all_body_parts

    # get day data and selected part 
    day_data = days[selected_day]
    part = day_data["selected_part"]

    # edit message
    text, kb = kbs.get_day_setting_by_name("workout_body_part", selected_day, days[selected_day],  lang=lang, all_body_parts=all_body_parts, user=user)
    await message.edit_text(text, reply_markup=kb)

    # "1" = True, "0" = False
    if confirm == "1": # check if confirm 
        # setting for all days
        for day in days.keys():
            days[day]["selected_part"] = part

        # updata user trainings
        await db.udpate_user_trainings(
            user_data.id, {"days_data": days}
        )

@router.callback_query(callback_filters.UserEditDay.filter(F.body_part_ind != -1))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    user_data = call.from_user
    chat_id = message.chat.id

    part_ind = callback_data.body_part_ind
    day = callback_data.day

    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    all_body_parts = user.trainings.all_body_parts

    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    day_data = days[day]
    # get part name
    all_body_parts = user.trainings.all_body_parts
    part = all_body_parts[part_ind]["name"]    

    if days[day]["selected_part"] == part:
        await call.answer("")
        return

    days[day]["selected_part"] = part
    day_data["selected_part"] = part

    # edit message
    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data,  lang=lang, all_body_parts=all_body_parts, user=user)
    await message.edit_text(text, reply_markup=kb)
    
    # update user trainings
    await db.udpate_user_trainings(user_data.id, {"days_data": days})

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

    
    # user
    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    msg = await message.answer(texts.new_body_part_name[lang])

    # get and add message to delete
    messages_to_delete: list = state_data["messages_to_delete"]
    messages_to_delete.append(msg.message_id)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        
    # set and update state
    await state.set_state(states.UserEditData.new_body_part)
    await state.update_data(
        selected_day=selected_day,
        message_to_update=message.message_id,
        message_title_to_delete=msg.message_id
    )

# *resp
# confirm
@router.callback_query(callback_filters.UserEditDay.filter(F.confirm_use_reps_for_all_days != " ")) 
async def confirm_reps_for_all_days(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id
    user_data = call.from_user

    selected_day = callback_data.day
    confirm = callback_data.confirm_use_reps_for_all_days

    user = await db.get_user(user_data.id)
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    # getting days and their data
    days: dict = user.trainings.days_data
    reps = days[selected_day]["reps"]

    # edit message
    text, kb = kbs.get_day_setting_by_name("reps", selected_day, days[selected_day], lang=lang)
    await message.edit_text(text, reply_markup=kb)

    # "1" = True, "0" = False
    if confirm == "1": # check if confirm 
        # setting for all days
        for day in days.keys():
            days[day]["reps"] = reps

        # updata user trainings
        await db.udpate_user_trainings(
            user_data.id, {"days_data": days}
        )

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
    
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    all_reps_names = user.trainings.all_reps_names

    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    
    day_data = days[day]
    reps = day_data["reps"]

    if action == "add_rep":
        # send new rep name setting 
        text, kb = kbs.get_rep_name_setting(day, all_reps_names, lang)
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
                reps[-1]["minutes"] = max(0, reps[-1]["minutes"])

        if action == "copy_last_rep":
            last_rep = deepcopy(reps[-2])
            last_break = deepcopy(reps[-1])

            reps.append(last_rep)
            reps.append(last_break)
        
        if action == "user_for_all_days":
            # send confirm message
            text, kb = kbs.get_confirm_use_reps_for_all_days(day, lang)
            await message.edit_text(text, reply_markup=kb)
            return
        
        # edit message after setting
        text, kb = kbs.get_day_setting_by_name("reps", day, day_data, lang=lang)
        await message.edit_text(text, reply_markup=kb)
        await db.udpate_user_trainings(user_data.id, {'days_data': days})
    
    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        
        
@router.callback_query(callback_filters.UserEditDay.filter(F.rep_name_ind != -1))
async def setting_rep_name(call: CallbackQuery, callback_data: callback_filters.UserEditDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    user_data = call.from_user

    day = callback_data.day
    rep_name_ind = callback_data.rep_name_ind

    user = await db.get_user(user_data.id)
    if user == None:
        await call.answer() 
    lang = user.lang

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return
    
    days = user.trainings.days_data

    if days == None:
        await call.answer("")
        return
    
    # get rep name
    all_reps_names = user.trainings.all_reps_names
    rep_name = all_reps_names[rep_name_ind]["name"]
    
    # update reps
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

    # edit message
    text, kb = kbs.get_day_setting_by_name("reps", day, day_data, lang=lang)
    await message.edit_text(text, reply_markup=kb)

    # update user trainings
    await db.udpate_user_trainings(user_data.id, {'days_data': days})

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

    state_data = await state.get_data()
    if state_data.get('timer'):
        await call.answer(texts.cant_edit_at_training[lang])
        return

    msg = await message.answer(texts.new_rep_name[lang])

    # get and add message to delete
    messages_to_delete: list = state_data["messages_to_delete"]
    messages_to_delete.append(msg.message_id)

    # set and update state
    await state.set_state(states.UserEditData.new_rep_name)
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