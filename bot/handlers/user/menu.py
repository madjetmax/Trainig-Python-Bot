from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import asyncio

from config import *

from database.models import User, FinishedUserTraining
import database as db
from keyboards.user import menu as kbs
from scheduler import user as schedule_manager

from texts import user as texts
from states import user as states

router = Router()

# user get info and trainings settings
@router.message(Command(commands=["me"]))
async def get_user_menu(message: Message, state: FSMContext):
    user_data = message.from_user

    user = await db.get_user(user_data.id)

    if user:
        # get and send menu
        text, kb, _ = await kbs.get_user_menu("main", lang=user.lang)

        await message.answer(text, reply_markup=kb)

        await state.set_state(states.UserEditData)
    else:
        lang = user_data.language_code
        await message.answer(texts.register[lang])

# change trainings start time
def check_time_valid(text: str):
    try:    
        if ":" in text:
            hours = int(text.split(":")[0])
            minutes = int(text.split(":")[1]) 
        elif "." in text:   
            hours = int(text.split(".")[0])
            minutes = int(text.split(".")[1])
        else:
            return False
        
        if hours >= 24 or hours < 0:
            return False
        
        if minutes >= 60 or minutes < 0:
            return False

        return hours, minutes
    except Exception as ex:
        print(ex)
        return False
    
@router.message(states.UserEditData.time_start, F.text)
async def get_new_start_time(message: Message, dispatcher: Dispatcher, state: FSMContext):
    message_id = message.message_id
    chat_id = message.chat.id
    bot: Bot = message.bot
    user_data = message.from_user

    valid_time = check_time_valid(message.text)

    if valid_time:
        

        # update and get state
        state_data = await state.update_data(
            time_start=message.text
        )

        user = await db.get_user(user_data.id)
        if user == None:
            return
        lang = user.lang

        # delete messages
        await message.delete()
        msg = await message.answer(texts.new_time_was_set[lang], reply_markup=None)

        try:
            await message.bot.delete_message(message.chat.id, message_id-1) 
        except Exception:
            pass

        # get time
        hours = valid_time[0]
        minutes = valid_time[1]

        # save to database
        update_data = {
            "time_start_hours": hours,
            "time_start_minutes": minutes,
        }
        training = await db.udpate_user_trainings(user_data.id, update_data)

        # start schedule job
        days = list(training.days_data.keys())
        schedule_manager.create_training_remind(
            bot, dispatcher, user_data.id, 
            days, 
            hours, minutes
        )

        await asyncio.sleep(1)
        # send user menu from trainings page
        text, kb, _ = await kbs.get_user_menu("get_edit_trainings", user_data, lang=lang, user=user)
        
        await message.answer(text, reply_markup=kb)
    else:
        # get user and lang
        user = await db.get_user(user_data.id)
        if user == None:
            return
        lang = user.lang

        await message.answer(texts.invalid_time[lang])

# new body part 
@router.message(states.UserEditData.new_body_part, F.text)
async def get_new_body_part(message: Message, state: FSMContext):
    bot: Bot = message.bot

    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id

    user_data = message.from_user

    user = await db.get_user(user_data.id)
    if user == None:
        return
    
    state_data = await state.get_data()

    day = state_data["selected_day"]


    # update body parts
    all_body_parts = user.trainings.all_body_parts
    all_body_parts.append(
        {
            "name": text,
            "en": text,
            "uk": text,
        }
    )

    # get and update days data
    days = user.trainings.days_data
    days[day]["selected_part"] = text
    day_data = days[day]
    
    data = {
        "all_body_parts": all_body_parts,
        "days_data": days,
    }
    await db.udpate_user_trainings(user_data.id, data)

    # delete messages
    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)
    # udpate message to update
    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data, lang=user.lang, all_body_parts=all_body_parts)

    await bot.edit_message_text(
        message_id=state_data["message_to_update"],
        chat_id=chat_id,
        text=text,
        reply_markup=kb
    )

    await state.set_state(states.UserEditData.days)

# new rep name 
@router.message(states.UserEditData.new_rep_name, F.text)
async def get_new_rep_name(message: Message, state: FSMContext):
    bot: Bot = message.bot 

    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id

    user_data = message.from_user
    user = await db.get_user(user_data.id)
    if user == None:
        return
    
    state_data = await state.get_data()

    day = state_data["selected_day"]


    # update body parts
    all_reps_names = user.trainings.all_reps_names
    all_reps_names.append(
        {
            "name": text,
            "en": text,
            "uk": text,
        }
    )

    # get and update days data
    days = user.trainings.days_data
    day_data = days[day]
    
    data = {
        "all_reps_names": all_reps_names,
        "days_data": days,
    }
    await db.udpate_user_trainings(user_data.id, data)

    # delete messages
    await message.delete()
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id-1)
    except Exception:
        pass
        
    # udpate message to update
    text, kb = kbs.get_rep_name_setting(day, all_reps_names, user.lang)

    await bot.edit_message_text(
        message_id=state_data["message_to_update"],
        chat_id=chat_id,
        text=text,
        reply_markup=kb
    )

    await state.set_state(states.UserEditData.days)
