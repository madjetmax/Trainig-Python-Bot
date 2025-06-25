from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext

import datetime
from zoneinfo import ZoneInfo

from config import *
from . import scheduler

import database as db
from database.models import User

from keyboards.user import training  as training_kbs
from keyboards.user import menu as menu_kbs

from texts import user as texts

from utils import user_aura as aura_manager


def set_timezone(date: datetime.datetime) -> datetime.datetime:
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    return date.astimezone(tz)

# *trainings
async def start_all_users_training_reminds(bot: Bot, dp: Dispatcher):
    # now = datetime.datetime.now()

    all_users = await db.get_all_users()

    # start shedule task to notify users trainings and skipped trainigs yesturday
    for user in all_users:
        trainings = user.trainings

        if trainings:
            days_data = trainings.days_data
            # create tasks 
            # trainig
            create_training_remind(
                bot, dp,
                user.id, 
                days_data, 
                # now.time().hour,
                # now.time().minute,
                trainings.time_start_hours, 
                trainings.time_start_minutes,
            )
            # skipped training
            create_skipped_training_remind(
                bot, dp,
                user.id, 
                ALL_WEEK_DAYS, 
                # now.time().hour,
                # now.time().minute,
                SCHD_SEND_TRAINIG_SKIPPED_HOURS,
                SCHD_SEND_TRAINIG_SKIPPED_MINUTES,
            )
    
# *training remind
# scheduler
def create_training_remind(bot: Bot, dp: Dispatcher, user_id, days: list, hours, minutes):
    """use to start remind trainings, also if you want to RESTART remind you can use this too"""
    now = datetime.datetime.now()

    # get job
    job_id = f'send_training_remind_{user_id}'
    job = scheduler.get_job(job_id)

    if job: # remove job if already exists
        scheduler.remove_job(job_id=job_id)
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

# send message
def check_training_is_done_today(user: User) -> bool:
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    today = datetime.datetime.now(tz)
    today_date = today.date()

    finished_trainings = user.finished_trainings

    for f_t in finished_trainings:
        f_t_date = set_timezone(f_t.time_start).date()
        # check if dates are the same
        if f_t_date == today_date:
            return True
    return False
    
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

    # check if user trained today
    done = check_training_is_done_today(user)
    if done:
        text = texts.already_trained_title[lang]

    kb = training_kbs.get_start_training(lang)

    await bot.send_message(user.id, text, reply_markup=kb)

# *skipped training
# scheduler
def create_skipped_training_remind(bot: Bot, dp: Dispatcher, user_id, days: list, hours, minutes):
    """use to start remind skipped trainings, also if you want to RESTART remind you can use this too"""
    now = datetime.datetime.now()

    # get job
    job_id = f'send_skip_training_remind_{user_id}'
    job = scheduler.get_job(job_id)

    if job: # remove job if already exists
        scheduler.remove_job(job_id=job_id)
    scheduler.add_job(
        send_skipped_training_remind, 'cron', 
        day_of_week=", ".join(days), 
        hour=hours,
        minute=minutes,
        second=SCHD_SKIPPEND_TRAINING_START_SECONDS,
        # second=now.time().second + 1,
        args=(bot, dp, user_id), 
        id=job_id
    )

# send message
def check_training_is_done_at_day(user: User, day: datetime.datetime) -> bool:
    day_date = day.date()

    finished_trainings = user.finished_trainings

    for f_t in finished_trainings:
        f_t_date = set_timezone(f_t.time_start).date()
        # check if dates are the same
        if f_t_date == day_date:
            return True
    return False

def check_aura_redused_today(user: User, today: datetime.datetime):
    today_date = today.date()

    stats = user.stats

    for st in stats:
        st_date = set_timezone(st.created).date()
        # check if dates are the same
        if st_date == today_date:
            return True
    return False

async def send_skipped_training_remind(bot: Bot, dp: Dispatcher, user_id: int):
    user = await db.get_user(user_id)
    lang = user.lang

    trainings = user.trainings
    days_data = trainings.days_data

    # check if training done yesturday
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    today = datetime.datetime.now(tz)

    # get yesturday
    yesturday = today - datetime.timedelta(days=1)  
    
    # get day name, ex: fri, mon  
    day_name = yesturday.strftime("%a").lower()
    
    if day_name not in days_data: # check if user has training in that day
        return
    
    # check if user registered earlier
    if set_timezone(user.created).date() >= yesturday.date():
        return 
    
    # checks
    trained = check_training_is_done_at_day(user, yesturday)
    aura_redused = check_aura_redused_today(user, today)
    if not trained and not aura_redused:
        
        # send skip message
        text = texts.missed_training[lang]
        await bot.send_message(
            chat_id=user_id, 
            text=text
        )
        # get aura and send user aura data
        user_aura = user.aura

        reduce_aura: float = aura_manager.reduce_aura()

        # reduce
        new_aura = user_aura - reduce_aura
        text = texts.aura_reduce_result[lang].format(
            aura_before=user_aura,
            aura_reduce=reduce_aura,
            current_aura=new_aura
        )

        # send message
        await bot.send_message(
            chat_id=user_id, 
            text=text
        )

        # update user 
        await db.update_user(
            user.id, {"aura": new_aura}
        )
        # create user stats in db
        await db.create_user_stats(user.id, {
            "aura_reduced_on_training_skip": reduce_aura
        })