from copy import deepcopy
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message

from config import *

# states
from aiogram.fsm.context import FSMContext
from states import user as states

from keyboards import callback_filters
from keyboards.user import register as kbs
from keyboards.user import menu as menu_kbs

from texts import user as texts
import database as db

router = Router()

async def delete_messages(bot: Bot, chat_id, messages):
    if messages:
        await bot.delete_messages(chat_id, messages)

# *user training setup on start
# choose lang 
@router.callback_query(callback_filters.UserChooseLang.filter())
async def choose_lang(call: CallbackQuery, callback_data: callback_filters.UserChooseLang, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user

    lang = callback_data.lang

    # send setup
    kb = kbs.confirm_setup(lang)
    await message.edit_text(texts.start_training_set_up[lang].format(name=user_data.full_name), reply_markup=kb)

    # update user
    await db.update_user(user_data.id, {'lang': lang})

@router.callback_query(callback_filters.UserConfirmSetupNavigate.filter())
async def setup_navigate(call: CallbackQuery, callback_data: callback_filters.UserConfirmSetupNavigate, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user
    bot: Bot = message.bot
    chat_id = message.chat.id

    kb_num = callback_data.kb_num
    to = callback_data.to
    day = callback_data.day

    if kb_num >= 0:
        if kb_num == 0: # get choose days 
            state_data = await state.get_data()
            lang = state_data["user_lang"]

            # send message
            kb = kbs.get_days_choice(selected_days=state_data["days"], lang=lang)
            await message.answer(
                texts.choose_days_title[lang],
                reply_markup=kb
            )

            # delete messages to delete
            messages_to_delete = state_data.get("messages_to_delete", [])
            await delete_messages(bot, chat_id, messages_to_delete)

            # update and set state 
            await state.update_data(messages_to_delete=[])
            await state.set_state(states.UserSetUp.days)

        if kb_num == 1: # get days to setting, ex: body part, reps
            state_data = await state.get_data()
            lang = state_data["user_lang"]

            # get selected days list to send
            selected_days = state_data.get("days", {})
            days_list = kbs.get_selected_days_list(selected_days, lang=lang)

            if len(selected_days) <= 0:
                await call.answer(texts.at_least_one_day_answer[lang])
                return

            # adding messages to delete
            messages_to_delete = state_data.get("messages_to_delete", [])

            # send messages
            for text, kb in days_list:
                msg = await message.answer(text, reply_markup=kb)
                messages_to_delete.append(msg.message_id)

            await message.delete()

            # update and set state
            await state.update_data(messages_to_delete=messages_to_delete)
            await state.set_state(states.UserSetUp.days) # set this to evoid user input and saving the time

        if kb_num == 2: # get start time
            state_data = await state.get_data()
            lang = state_data["user_lang"]

            # check if every day has body part and reps
            days: dict = state_data["days"]
            for key, data in days.items():
                day_name = texts.trans_days_of_week[lang][key] # get day_name on lang by its key

                # for body part
                if data["selected_part"] is None:
                    answer = texts.set_body_part_answer[lang].format(day=day_name)
                    await call.answer(answer)
                    return
                
                # for reps
                if data["reps"] == []:
                    answer = texts.set_reps_answer[lang].format(day=day_name)
                    await call.answer(answer)
                    return

            # send message
            kb = kbs.get_back_to_days_settings(lang)
            await message.answer(texts.workout_start_time[lang], reply_markup=kb, parse_mode="HTML")

            # delete messages to delete
            messages_to_delete = state_data.get("messages_to_delete", [])
            await delete_messages(bot, chat_id, messages_to_delete)

            # set and update state
            await state.set_state(states.UserSetUp.time_start)
            await state.update_data(
                messages_to_delete=[]
            )

    elif to != " ": 
        if to == "day_setting": # send selected day, ex: body part, reps. if back to selected days list
            state_data = await state.get_data()
            lang = state_data["user_lang"]

            # send message
            kb = kbs.get_selected_day(day, lang)
            await message.edit_text(kb[0], reply_markup=kb[1])

            await state.set_state(states.UserSetUp.days)

            try:
                await bot.delete_message(
                    chat_id=chat_id, message_id=state_data["message_title_to_delete"]
                )
            except Exception:
                pass

        if to == "day_reps_setting": # send reps setting buttons and added reps list 
            state_data = await state.get_data()
            lang = state_data["user_lang"]
            day_data = state_data.get("days", {}).get(day, {})

            # send message
            text, kb = kbs.get_day_setting_by_name("reps", day, day_data, state_data, lang)
            await message.edit_text(text, reply_markup=kb)

            await state.set_state(states.UserSetUp.days)

            try:
                await bot.delete_message(
                    chat_id=chat_id, message_id=state_data["message_title_to_delete"]
                )
            except Exception:
                pass

@router.callback_query(callback_filters.UserConfirmSetup.filter())
async def confirm_setup(call: CallbackQuery, callback_data: callback_filters.UserConfirmSetup, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user

    data = callback_data.data

    # get user and lang 
    user = await db.get_user(user_data.id)
    lang = user.lang

    if data == "confirm":
        # get kb and send message
        kb = kbs.get_days_choice(lang=user.lang)
        await message.edit_text(
            texts.choose_days_title[user.lang],
            reply_markup=kb
        )

        # set and update state
        await state.clear()

        await state.set_state(states.UserSetUp.days)
        await state.update_data(
            user_lang=user.lang,
            all_body_parts=ALL_BODY_PARTS,
            all_reps_names=ALL_REPS_NAMES,
            days={}
        )
    elif data == "cancel":
        await message.edit_text(texts.can_setup_trainigns[lang])

@router.callback_query(callback_filters.UserChooseDay.filter())
async def choose_day(call: CallbackQuery, callback_data: callback_filters.UserChooseDay, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user

    day = callback_data.day

    state_data = await state.get_data()

    # get and update selected days
    selected_days: list = state_data.get("days")

    if selected_days is None:
        await call.answer()
        return
    lang = state_data["user_lang"]
    
    # add or remove day from selected days 
    if day not in selected_days:
        selected_days[day] = {
            "selected_part": None,
            "reps": [],
        }
    else:
        if len(selected_days) <= 1:
            await call.answer(texts.at_least_one_day_answer[lang])
            return
        
        del selected_days[day]

    # sorting days by number of day in WEEK_DAYS_SORT
    selected_days = {k: d for k, d in sorted(selected_days.items(), key=lambda x: WEEK_DAYS_SORT[x[0]])}

    # edit message
    new_kb = kbs.get_days_choice(selected_days=selected_days, lang=lang)
    await message.edit_reply_markup(reply_markup=new_kb)

    # update state
    await state.update_data(
        days=selected_days
    )

# setting day, ex: body part, reps
@router.callback_query(callback_filters.UserSettingDay.filter(F.setting != " "))
async def setting_day_setting(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    day = callback_data.day
    setting = callback_data.setting

    state_data = await state.get_data()

    days = state_data.get("days")

    if days is None:
        await call.answer()
        return
    lang = state_data["user_lang"]

    day_data = days.get(day, {})
    
    # edit message
    text, kb = kbs.get_day_setting_by_name(setting, day, day_data, state_data, lang)
    await message.edit_text(text=text, reply_markup=kb)

    await state.set_state(states.UserSetUp.days)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        

# *body part
# to set body_part for all days
@router.callback_query(callback_filters.UserSettingDay.filter(F.use_body_part_for_all_days)) # check if True
async def set_body_part_for_all_days(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    selected_day = callback_data.day

    state_data = await state.get_data()
    lang = state_data["user_lang"]

    # get day data and selected part 
    days = state_data["days"]
    day_data = days[selected_day]
    part = day_data["selected_part"]

    if part is not None: 
        # send confirm
        text, kb = kbs.get_confirm_use_body_part_for_all_days(selected_day, part, lang)
        await message.edit_text(text, reply_markup=kb)
    await call.answer()

# confirm
@router.callback_query(callback_filters.UserSettingDay.filter(F.confirm_use_body_part_for_all_days != " ")) 
async def confirm_body_part_for_all_days(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    selected_day = callback_data.day
    part_ind = callback_data.body_part_ind
    confirm = callback_data.confirm_use_body_part_for_all_days

    state_data = await state.get_data()
    lang = state_data["user_lang"]
    days: dict = state_data["days"]

    # get selected part
    day_data = days[selected_day]
    part = day_data["selected_part"]

    # "1" = True, "0" = False
    if confirm == "1": # check if confirm 
        # setting for all days
        for day in days.keys():
            days[day]["selected_part"] = part

        await state.update_data(
            days=days
        )
    # edit message
    text, kb = kbs.get_day_setting_by_name("workout_body_part", selected_day, days[selected_day], state_data, lang)
    await message.edit_text(text, reply_markup=kb)

# *set body part for day
@router.callback_query(callback_filters.UserSettingDay.filter(F.body_part_ind != -1))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    part_ind = callback_data.body_part_ind
    day = callback_data.day

    state_data = await state.get_data()
    
    # get and update days 
    days = state_data.get("days")

    # answer empty callback
    if days is None:
        await call.answer()
        return
    
    # get part from ind
    all_body_parts = state_data["all_body_parts"]

    part = all_body_parts[part_ind]["name"]
    
    if days[day]["selected_part"] == part:
        await call.answer()
        return
    
    lang = state_data["user_lang"]

    # update selected part
    day_data = days[day]
    days[day]["selected_part"] = part

    # get kb and send message
    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data, state_data, lang)
    await message.edit_text(text, reply_markup=kb)

    await state.set_state(states.UserSetUp.days)
    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        
@router.callback_query(callback_filters.UserSettingDay.filter(F.add_custom_body_part)) # check if True
async def setting_custom_body_part(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    selected_day = callback_data.day

    state_data = await state.get_data()

    if state_data.get("days") is None:
        await call.answer("")
        return
    lang = state_data["user_lang"]
    
    # send message
    msg = await message.answer(texts.new_body_part_name[lang])

    # get and add message to delete
    messages_to_delete: list = state_data["messages_to_delete"]
    messages_to_delete.append(msg.message_id)

    # set state
    await state.set_state(states.UserSetUp.new_body_part)
    
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

# *reps
# confirm
@router.callback_query(callback_filters.UserSettingDay.filter(F.confirm_use_reps_for_all_days != " ")) 
async def confirm_reps_for_all_days(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    selected_day = callback_data.day
    confirm = callback_data.confirm_use_reps_for_all_days

    state_data = await state.get_data()
    lang = state_data["user_lang"]

    # getting days and their data
    days: dict = state_data["days"]
    reps = days[selected_day]["reps"]

    # "1" = True, "0" = False
    if confirm == "1": # check if confirm 
        # setting for all days
        for day in days.keys():
            days[day]["reps"] = reps

        await state.update_data(
            days=days
        )

    # edit message
    text, kb = kbs.get_day_setting_by_name("reps", selected_day, days[selected_day], state_data, lang)
    await message.edit_text(text, reply_markup=kb)

@router.callback_query(callback_filters.UserSettingDay.filter(F.reps_action != " "))
async def setting_reps(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    action = callback_data.reps_action
    day = callback_data.day

    state_data = await state.get_data()

    days = state_data.get("days")

    if days is None:
        await call.answer("")
        return
    
    lang = state_data["user_lang"]
    
    day_data = days[day]
    reps = day_data["reps"]

    all_reps_names = state_data["all_reps_names"]

    if action == "add_rep":
        # send rep name choose
        text, kb = kbs.get_rep_name_setting(day, all_reps_names, lang)
        await message.edit_text(text, reply_markup=kb)

    else: # other reps controll
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

        # edit message                    
        text, kb = kbs.get_day_setting_by_name("reps", day, day_data, state_data, lang)
        await message.edit_text(text, reply_markup=kb)

        await state.update_data(days=days)

    await state.set_state(states.UserSetUp.days)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 
        

@router.callback_query(callback_filters.UserSettingDay.filter(F.rep_name_ind != -1))
async def setting_rep_name(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    day = callback_data.day
    rep_name_ind = callback_data.rep_name_ind

    state_data = await state.get_data()
    
    days = state_data.get("days")

    if days is None:
        await call.answer("")
        return
    
    lang = state_data["user_lang"]

    # get rep name 
    all_reps_names = state_data["all_reps_names"]
    rep_name = all_reps_names[rep_name_ind]["name"]
    
    # udpate reps
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
    text, kb = kbs.get_day_setting_by_name("reps", day, day_data, state_data, lang)
    await message.edit_text(text, reply_markup=kb)

    # set and update state
    await state.set_state(states.UserSetUp.days)
    await state.update_data(days=days)

    # delete message title
    try:
        await message.bot.delete_message(
            chat_id=chat_id, message_id=state_data["message_title_to_delete"]
        )
    except Exception as ex:
        pass 


@router.callback_query(callback_filters.UserSettingDay.filter(F.add_custom_rep_name)) # check if True
async def setting_custom_rep_name(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message
    chat_id = message.chat.id

    selected_day = callback_data.day

    state_data = await state.get_data()

    if state_data.get("days") is None:
        await call.answer("")
        return
    
    lang = state_data["user_lang"]

    msg = await message.answer(texts.new_rep_name[lang])

    # get and add message to delete
    messages_to_delete: list = state_data["messages_to_delete"]
    messages_to_delete.append(msg.message_id)

    # set state
    await state.set_state(states.UserSetUp.new_rep_name)
    
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

# *user edit trainig
@router.callback_query(callback_filters.UserEditTrainingConfirm.filter())
async def confirm_edit_training(call: CallbackQuery, callback_data: callback_filters.UserEditTrainingConfirm, state: FSMContext):
    message: Message = call.message
    chat_id = message.chat.id

    user_data = call.from_user
    user = await db.get_user(user_data.id)
    if user is None:
        call.answer()
    
    lang = user.lang

    call_data = callback_data.data
    if call_data == "confirm":
        text, kb, _ = await menu_kbs.get_user_menu("get_edit_trainings", user_data, lang=lang)

        await message.edit_text(text, reply_markup=kb)

    elif call_data == "cancel":
        await message.delete()