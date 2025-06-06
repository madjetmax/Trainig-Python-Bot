from aiogram import Bot
from aiogram.types import Message
import datetime

from config import *

from . import scheduler

import database as db


# start
def start_training_update(timer):
    """takes timer as a class of training_timers.Timer()"""

    job_id=f"trainin_timer_{timer.user_id}"

    scheduler.add_job(
        timer.update_message, 'interval', 
        seconds=TIMER_UPDATE_DALAY,
        id=job_id
    )



def start_timer_end_check(timer):
    """takes timer as a class of training_timers.Timer()"""

    job_id=f"trainin_timer_end_{timer.user_id}"

    minutes = timer.time // 60
    seconds = timer.time % 60

    scheduler.add_job(
        timer.update_on_end, 'interval', 
        minutes=minutes,
        seconds=seconds,
        id=job_id
    )

# stop
def stop_training_update(timer):
    """takes timer as a class of training_timers.Timer()"""

    job_id=f"trainin_timer_{timer.user_id}"
    scheduler.remove_job(job_id)

def stop_timer_end_check(timer):
    """takes timer as a class of training_timers.Timer()"""

    job_id=f"trainin_timer_end_{timer.user_id}"
    scheduler.remove_job(job_id)
