import asyncio
import time

from config import *

timer_tasks = {}
timers = {} # user_id: Timer() object

class Timer():
    """takes user_id and max_time (in seconds)"""
    def __init__(self, user_id, max_time=0):
        self.max_time = max_time # seconds
        self.time = max_time # seconds
        self.start_time = 0

        self.user_id = user_id

        self.on_run = False

        # update coroutine
        self.on_update_funk = None
        self.on_update_funk_args = ()
        
        # end coroutine
        self.on_end_funk = None
        self.on_end_funk_args = ()

    # tasks
    async def update_task(self):
        try:
            while True:
                await asyncio.sleep(TIMER_UPDATE_DALAY)
                await self.update_message()
        except Exception as ex:
            print(ex)

    async def on_end_task(self):
        await asyncio.sleep(self.time) 
        await self.update_on_end()
    
    # start
    async def start_update_task(self):
        # creating task
        task = asyncio.create_task(
            self.update_task()   
        )
        task_id = f"timer_update_{self.user_id}"
        timer_tasks[task_id] = task

    async def start_end_task(self):
        # creating task
        task = asyncio.create_task(
            self.on_end_task()   
        )
        task_id = f"timer_end_{self.user_id}"
        timer_tasks[task_id] = task

    # remove 
    async def remove_update_task(self):
        # cancel and remove task
        task_id = f"timer_update_{self.user_id}"
        try:
            timer_tasks[task_id].cancel()
            timer_tasks.pop(task_id)
        except KeyError:
            pass
    async def remove_end_task(self):
        # cancel and remove task
        task_id = f"timer_end_{self.user_id}"
        try:
            timer_tasks[task_id].cancel()
            timer_tasks.pop(task_id)
        except KeyError:
            pass

    # start and end
    async def start(self):
        if not self.on_run:
            self.on_run = True
            self.start_time = int(time.time())

            await self.start_update_task()
            await self.start_end_task()

    async def stop(self):
        if self.on_run:
            self.on_run = False

            await self.remove_update_task()
            await self.remove_end_task()

    def restart(self):
        self.time = self.max_time
        
    async def update_end_time(self):
        # start scheduler again
        
        # restart end
        await self.remove_end_task()
        await self.start_end_task()

        # restart update
        await self.remove_update_task()
        await self.start_update_task()

    # schedule funks
    async def update_message(self):
        if self.on_run:
            current_time = int(time.time())
            self.time = self.max_time - int(current_time - self.start_time)

            if self.time >= 0:
                await self.on_update_funk(*self.on_update_funk_args)

    async def update_on_end(self):
        if self.on_run:
            current_time = int(time.time())
            self.time = self.max_time - int(current_time - self.start_time)

            await self.on_end_funk(*self.on_end_funk_args)

            await self.stop()

    def get_clear_time(self) -> tuple[int, int]:
        """returns minutes ans seconds"""

        minutes = str(self.time // 60)
        seconds = str(self.time % 60)

        if len(minutes) == 1:
            minutes = "0" + minutes

        if len(seconds) == 1:
            seconds = "0" + seconds

        return minutes, seconds
