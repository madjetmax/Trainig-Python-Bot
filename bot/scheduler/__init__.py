from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import *

scheduler = AsyncIOScheduler({'apscheduler.timezone': SCHD_TIME_ZONE})