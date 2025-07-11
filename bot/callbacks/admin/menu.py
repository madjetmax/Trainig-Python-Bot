from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from config import *
from aiogram.exceptions import TelegramBadRequest

import datetime
from zoneinfo import ZoneInfo
# states
from aiogram.fsm.context import FSMContext
from states import admin as states

from keyboards import callback_filters
from keyboards.admin import menu as kbs
from keyboards.admin import user_message as user_message_kbs

from texts import admin as texts
import database as db
from database.models import User, FinishedUserTraining, UserTrainings, AdminChatting

from middlewares.admin import CallbacksMiddleware

router = Router()
router.callback_query.middleware.register(CallbacksMiddleware())

async def delete_messages(bot: Bot, chat_id, messages):
    if messages:
        await bot.delete_messages(chat_id, messages)


def set_timezone(date: datetime.datetime) -> datetime.datetime:
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    return date.astimezone(tz)


# *menu navigation
@router.callback_query(callback_filters.AdminMenu.filter())
async def admin_menu(call: CallbackQuery, callback_data: callback_filters.AdminMenu, state: FSMContext):
    # message data
    message = call.message
    bot: Bot = message.bot
    chat_id = message.chat.id
    user_data = call.from_user
    
    state_data = await state.get_data()

    # user 
    user = await db.get_user(user_data.id)
    if user is None:
        await call.answer()

    lang = user.lang

    # calldata
    to = callback_data.to

    text, kb, messages = await kbs.get_admin_menu(to, user_data, lang, user=user)

    await state.set_state(states.AdminMenu)

    if messages: # send messages if != []
        messages_to_delete = []
        await message.delete()
        for text, kb, photo_path in messages:
            if photo_path:
                try:
                    msg = await message.answer_photo(photo=photo_path, caption=text, reply_markup=kb)
                except:
                    # send without photo
                    msg = await message.answer(text=text, reply_markup=kb)
            else: 
                msg = await message.answer(text=text, reply_markup=kb)
            messages_to_delete.append(msg.message_id)

        await state.update_data(messages_to_delete=messages_to_delete)
    else: 
        messages_to_delete = state_data.get("messages_to_delete")
        if messages_to_delete: # send new message and delete messages_to_delete from state
            await message.answer(text=text, reply_markup=kb)
            await delete_messages(message.bot, user_data.id, messages_to_delete)
            await state.update_data(
                messages_to_delete=[]
            )
        else: # just answer
            await message.edit_text(text=text, reply_markup=kb)

# user controll
@router.callback_query(callback_filters.ControlUser.filter())
async def control_user(call: CallbackQuery, callback_data: callback_filters.ControlUser):
    message = call.message
    admin_data = call.from_user

    user_id = callback_data.user_id
    action = callback_data.action

    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    if action == "block_admin_msgs":
        user = await db.update_user(user_id, {"can_send_messages_to_admins": False})

    if action == "unblock_admin_msgs":
        user = await db.update_user(user_id, {"can_send_messages_to_admins": True})

    # edit message
    text, kb = kbs.get_user_control(user, admin_lang)
    await message.edit_text(text, reply_markup=kb)
    

# *add more admin messages 
def sort_admin_messages(x: AdminChatting) -> int:
    # getting seconds from datetime to sort
    seconds = x.created.timestamp()
    return -seconds

@router.callback_query(callback_filters.AdminAddMoreAM.filter())
async def add_more_admin_messages(call: CallbackQuery, callback_data: callback_filters.AdminAddMoreAM, state: FSMContext):
    message = call.message
    admin_data = call.from_user

    start = callback_data.start
    offset = callback_data.offset

    admin = await db.get_user(admin_data.id)
    lang = admin.lang

    # get message to delete
    state_data = await state.get_data()
    messages_to_delete = state_data.get("messages_to_delete")

    # get and send all admin messages as messages list
    all_admin_messages = await db.get_admin_messages_from_users()

    sorted_admin_messages = sorted(all_admin_messages, key=sort_admin_messages)[start:start + offset]

    timezone = ZoneInfo(DATETIME_TIME_ZONE)

    global_i = start

    for admin_message in sorted_admin_messages:
        # get from_user user
        message_user = await db.get_user(admin_message.from_user_id)
        date_sent = admin_message.created.astimezone(timezone)
        # get text and kb 
        message_text = texts.to_admin_message_text[lang].format(
            message_id=admin_message.id,
            from_user_id=message_user.id,
            from_user_name=message_user.name,
            date_sent=set_timezone(date_sent),
            text=admin_message.message
        )
        block_msgs: bool = message_user.can_send_messages_to_admins
        message_kb = user_message_kbs.get_user_message_controll(block_msgs, admin_message.id, admin_message.from_user_id, lang)
        # send and add message to messages list
        if admin_message.photo_path:
            msg = await message.answer_photo(photo=admin_message.photo_path, caption=message_text, reply_markup=message_kb)
        else:
            msg = await message.answer(message_text, reply_markup=message_kb)

        global_i += 1

        # add message to delete
        if messages_to_delete is not None:
            messages_to_delete.append(msg.message_id)

    # send navigation kb and message
    kb = kbs.get_admin_messages_controll(global_i + 1 < len(all_admin_messages), start+offset, offset, lang)
    msg = await message.answer(texts.navigation_title[lang], reply_markup=kb)
    
    # delete message
    await message.delete()

    # add to messages_to_delete
    if messages_to_delete is not None:
        messages_to_delete.append(msg.message_id)
        # update state
        await state.update_data(messages_to_delete=messages_to_delete)