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

# all texts and translates

# message texts
greate = {
    "en": "Hello {name}, I'm trainnign bot\n\nChoose Language",
    "uk": "Привіт {name}, Я - бот для тренувань\n\nВиберіть Мову",
}

start_training_set_up = {
    "en": "Do you want set up you trainnings?",
    "uk": "Хочете пройти швидке налаштування тренувань?",
}

choose_days_title = {
    "en": "Choose Days",
    "uk": "Виберіть Дні",
}

can_setup_trainigns = {
    "en": "You can always setup your trainings by command /trainings",
    "uk": "Ви завжди можете налаштувати тренування за командою /trainings",
}

edit_trainings = {
    "en": "you have already created trainings, do you want to edit?",
    "uk": "Ви вже створийли тренування, хочете відредагувати?",
}

register = {
    "en": "You are not registered /start to continue",
    "uk": "Ви не зареєстовані, /start щоб продовжити",
}

workout_start_time = {
    "en": f"sent workout start time in format <em>{html.escape('<hours>')}.{html.escape('<minutes>')}</em> example: <em>12:40 or 20:00</em>",
    "uk": f"Напишіть час початку тренувань, в форматі <em>{html.escape('<години>')}.{html.escape('<хвилини>')}</em> наприклад: <em>12:40 або 20:00</em>",
}
new_time_was_set = {
    "en": "New time was set!",
    "uk": "Встановлено новий час!",
}

trainings_set_up = {
    "en": "Trainigs set up!",
    "uk": "Тренування успішно додані!",
}

invalid_time = {
    "en": "Invalid time!",
    "uk": "Некоректний час!",
}

start_training = {
    "en": "You are not on training, /start_training to start",
    "uk": "Ви не на тренуванні, /start_training щоб почати",
}



navigation_title = {
    "en": "Navigation",
    "uk": "Навігація",
}

new_body_part_name = {
    "en": "Enter new body part name",
    "uk": "Введіть назву для новох частни тіла",
}

new_rep_name = {
    "en": "Enter new rep name",
    "uk": "Введіть назву для нового підходу",
}

# menu 
main_menu = {
    "en" : 'Main menu',
    "uk" : 'Головна сторінка',
}

edit_trainings_menu = {
    "en" : "Choose what you want to edit",
    "uk" : "Виберіть що ви хочете змінити",
}

edit_selected_days_menu = {
    "en": "Select Days",
    "uk": "Виберіть Дні",
}

edit_reps_menu = {
    "en" : "Edit Reps and breaks",
    "uk" : "Налаштування Підходів та Перерв",
}

edit_lang_menu = {
    "en": 'Choose language',
    "uk": 'Вибуріть мову',
}

new_trainings_start_time = {
    "en": "Enter new time for trainings start, current: {hours}:{minutes}",
    "uk": "Введіть новий час для початку тренувань, поточний час: {hours}:{minutes}",
}

cant_edit_at_training = {
    "en": "Cant edit data while training",
    "uk": 'Під час тренування, данні змінити не можна',
}

# body parts
select_body_part_title = {
    "en": "Select body part for {day}",
    "uk": "Виберіть частину тіла для {day}",
}

# reps
select_rep_name_title = {
    "en": "Select rep name",
    "uk": "Виберіть назву підходу",
}

empty_reps_title = {
    "en": "No reps and breaks added, tap bellow to add",
    "uk": "Підходи та перерви не додані, натисніть нижче щоб додати",
}

reps_list_title = {
    "en": "Reps and Breaks for {day}\n",
    "uk": "Підходи та перерви для {day}\n",
}

break_in_list = {
    "en": "Break, time: {minutes}:{seconds}\n",
    "uk": "Перерва, час: {minutes}:{seconds}\n",
}

# trainigs 
its_training_time = {
    "en": "It's trainig time!",
    "uk": "Час тренування!",
}


break_timer_title = {
    "en": "Break, {minutes}:{seconds} left",
    "uk": "Перерва, {minutes}:{seconds} лишилося",
}

warmup_timer_title = {
    "en": "Warmup, {minutes}:{seconds} left",
    "uk": "Розігрів, {minutes}:{seconds} лишилося",
}

break_title = {
    "en": "Break, {minutes}:{seconds}",
    "uk": "Перерва, {minutes}:{seconds}",
}

warmup_title = {
    "en": "Warmup, {minutes}:{seconds}",
    "uk": "Розігрів, {minutes}:{seconds}",
}

