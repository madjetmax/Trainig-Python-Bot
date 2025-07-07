from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from texts import admin as texts
from zoneinfo import ZoneInfo

from config import *

from . import user_message as user_message_kbs
from .. import callback_filters

import database as db
from database.models import User, UserTrainings, FinishedUserTraining, AdminChatting

from texts import user as user_texts

admin_menu = {
    "main": [ # page name  
        { 
            "text": {
                "en": "All Users",
                "uk": "Усі Користувачі",
            },
            "to": "get_users",
        }, # button
        { 
            "text": {
                "en": "Inbox and Feedbacks",
                "uk": "Вхідні повідомлення та Фідбеки"
            },
            "to": "get_inbox",
        },
    ],
}


async def get_admin_menu(to=None, user_data=None, lang="", **kwargs) -> tuple[str, InlineKeyboardMarkup, list]:
    """returns text, kb, messages (list[tuple[str, InlineKeyboardMarkup]]) from to (page name)  takes additional args to get specific data, user from database"""
    
    kb = InlineKeyboardBuilder()
    text = ""
    messages = []

    if to == "main":
        buttons = admin_menu["main"]
        text = texts.main_menu[lang]

        # add buttons to kb
        for button in buttons:
            calldata = callback_filters.AdminMenu(to=button["to"]).pack()
            kb.row(
                InlineKeyboardButton(text=button["text"][lang], callback_data=calldata)
            )
    if to == "get_users":
        # add title message
        title = texts.all_users_menu[lang]
        messages.append((title, None, None))

        # get and send all users as messages list
        all_users = await db.get_all_users()
        for user in all_users:
            user_text, user_kb = get_user_control(user, lang)
            messages.append((user_text, user_kb, None))

        # back button
        calldata = callback_filters.AdminMenu(to="main").pack()
        
        back_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texts.back_btn[lang], callback_data=calldata)]
        ])
        messages.append((texts.navigation_title[lang], back_kb, None))
    
    if to == "get_inbox":
        all_admin_messages = await db.get_admin_messages_from_users()
        if all_admin_messages == []:
            # add empy title 
            title = texts.empty_admin_messages[lang]

            # back kb
            back_calldata = callback_filters.AdminMenu(to="main").pack()
            back_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=texts.back_btn[lang], callback_data=back_calldata)]
            ]) 
            messages.append((title, back_kb, None))
        else:
            # add title message
            title = texts.inbox_menu[lang]
            messages.append((title, None, None))

            offset = 10

            # get and send all admin messages as messages list
            sorted_admin_messages = sorted(all_admin_messages, key=sort_admin_messages)[:offset]

            timezone = ZoneInfo(DATETIME_TIME_ZONE)

            global_i = 0

            for admin_message in sorted_admin_messages:
                # get from_user user
                message_user = await db.get_user(admin_message.from_user_id)
                date_sent = admin_message.created.astimezone(timezone)
                # get text and kb 
                message_text = texts.to_admin_message_text[lang].format(
                    message_id=admin_message.id,
                    from_user_id=message_user.id,
                    from_user_name=message_user.name,
                    date_sent=date_sent,
                    text=admin_message.message
                )
                block_msgs: bool = message_user.can_send_messages_to_admins

                # add message to messages list
                message_kb = user_message_kbs.get_user_message_controll(block_msgs, admin_message.id, admin_message.from_user_id, lang)
                messages.append((message_text, message_kb, admin_message.photo_path))
                global_i += 1

            # nevigation kb
            navigation_kb = get_admin_messages_controll(global_i + 1 < len(all_admin_messages), start=offset, offset=offset, lang=lang)

            messages.append((texts.navigation_title[lang], navigation_kb, None))

    return text, kb.as_markup(), messages

def sort_admin_messages(x: AdminChatting) -> int:
    # getting seconds from datetime to sort
    seconds = x.created.timestamp()
    return -seconds


# todo user control kb
def get_user_control(user: User, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    """returns text and kb, to contrlol user data, delete update"""

    kb = InlineKeyboardBuilder()
    text = str(user)

    # block / unblock admin messages
    if user.can_send_messages_to_admins:
        calldata = callback_filters.ControlUser(user_id=user.id, action="block_admin_msgs").pack()
        kb.row(InlineKeyboardButton(text=texts.block_user_messages_send_btn[lang], callback_data=calldata))
    else:
        calldata = callback_filters.ControlUser(user_id=user.id, action="unblock_admin_msgs").pack()
        kb.row(InlineKeyboardButton(text=texts.unblock_user_messages_send_btn[lang], callback_data=calldata))

    return text, kb.as_markup()

def get_admin_messages_controll(add_add_more_btn: bool, start: int, offset: int, lang):
    kb = InlineKeyboardBuilder()
    
    # add more
    if add_add_more_btn:
        add_more_calldata = callback_filters.AdminAddMoreAM(start=start, offset=offset).pack()
        kb.row(InlineKeyboardButton(text=user_texts.add_more_btn[lang], callback_data=add_more_calldata))
    
    # back  
    back_calldata = callback_filters.AdminMenu(to="main").pack()
    kb.row(InlineKeyboardButton(text=texts.back_btn[lang], callback_data=back_calldata))
    
    return kb.as_markup()