from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import *
import database as db
from database.models import User, AdminChatting

from .. import callback_filters
from texts import admin as texts


# *user message
def get_user_message_controll(block_msgs: bool, message_id, user_id, lang) -> InlineKeyboardMarkup:
    if block_msgs:
        block_btn = [InlineKeyboardButton(
            text=texts.block_user_messages_send_btn[lang], callback_data=callback_filters.AdminUserMessage(user_id=user_id, action="block_msgs", admin_message_id=message_id).pack()
        )]
    else:
        block_btn = [InlineKeyboardButton(
            text=texts.unblock_user_messages_send_btn[lang], callback_data=callback_filters.AdminUserMessage(user_id=user_id, action="unblock_msgs", admin_message_id=message_id).pack()
        )]
    
    kb =  InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.answer_btn[lang], callback_data=callback_filters.AdminUserMessage(user_id=user_id, action="answer").pack()
        )],
        block_btn
    ])

    return kb

def get_confirm_user_messages_block(message_id, user_id, lang) -> InlineKeyboardMarkup:
    block_calldata = callback_filters.AdminConfrimUserMessagesBlock(user_id=user_id, confirm_block_messages=True, admin_message_id=message_id).pack()

    cancel_calldata = callback_filters.AdminConfrimUserMessagesBlock(user_id=user_id, cancel=True, admin_message_id=message_id).pack()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.block_btn[lang], callback_data=block_calldata)],
        [InlineKeyboardButton(text=texts.cancel_btn[lang], callback_data=cancel_calldata)],
    ])

    return kb

def get_confirm_user_messages_unblock(message_id, user_id, lang) -> InlineKeyboardMarkup:
    unblock_calldata = callback_filters.AdminConfrimUserMessagesBlock(user_id=user_id, confirm_unblock_messages=True, admin_message_id=message_id).pack()

    cancel_calldata = callback_filters.AdminConfrimUserMessagesBlock(user_id=user_id, cancel=True, admin_message_id=message_id).pack()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.unblock_btn[lang], callback_data=unblock_calldata)],
        [InlineKeyboardButton(text=texts.cancel_btn[lang], callback_data=cancel_calldata)],
    ])

    return kb

# sending message
def get_cancel_message_to_user(lang):
    cancel_calldata = callback_filters.AdminCancelSendMessage(cancel=True).pack()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.cancel_btn[lang], callback_data=cancel_calldata)]
    ])

    return kb