rep_title = {
    "en": "Current rep: {name}",
    "uk": "Підхід: {name}",
}

curent_rep = {
    "en": "Current: {name}",
    "uk": "Поточний: {name}",
}

finished_training_text = {
    "en": """
ID: {id}
Date: {date}
Body part: {body_part}\n
Started at: {time_start}
End at: {time_end}
Training time: {training_time}\n
Finished reps: {reps_finished}
Reps all: {all_reps}\n
Aura got: {aura_got}
    """,
    "uk": """
ID: {id}
Дата: {date}
Частина тіла: {body_part}\n
Плчаток: {time_start}
Кінець: {time_end}
Повний час тренування: {training_time}\n
Закінчено підходів: {reps_finished}
Всього підходів: {all_reps}\n
Отримано aura: {aura_got}
    """,
}


finished_training_result = {
    "en": """
Body part: {body_part}\n
Started at: {time_start}
End at: {time_end}
Training time: {training_time}\n
Finished reps: {reps_finished}
Reps all: {all_reps}\n
Aura got: {aura_got}
    """,
    "uk": """
Частина тіла: {body_part}\n
Початок: {time_start}
Кінець: {time_end}
Повний час тренування: {training_time}\n
Закінчено підходів: {reps_finished}
Всього підходів: {all_reps}\n
Отримано aura: {aura_got}
    """,
}


training_status = {
    "en": """
Current Body part: {body_part}\n
training time: {clear_training_time}
started at: {clear_time_start}\n
finished reps: {reps_finished}
reps left: {reps_left}
    """,

    "uk": """
Поточна частина тіла: {body_part}\n
Початок: {clear_time_start}\n
Час тренування: {clear_training_time}
Завершено підходів: {reps_finished}
Подходів лишилося: {reps_left}
    """,
}


finish_training_confirm_title = {
    "en": "Do you realy want to finish training?",
    "uk": "Ви дійсно хочете завершити тренування?",
}

pause_training_confirm_title = {
    "en": "Pause training?\nAfter reset, break timer will end",
    "uk": "Призупинити тренування?\n Після відновлення, таймер перерви закінчиться",
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

add_more_btn = {
    "en": "Add more",
    "en": "Додати ще",
}

workout_body_part_setting_btn = {
    "en": "workout body part",
    "uk": "Частина тіла",
}
reps_setting_btn = {
    "en": "Reps and Breaks",
    "uk": "Підходи та перерви",
}

# reps
add_rep = {
    "en": 'Add Rep',
    "uk": 'Додати Підхід',
}

del_rep = {
    "en": 'Delete last rep',
    "uk": 'Видалити остінній підхід',
}

add_1_min_break = {
    "en": "Add 1 min to last break",
    "uk": "Додати 1 хвилину до останньої перерви",
}

remove_1_min_break = {
    "en": "Remove 1 min from last break",
    "uk": "Видалити 1 хвилину з останньої перерви",
}

custom_btn = {
    "en": "Custom",
    "uk": "Створити +",
}

# trainings
start_training_confirm_btn = {
    "en": "Start",
    "uk": "Почати",
}

not_today_btn = {
    "en": "Not Today",
    "uk": "Не Сьогодні",
}

take_break_btn = {
    "en": "Take a Break",
    "uk": "Перерва",
}

add_30_seconds = {
    "en": "Add 30 seconds",
    "uk": "Додати 30 секунд",
}


pause_training_btn = {
    "en": "Pause training",
    "uk": "Призупинити тренування",
}

resume_training_btn = {
    "en": "Resume training",
    "uk": "Відновити тренування",
}

finish_training_btn = {
    "en": "Finish training",
    "uk": "Завершити тренування",
}



pause_training_confirm_btn = {
    "en": "Pause",
    "uk": "Призупинити",
}

finish_training_confirm_btn = {
    "en": "Finish",
    "uk": "Завершити",
}

# langs codes
trans_leng_codes = {
    "en": "English 🇬🇧",
    "uk": "Укріїнська 🇺🇦",
}

# call answers
at_least_one_day_answer = {
    "en": "At least one day should be selected",
    "uk": "Виберіть хоча б один день",
}

set_body_part_answer = {
    "en": "Set body part for {day} to continue",
    "uk": "Щоб продовжити, визначте частину тіла для {day}",
}

set_reps_answer = {
    "en": "Set reps for {day} to continue",
    "uk": "Щоб продовжити, визначте підходи для {day}",
}