from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import asyncio

from config import *

from database.models import User, FinishedUserTraining
import database as db
from keyboards.user import register as kbs
from scheduler import user as schedule_manager

from texts import user as texts
from states import user as states

router = Router()

# registration 
@router.message(CommandStart())
async def start(message: Message):
    user_data = message.from_user

    # check if user created trainings 
    trainings = await db.get_user_trainings(user_data.id)

    if trainings == None:
        kb = kbs.confirm_setup()
        await message.answer(texts.greate.format(name=user_data.full_name), reply_markup=kb)

        # create user
        await db.create_user(user_data.id, user_data.full_name)
        
    else:
        kb = kbs.get_user_edit_training_confirm()
        await message.answer("you have already created trainings, do you want to edit?", reply_markup=kb)


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
    
@router.message(states.UserSetUp.time_start, F.text)
async def get_start_time(message: Message, state: FSMContext):
    valid_time = check_time_valid(message.text)

    if valid_time:
        message_id = message.message_id
        chat_id = message.chat.id
        bot: Bot = message.bot
        user_data= message.from_user

        # update state
        await state.update_data(
            time_start=message.text
        )

        # delete messages
        await message.delete()
        msg = await message.answer("Trainigs set up!", reply_markup=None)

        try:
            await message.bot.delete_message(message.chat.id, message_id-1) 
        except Exception:
            pass

        # get time
        hours = valid_time[0]
        minutes = valid_time[1]

        # save to database
        state_data = await state.get_data()

        await db.create_user_trainigs(
            user_data.id, state_data, hours, minutes
        )

        # start schedule job
        days = list(state_data["days"].keys())
        
        schedule_manager.create_training_remind(
            bot, user_data.id, 
            days, 
            hours, minutes
        )

        await state.clear()

        await asyncio.sleep(2)
        await message.bot.delete_message(chat_id, msg.message_id)
        
    else:
        await message.answer("Invalid time!")
