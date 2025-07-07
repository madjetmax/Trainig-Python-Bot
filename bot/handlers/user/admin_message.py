from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from uuid import uuid4

from config import *
import asyncio
import random

import database as db
from database.models import User, AdminChatting

from keyboards.user import admin_message as kbs
from keyboards.admin import user_message as admin_kbs

from texts import user as texts
from texts import admin as admin_texts
from states import user as states

from middlewares.user import admin_message_middleware

router = Router()
router.message.middleware.register(admin_message_middleware)


@router.message(Command("admin_message"))
async def send_admin_message(message: Message, state: FSMContext):
    user_data = message.from_user

    user = await db.get_user(user_data.id)
    lang = user.lang
    # send message and kb
    kb = kbs.get_cancel_admin_message(lang)
    await message.answer(texts.enter_admin_message_title[lang], reply_markup=kb)

    # set and update state
    await state.set_state(states.UserAdminMessage.text)
    await state.update_data(on_admin_message=True)

async def send_to_admins(bot: Bot, from_user: User, admin_message: AdminChatting):
    photo_path = admin_message.photo_path

    from_user_id = admin_message.from_user_id
    from_user_name = from_user.name

    date_sent = admin_message.created
    message_text = admin_message.message
    message_id = admin_message.id

    # send message to admins
    for admin_id in ADMINS: # ids
        try: 
            admin = await db.get_user(admin_id)
            lang = admin.lang
            text = admin_texts.to_admin_message_text[lang].format(
                message_id=message_id,
                from_user_id=from_user_id,
                from_user_name=from_user_name,
                date_sent=date_sent,
                text=message_text
            )

            # get kb and send message
            # passing block_msgs to True because in this case user can send messages and admin only can block messages
            kb = admin_kbs.get_user_message_controll(True, message_id, from_user.id, lang) 
            if photo_path:
                await bot.send_photo(admin_id, photo_path, caption=text, reply_markup=kb)
            else:
                await bot.send_message(admin_id, text, reply_markup=kb)
        except:
            pass

# get admin message text
@router.message(states.UserAdminMessage.text, F.text)
async def get_admin_message_text(message: Message, state: FSMContext):
    message_text = message.text
    user_data = message.from_user

    user = await db.get_user(user_data.id)
    lang = user.lang

    # send sending message
    progress_msg = await message.answer(texts.sending_to_andmin[lang])

    # check if user can send messages to admin, admin can block user messages
    if user.can_send_messages_to_admins == False:
        # sleep random time
        sleep_time = random.randint(5, 20) / 10
        await asyncio.sleep(sleep_time)

        # send message and return to break func
        await progress_msg.edit_text(texts.failed_send_to_admin[lang])
        
        # clear state
        await state.clear()
        return

    # create admin message in database
    admin_message = await db.create_admin_message(
        user_data.id, -1,
        message_text, photo_path=None
    )
    
    # else send to admins
    await send_to_admins(message.bot,user, admin_message)

    # answer sent message 
    await progress_msg.edit_text(texts.sent_to_admin[lang])
    
    await state.clear()

# get admin message text
@router.message(states.UserAdminMessage.text, F.photo)
async def get_admin_message_text_and_photo(message: Message, state: FSMContext):
    user_data = message.from_user
    title = message.caption
    photo = message.photo

    user = await db.get_user(user_data.id)
    lang = user.lang

    if title is None:
        await message.answer(texts.title_empty[lang])
        return

    # send sending message
    await message.answer(texts.sending_to_andmin[lang])

    # check if user can send messages to admin, admin can block user messages
    if user.can_send_messages_to_admins == False:
        # sleep random time
        sleep_time = random.randint(5, 20) / 10
        await asyncio.sleep(sleep_time)

        # send message and return to break func
        await message.answer(texts.failed_send_to_admin[lang])
        
        # clear state
        await state.clear()
        return
    
    # creating photo_path
    photo_id = photo[-1].file_id

    # create admin message in database
    admin_message = await db.create_admin_message(
        user_data.id, -1,
        title, photo_path=photo_id
    )
    
    # send to admins
    await send_to_admins(message.bot,user, admin_message)

    # answer sent message 
    await message.answer(texts.sent_to_admin[lang])

    # clear state
    await state.clear()