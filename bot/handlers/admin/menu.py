from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import asyncio

from config import *

from database.models import User, FinishedUserTraining
import database as db

from texts import user as texts
from states import user as states
from keyboards.admin import menu as kbs

from middlewares.admin import HandlersMiddleware

router = Router()

router.message.middleware.register(HandlersMiddleware())

# get menu 
@router.message(Command("admin"))
async def get_main_menu(message: Message, state: FSMContext):
    # message data
    user_data = message.from_user
    bot: Bot = message.bot
    chat_id = message.chat.id

    # get user and lang
    user = await db.get_user(user_data.id)
    lang = user.lang

    # send message and kb
    text, kb, _ = await kbs.get_admin_menu("main", user_data, lang)
    await message.answer(text, reply_markup=kb)