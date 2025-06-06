from aiogram import Router, F, Bot
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
        text, kb, messages = await kbs.get_user_menu(0)

        await message.answer(text, reply_markup=kb)

        await state.set_state(states.UserEditData)
    else:
        await message.answer(texts.register)

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
async def get_new_start_time(message: Message, state: FSMContext):
    valid_time = check_time_valid(message.text)

    if valid_time:
        message_id = message.message_id
        chat_id = message.chat.id
        bot: Bot = message.bot
        user_data = message.from_user

        # update state
        await state.update_data(
            time_start=message.text
        )

        # delete messages
        await message.delete()
        msg = await message.answer("New time was set!", reply_markup=None)

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
            bot, user_data.id, 
            days, 
            hours, minutes
        )

        await asyncio.sleep(1)
        # send user menu from trainings page
        text, kb, _ = await kbs.get_user_menu(-1, "get_edit_trainings", user_data)
        
        await message.answer(text, reply_markup=kb)
    else:
        await message.answer("Invalid time!")

