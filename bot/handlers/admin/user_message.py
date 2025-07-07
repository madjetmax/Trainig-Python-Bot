from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import *
import asyncio
import random

import database as db
from database.models import User, AdminChatting

from keyboards.admin import user_message as kbs
from keyboards.user import admin_message as user_kbs

from texts import admin as texts
from texts import user as user_texts

from states import admin as states

router = Router()


@router.message(states.AdminUserMessage.text, F.text)
async def send_messge_to_user(message: Message, state: FSMContext):
    message_text = message.text
    admin_data = message.from_user
    bot: Bot = message.bot

    state_data = await state.get_data()

    # get user data from state
    user_id = state_data["user_id"]
    user = await db.get_user(user_id)
    user_lang = user.lang

    # create admin chatting in database
    admin_message = await db.create_admin_message(-1, user_id, message_text, None)

    # get text 
    text = user_texts.from_admin_text[user_lang].format(
        date_sent=admin_message.created,
        text=admin_message.message
    )

    # get kb and send message to user
    kb = user_kbs.get_admin_message_control(user_lang)
    try:
        await bot.send_message(user_id, text, reply_markup=kb)

        admin = await db.get_user(admin_data.id)
        admin_lang = admin.lang
        # answer to admin on success
        await message.answer(user_texts.sent_to_admin[admin_lang])
    except:
        pass

    # clear state
    await state.clear()

@router.message(states.AdminUserMessage.text, F.photo)
async def send_messge_to_user_and_photo(message: Message, state: FSMContext):
    title = message.caption
    photo = message.photo
    admin_data = message.from_user
    bot: Bot = message.bot

    state_data = await state.get_data()


    # get admin
    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    if title is None:
        await user_texts.title_empty[admin_lang]
        return

    # get user data from state
    user_id = state_data["user_id"]
    user = await db.get_user(user_id)
    user_lang = user.lang

    # creating photot_path 
    photo_id = photo[-1].file_id

    # create admin chatting in database
    admin_message = await db.create_admin_message(-1, user_id, title, photo_id)

    # get text 
    text = user_texts.from_admin_text[user_lang].format(
        date_sent=admin_message.created,
        text=admin_message.message
    )

    # get kb and send message to user
    kb = user_kbs.get_admin_message_control(user_lang)
    try:
        await bot.send_photo(user_id, photo=photo_id, caption=text, reply_markup=kb)        
        # answer to admin on success
        await message.answer(user_texts.sent_to_admin[admin_lang])
    except:
        pass

    # clear state
    await state.clear()