from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from config import *
from aiogram.exceptions import TelegramBadRequest

# states
from aiogram.fsm.context import FSMContext
from states import admin as states

from keyboards import callback_filters
from keyboards.admin import menu as kbs
from texts import admin as texts
import database as db
from database.models import User, FinishedUserTraining, UserTrainings

from middlewares.admin import CallbacksMiddleware

router = Router()
router.callback_query.middleware.register(CallbacksMiddleware())

async def delete_messages(bot: Bot, chat_id, messages):
    if messages:
        await bot.delete_messages(chat_id, messages)

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
        for text, kb in messages:
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
