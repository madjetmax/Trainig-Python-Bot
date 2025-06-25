from aiogram import Bot, Dispatcher
import asyncio, os
from config import *

import database.engine
import handlers
import callbacks
import database
import scheduler
from scheduler import user as user_scheduler

# *for deploy
# from aiogram.client.session.aiohttp import AiohttpSession

# session = AiohttpSession(proxy="http://proxy.server:3128")
# bot = Bot(token=BOT_TOKEN, session=session)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers( 
    handlers.router,
    callbacks.router,
)


# start funcs
async def start_scheduler():
    scheduler.scheduler.start()
    await user_scheduler.start_all_users_training_reminds(bot, dp)

async def start_db():
    await database.engine.create_db()

async def main():
    await start_db()
    await start_scheduler()    

    # start bot polling
    print('bot launched')
    await dp.start_polling(bot, skip_updates=True)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot stoped!")