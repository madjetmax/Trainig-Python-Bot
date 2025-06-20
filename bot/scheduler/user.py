from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext

import datetime

from config import *
from . import scheduler

import database as db
from database.models import User

from keyboards.user import training  as training_kbs
from keyboards.user import register as register_kbs
from keyboards.user import menu as menu_kbs

from texts import user as texts

# *trainings
async def start_all_users_training_reminds(bot: Bot, dp: Dispatcher):
    now = datetime.datetime.now()

    all_users = await db.get_all_users()

    # start shedule task to notify users trainings
    for user in all_users:
        trainings = user.trainings

        if trainings:
            days_data = trainings.days_data

            # create task
            create_training_remind(
                bot, dp,
                user.id, 
                days_data, 
                # now.time().hour,
                # now.time().minute,
                trainings.time_start_hours, 
                trainings.time_start_minutes,
            )
    
async def send_trainig_remind(bot: Bot, dp: Dispatcher, user_id: int):
    user = await db.get_user(user_id)
    lang = user.lang

    # get user state
    storage_key = StorageKey(
        bot.id, user_id, user_id
    )
    state = FSMContext(
        storage=dp.storage,
        key=storage_key
    )

    # get data 
    state_data = await state.get_data()

    if state_data.get("timer"): # check if user on training
        return
    
    # else send start message
    text = texts.its_training_time[lang]
    kb = training_kbs.get_start_training(lang)

    await bot.send_message(user.id, text, reply_markup=kb)

def create_training_remind(bot: Bot, dp: Dispatcher, user_id, days: list, hours, minutes):
    now = datetime.datetime.now()

    # get job
    job_id = f'send_training_remind_{user_id}'
    job = scheduler.get_job(job_id)

    if job: # restart if job already exists
        restart_training_remind(job_id, bot, dp, user_id, days, hours, minutes)
    else:
        scheduler.add_job(
            send_trainig_remind, 'cron', 
            day_of_week=", ".join(days), 
            hour=hours,
            minute=minutes,
            second=SCHD_TRAINING_START_SECONDS,
            # second=now.time().second + 1,
            args=(bot, dp, user_id), 
            id=job_id
        )

def restart_training_remind(job_id, bot: Bot, dp: Dispatcher, user_id, days: list, hours, minutes):
    # get job
    job_id = f'send_training_remind_{user_id}'
    job = scheduler.get_job(job_id)

    if job: # start job if found 
        scheduler.remove_job(job_id)
        scheduler.add_job(
            send_trainig_remind, 'cron', 
            day_of_week=", ".join(days), 
            hour=hours, 
            minute=minutes, 
            second=SCHD_TRAINING_START_SECONDS,
            args=(bot, dp, user_id), 
            id=job_id
        )
        return True
    return False