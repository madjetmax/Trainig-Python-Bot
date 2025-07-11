import html

all_lengs_codes = [
    "en", "uk"
]

days_of_week = [
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
]

# messages and texts
# *admin menu
main_menu = {
    "en": "Admin menu🫅🏿",
    "uk": "Меню Адміна🫅🏿"
}

all_users_menu = {
    "en": "All Users",
    "uk": "Усі Користувачі"
}

inbox_menu = {
    "en": "Inbox and Feedbacks",
    "uk": "Вхідні повідомлення та Фідбеки"
}

# help
navigation_title = {
    "en": "Navigation",
    "uk": "Навігація",
}


# chatting with user
to_admin_message_text = {
    "en": """
ID: {message_id},
USER ID: {from_user_id},
USER NAME: {from_user_name},
DATE: {date_sent},
TEXT: {text}
    """,
    "uk": """
ID: {message_id},
ID КОРИСТУВАЧА: {from_user_id},
ІМ'Я КОРИСТУВАЧА: {from_user_name},
ДАТА ВІДПРАВКИ: {date_sent},
ТЕКСТ ПОВІДОМЛЕННЯ: {text}
    """,
}

confirm_block_user_messages_sending_title = {
    "en": "Do you realy want to block message for {user_name}?",
    "uk": "Ви дійсно хочете заблокувати повідомлення для {user_name}?",
}

confirm_unblock_user_messages_sending_title = {
    "en": "Do you realy want to unblock message for {user_name}?",
    "uk": "Ви дійсно хочете розблокувати повідомлення для {user_name}?",
}


empty_admin_messages = {
    "en": "No admin messages yet",
    "uk": "Немає повідомлень користувачів",
}

cant_user_messages_while_training = {
    "en": "Cant chat with user while training",
    "uk": 'Не можна відправити повідомлення користувачу під час тренування',
}

# buttons
trans_days_of_week = {
    "en": {
        "mon": "Monday",
        "tue": "Tuesday",
        "wed": "Wednesday",
        "thu": "thursday",
        "fri": "Friday",
        "sat": "saturday",
        "sun": "Sunday",
    }, 
    "uk": {
        "mon": "Понеділок",
        "tue": "Вівторок",
        "wed": "Середа",
        "thu": "Четверг",
        "fri": "П'ятниця",
        "sat": "Субота",
        "sun": "Неділя",
    }, 
}

answer_btn = {
    "en": "Answer",
    "uk": "Відповісти",
}

block_user_messages_send_btn = {
    "en": "Block sending messages",
    "uk": "Заблокувати можливість відправки повідомлень",
}

unblock_user_messages_send_btn = {
    "en": "Unblock sending messages",
    "uk": "Розблокувати можливість відправки повідомлень",
}

block_btn = {
    "en": 'Block',
    "uk": "Заблокувати"
}
unblock_btn = {
    "en": 'Unblock',
    "uk": "Розблокувати"
}

back_btn = {
    "en": "Back <<",
    "uk": "Назад <<",
}

next_btn = {
    "en": "Next >>",
    "uk": "Далі >>",
}

yes_btn = {
    "en": "Yes",
    "uk": "Так",
}

no_btn = {
    "en": "No",
    "uk": "Ні",
}

cancel_btn = {
    "en": "Cansel",
    "uk": "Відміна",
}