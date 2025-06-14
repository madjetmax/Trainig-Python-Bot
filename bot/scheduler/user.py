from aiogram import Bot
from aiogram.types import Message
import datetime


from config import *
from . import scheduler

import database as db
from database.models import User

from keyboards.user import training  as training_kbs
from keyboards.user import register as register_kbs
from keyboards.user import menu as menu_kbs

from texts import user as texts


day_from_full_name = {
    "Monday": "mon",
    "Tuesday": "tue",
    "Wednesday": "wed",
    "Thursday": "thu",
    "Friday": "fri",
    "Saturday": "sat",
    "Sunday": "sun",
}

# *trainings
async def start_all_users_training_reminds(bot: Bot):
    now = datetime.datetime.now()

    all_users = await db.get_all_users()
    for user in all_users:
        trainings = user.trainings

        if trainings:

            days_data = trainings.days_data

            create_training_remind(
                bot, user.id, 
                days_data, 
                trainings.time_start_hours, 
                trainings.time_start_minutes,
            )
    
async def send_trainig_remind(bot: Bot, user_id: int):
    user = await db.get_user(user_id)
    lang = user.lang

    text = texts.its_training_time[lang]
    kb = training_kbs.get_start_training(lang)

    await bot.send_message(user.id, text, reply_markup=kb)

def create_training_remind(bot: Bot, user_id, days: list, hours, minutes):
    # convert days to clear days, ex: Friday -> fri
    days = [day_from_full_name.get(d, d) for d in days]
    now = datetime.datetime.now()

    # get job
    job_id = f'send_training_remind_{user_id}'
    job = scheduler.get_job(job_id)

    if job: # restart if job already exists
        restart_training_remind(job_id, bot, user_id, days, hours, minutes)
    else:
        scheduler.add_job(
            send_trainig_remind, 'cron', 
            day_of_week=", ".join(days), 
            hour=hours, 
            minute=minutes, 
            second=SCHD_TRAINING_START_SECONDS,
            args=(bot, user_id), 
            id=job_id
        )

def restart_training_remind(job_id, bot: Bot, user_id, days: list, hours, minutes):
    # convert days to clear days, ex: Friday -> fri
    days = [day_from_full_name.get(d, d) for d in days]

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
            args=(bot, user_id), 
            id=job_id
        )
        return True
    return False