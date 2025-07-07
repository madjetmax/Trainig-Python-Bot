from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import *
import database as db
from .. import callback_filters
from texts import user as user_texts


# *admin message
def get_cancel_admin_message(lang) -> InlineKeyboardMarkup:
    calldata = callback_filters.UserAdminMessage(data="cancel").pack()
    kb =  InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=user_texts.cancel_btn[lang], callback_data=calldata)]
    ])

    return kb

def get_admin_message_control(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=user_texts.answer_btn[lang], 
            callback_data=callback_filters.UserControllAdminMessage(action="answer").pack()
        )]
    ])

    return kb