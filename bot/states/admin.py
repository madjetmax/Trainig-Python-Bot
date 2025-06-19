from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class AdminMenu(StatesGroup):


    messages_to_delete = State() # ids