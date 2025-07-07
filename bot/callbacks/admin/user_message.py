from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from config import *
from aiogram.exceptions import TelegramBadRequest

# states
from aiogram.fsm.context import FSMContext
from states import admin as states

from database.models import User, AdminChatting
import database as db

from keyboards import callback_filters
from keyboards.admin import user_message as kbs
from texts import admin as texts
from texts import user as user_texts

import database as db

router = Router()

@router.callback_query(callback_filters.AdminUserMessage.filter(F.action == "answer"))
async def get_cancel_admin_message(call: CallbackQuery, callback_data: callback_filters.AdminUserMessage, state: FSMContext):
    message = call.message
    admin_data = call.from_user

    from_user_id = callback_data.user_id

    admin = await db.get_user(admin_data.id)
    lang = admin.lang
    # get kb and send message
    kb = kbs.get_cancel_message_to_user(lang)
    await message.answer(user_texts.enter_admin_message_title[lang], reply_markup=kb)

    # set and update state
    await state.set_state(states.AdminUserMessage.text)
    await state.update_data(user_id=from_user_id)
    # answer empty callback
    await call.answer()

# *block messages sending
@router.callback_query(callback_filters.AdminUserMessage.filter(F.action == "block_msgs")) 
async def block_messages_send(call: CallbackQuery, callback_data: callback_filters.AdminUserMessage, state: FSMContext):
    admin_data = call.from_user
    message = call.message
    bot = message.bot

    user_id = callback_data.user_id
    admin_message_id = callback_data.admin_message_id

    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    user = await db.get_user(user_id)
    
    # edit message
    # text and kb to block
    text = texts.confirm_block_user_messages_sending_title[admin_lang].format(
        user_name=user.name
    )
    kb = kbs.get_confirm_user_messages_block(admin_message_id, user_id, admin_lang)
    
    # check type of message
    if message.text is None:
        await message.edit_caption(caption=text, reply_markup=kb)
    else:
        await message.edit_text(text, reply_markup=kb)

# *block 
@router.callback_query(callback_filters.AdminConfrimUserMessagesBlock.filter(F.confirm_block_messages)) # check if True
async def confirm_block_messages_send(call: CallbackQuery, callback_data: callback_filters.AdminConfrimUserMessagesBlock, state: FSMContext):
    admin_data = call.from_user
    message = call.message

    user_id = callback_data.user_id
    admin_message_id = callback_data.admin_message_id

    # get admin message from database
    admin_message: AdminChatting = await db.get_admin_message(admin_message_id)

    if admin_message is None:
        await call.answer()
        return 

    # get admin and user
    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    user = await db.get_user(user_id)

    photo_path = admin_message.photo_path
    if photo_path:...
        # todo make photo
    
    text = texts.to_admin_message_text[admin_lang].format(
        message_id=admin_message.id,
        from_user_id=admin_message.from_user_id,
        from_user_name=user.name,
        date_sent=admin_message.created,
        text=admin_message.message
    )

    # get kb and edit message
    kb = kbs.get_user_message_controll(False, admin_message_id, user_id, admin_lang)

    # check message type
    if message.text is None:
        await message.edit_caption(caption=text, reply_markup=kb)
    else:
        await message.edit_text(text, reply_markup=kb)

    # update user
    await db.update_user(user_id, {"can_send_messages_to_admins": False})

# *unblock messages sending
@router.callback_query(callback_filters.AdminUserMessage.filter(F.action == "unblock_msgs")) 
async def unblock_messages_send(call: CallbackQuery, callback_data: callback_filters.AdminUserMessage, state: FSMContext):
    admin_data = call.from_user
    message = call.message
    bot = message.bot

    user_id = callback_data.user_id
    admin_message_id = callback_data.admin_message_id

    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    user = await db.get_user(user_id)
    
    # edit message
    # text and kb to unblock
    text = texts.confirm_unblock_user_messages_sending_title[admin_lang].format(
        user_name=user.name
    )
    kb = kbs.get_confirm_user_messages_unblock(admin_message_id, user_id, admin_lang)

    # check type of message
    if message.text is None:
        await message.edit_caption(caption=text, reply_markup=kb)
    else:
        await message.edit_text(text, reply_markup=kb)

# *unblock 
@router.callback_query(callback_filters.AdminConfrimUserMessagesBlock.filter(F.confirm_unblock_messages)) # check if True
async def confirm_unblock_messages_send(call: CallbackQuery, callback_data: callback_filters.AdminConfrimUserMessagesBlock, state: FSMContext):
    admin_data = call.from_user
    message = call.message

    user_id = callback_data.user_id
    admin_message_id = callback_data.admin_message_id

    # get admin message from database
    admin_message: AdminChatting = await db.get_admin_message(admin_message_id)

    if admin_message is None:
        await call.answer()
        return 

    # get admin and user
    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    user = await db.get_user(user_id)

    photo_path = admin_message.photo_path
    if photo_path:...
        # todo make photo
    
    text = texts.to_admin_message_text[admin_lang].format(
        message_id=admin_message.id,
        from_user_id=admin_message.from_user_id,
        from_user_name=user.name,
        date_sent=admin_message.created,
        text=admin_message.message
    )

    # get kb and edit message
    kb = kbs.get_user_message_controll(True, admin_message_id, user_id, admin_lang)

    # check message type
    if message.text is None:
        await message.edit_caption(caption=text, reply_markup=kb)
    else:
        await message.edit_text(text, reply_markup=kb)

    # update user
    await db.update_user(user_id, {"can_send_messages_to_admins": True})

# *cancel
@router.callback_query(callback_filters.AdminConfrimUserMessagesBlock.filter(F.cancel)) # check if False
async def confirm_block_messages_send(call: CallbackQuery, callback_data: callback_filters.AdminConfrimUserMessagesBlock, state: FSMContext):
    admin_data = call.from_user
    message = call.message

    user_id = callback_data.user_id
    admin_message_id = callback_data.admin_message_id

    # get admin message from database
    admin_message: AdminChatting = await db.get_admin_message(admin_message_id)

    if admin_message is None:
        await call.answer()
        return 

    # get admin and user
    admin = await db.get_user(admin_data.id)
    admin_lang = admin.lang

    user = await db.get_user(user_id)

    photo_path = admin_message.photo_path
    if photo_path:...
        # todo make photo
    
    text = texts.to_admin_message_text[admin_lang].format(
        message_id=admin_message.id,
        from_user_id=admin_message.from_user_id,
        from_user_name=user.name,
        date_sent=admin_message.created,
        text=admin_message.message
    )
    # get it from user.can_send_messages_to_admins to pass in to kb get funk as blokc_msgs
    block_msgs: bool = user.can_send_messages_to_admins

    # get kb and edit message
    kb = kbs.get_user_message_controll(block_msgs, admin_message_id, user_id, admin_lang)

    # check message type
    if message.text is None:
        await message.edit_caption(caption=text, reply_markup=kb)
    else:
        await message.edit_text(text, reply_markup=kb)

# cancel send messge to user
@router.callback_query(callback_filters.AdminCancelSendMessage.filter(F.cancel)) # check if True
async def get_cancel_admin_message(call: CallbackQuery, state: FSMContext):
    message = call.message

    # delete and clear state
    await message.delete()
    await state.clear()    

