from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from texts import admin as texts
from .. import callback_filters

import database as db
from database.models import User, UserTrainings, FinishedUserTraining


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
        messages.append((title, None))

        # get and send all users as messages list
        all_users = await db.get_all_users()
        for user in all_users:
            user_text, user_kb = get_user_control(user, lang)
            messages.append((user_text, user_kb))

        # back button
        calldata = callback_filters.AdminMenu(to="main").pack()
        
        back_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texts.back_btn[lang], callback_data=calldata)]
        ])
        messages.append((texts.navigation_title[lang], back_kb))
        
    return text, kb.as_markup(), messages

# todo user control kb
control_buttons = [

]
def get_user_control(user: User, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    """returns text and kb, to contrlol user data, delete update"""

    kb = InlineKeyboardBuilder()
    text = str(user)

    for btn in control_buttons:
        calldata = callback_filters.ComtrolUser(user_id=user.id, action=btn["action"]).pack()
        kb.row(InlineKeyboardButton(text=btn["text"][lang], callback_data=calldata))

    return text, kb.as_markup()