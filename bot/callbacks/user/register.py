from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message

from config import *

# states
from aiogram.fsm.context import FSMContext
from states import user as states

from keyboards import callback_filters
from keyboards.user import register as kbs
from texts import user as texts
import database as db

router = Router()

async def delete_messages(bot: Bot, chat_id, messages):
    if messages:
        await bot.delete_messages(chat_id, messages)


# *user training setup on start
@router.callback_query(callback_filters.UserConfirmSetupNavigate.filter())
async def setup_navigate(call: CallbackQuery, callback_data: callback_filters.UserConfirmSetupNavigate, state: FSMContext):
    message: Message = call.message
    bot: Bot = message.bot
    chat_id = message.chat.id

    kb_num = callback_data.kb_num
    to = callback_data.to
    day = callback_data.day

    if kb_num >= 0:
        if kb_num == 0:
            state_data = await state.get_data()
            kb = kbs.get_setup_start(selected_days=state_data.get("days", {}))
            await message.answer(
                "choose days",
                reply_markup=kb
            )

            messages_to_delete = state_data.get("messages_to_delete", [])
            await delete_messages(bot, chat_id, messages_to_delete)

        if kb_num == 1:
            
            selected_days = (await state.get_data()).get("days")
            days_list = kbs.get_selected_days_list(selected_days)

            # adding messages to delete
            state_data = await state.get_data()
            messages_to_delete = state_data.get("messages_to_delete", [])

            for text, kb in days_list:
                msg = await message.answer(text, reply_markup=kb)
                messages_to_delete.append(msg.message_id)

            await state.update_data(messages_to_delete=messages_to_delete)

            await state.set_state(states.UserSetUp.days) # set this to evoid user input and saving the time

            await message.delete()

        if kb_num == 2:
            kb = kbs.get_back_to_days_settings()
            await message.answer("enter time when you want to start training", reply_markup=kb)

            await state.set_state(states.UserSetUp.time_start)
            state_data = await state.get_data()
            
            messages_to_delete = state_data.get("messages_to_delete", [])
            await delete_messages(bot, chat_id, messages_to_delete)

    elif to != " ":
        if to == "selected_days_list":
            kb = kbs.get_selected_day(day)
            await message.edit_text(kb[0], reply_markup=kb[1])

@router.callback_query(callback_filters.UserConfirmSetup.filter())
async def confirm_setup(call: CallbackQuery, callback_data: callback_filters.UserConfirmSetup, state: FSMContext):
    message: Message = call.message

    call_data = callback_data.data
    if call_data == "confirm":
        await state.clear()

        await state.set_state(states.UserSetUp.days)
        kb = kbs.get_setup_start()
        await message.edit_text(
            "choose days",
            reply_markup=kb
        )
    elif call_data == "cancel":
        await message.edit_text("You can always setup your trainings by command /trainings")
        

@router.callback_query(callback_filters.UserChooseDay.filter())
async def choose_day(call: CallbackQuery, callback_data: callback_filters.UserChooseDay, state: FSMContext):
    message: Message = call.message
    day = callback_data.day

    days = (await state.get_data()).get("days", {})
    if day not in days:
        days[day] = {
            "selected_part": None,
            "reps": [],
        }
    else:
        del days[day]

    new_kb = kbs.get_setup_start(selected_days=days)
    await message.edit_reply_markup(reply_markup=new_kb)

    await state.update_data(
        days=days
    )


@router.callback_query(callback_filters.UserSettingDay.filter(F.setting != " "))
async def setting_day_setting(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message

    day = callback_data.day
    setting = callback_data.setting

    day_data = (await state.get_data()).get("days", {}).get(day, {})

    text, kb = kbs.get_day_setting_by_name(setting, day, day_data)
    await message.edit_text(text=text, reply_markup=kb)

@router.callback_query(callback_filters.UserSettingDay.filter(F.body_part != " "))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message

    part = callback_data.body_part
    day = callback_data.day


    days = (await state.get_data()).get("days")

    if days == None:
        await call.answer("")
        return
    day_data = days[day]

    days[day]["selected_part"] = part
    await state.update_data(days=days)


    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data)

    await message.edit_text(text, reply_markup=kb)

@router.callback_query(callback_filters.UserSettingDay.filter(F.reps_action != " "))
async def setting_day_body_part(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message

    action = callback_data.reps_action
    day = callback_data.day

    days = (await state.get_data()).get("days")

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
            
        await state.update_data(days=days)
        text, kb = kbs.get_day_setting_by_name("reps", day, day_data)
        await message.edit_text(text, reply_markup=kb)

@router.callback_query(callback_filters.UserSettingDay.filter(F.rep_name != " "))
async def setting_rep_name(call: CallbackQuery, callback_data: callback_filters.UserSettingDay, state: FSMContext):
    message = call.message

    day = callback_data.day
    rep_name = callback_data.rep_name

    days = (await state.get_data()).get("days")

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

    await state.update_data(days=days)
    text, kb = kbs.get_day_setting_by_name("reps", day, day_data)
    await message.edit_text(text, reply_markup=kb)


# todo user edit trainig. I future i need to add this feature
@router.callback_query(callback_filters.UserEditTrainingConfirm.filter())
async def confirm_edit_training(call: CallbackQuery, callback_data: callback_filters.UserEditTrainingConfirm, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user

    call_data = callback_data.data
    if call_data == "confirm":
        deleted = await db.delete_user_trainings(user_data.id)

    elif call_data == "cancel":
        await message.delete()