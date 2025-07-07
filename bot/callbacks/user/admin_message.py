from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from config import *
from aiogram.exceptions import TelegramBadRequest

# states
from aiogram.fsm.context import FSMContext
from states import user as states

from keyboards import callback_filters
from keyboards.user import admin_message as kbs
from texts import user as texts
import database as db

from middlewares.user import admin_message_middleware

router = Router()
router.callback_query.middleware.register(admin_message_middleware)

@router.callback_query(callback_filters.UserAdminMessage.filter(F.data == "cancel"))
async def get_cancel_admin_message(call: CallbackQuery, state: FSMContext):
    message = call.message
    user_data = call.from_user

    # delete message and clear state
    await message.delete()
    await state.clear()

# answer to admin
@router.callback_query(callback_filters.UserControllAdminMessage.filter(F.action == "answer"))
async def get_answer_to_admin(call: CallbackQuery, state: FSMContext):
    message = call.message
    user_data = call.from_user

    user = await db.get_user(user_data.id)
    lang = user.lang
    # send message and kb
    kb = kbs.get_cancel_admin_message(lang)
    await message.answer(texts.enter_admin_message_title[lang], reply_markup=kb)

    # set and update state
    await state.set_state(states.UserAdminMessage.text)
    await state.update_data(on_admin_message=True)

    await call.answer()