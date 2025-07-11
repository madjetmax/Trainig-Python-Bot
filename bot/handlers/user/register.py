from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import *

from database.models import User, FinishedUserTraining
import database as db
from keyboards.user import register as kbs
from scheduler import user as schedule_manager

from texts import user as texts
from states import user as states

router = Router()

# registration 
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_data = message.from_user

    # await db.delete_user(user_data.id)

    user = await db.get_user(user_data.id)

    if user: # send register message
        trainings = user.trainings
        
        lang = user.lang

        # check if user created trainings 
        if trainings:
            # check if user on training 
            state_data = await state.get_data()
            if state_data.get("timer"):
                await message.answer(texts.cant_edit_at_training[lang])
                return
            
            # else send edit confirm
            kb = kbs.get_user_edit_training_confirm(lang)
            await message.answer(texts.edit_trainings[lang], reply_markup=kb)
        else:
            # send setup trainings
            kb = kbs.confirm_setup(lang)
            await message.answer(texts.start_training_set_up[lang].format(name=user_data.full_name), reply_markup=kb)
    
    else: # send choosed lang
        lang = user_data.language_code

        if lang not in texts.all_lengs_codes:
            lang = "en"

        # send message
        kb = kbs.get_choose_lang()
        await message.answer(texts.greate[lang].format(name=user_data.full_name.capitalize()), reply_markup=kb)

        # create user
        await db.create_user(user_data.id, user_data.full_name, lang)

# new body part 
@router.message(states.UserSetUp.new_body_part, F.text)
async def get_new_body_part(message: Message, state: FSMContext):
    bot: Bot = message.bot
    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id
    
    state_data = await state.get_data()
    lang = state_data["user_lang"]

    # get days, day and day_data
    days = state_data["days"]

    day = state_data["selected_day"]
    day_data = days[day]

    # update body parts
    all_body_parts = state_data["all_body_parts"]
    all_body_parts.append(
        {
            "name": text,
            "en": text,
            "uk": text,
        }
    )

    # set selected body part
    days[day]["selected_part"] = text

    # udpate message to update
    text, kb = kbs.get_day_setting_by_name("workout_body_part", day, day_data, state_data, lang)

    await bot.edit_message_text(
        message_id=state_data["message_to_update"],
        chat_id=chat_id,
        text=text,
        reply_markup=kb
    )

    # delete messages
    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)
    
    # set state
    await state.set_state(states.UserSetUp.days)

# new rep name
@router.message(states.UserSetUp.new_rep_name, F.text)
async def get_new_rep_name(message: Message, state: FSMContext):
    bot: Bot = message.bot
    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id
    
    state_data = await state.get_data()
    lang = state_data["user_lang"]

    # get day 
    day = state_data["selected_day"]

    # update body parts
    all_reps_names = state_data["all_reps_names"]
    all_reps_names.append(
        {
            "name": text,
            "en": text,
            "uk": text,
        }
    )

    # udpate message to update
    text, kb = kbs.get_rep_name_setting(day, all_reps_names, lang)

    await bot.edit_message_text(
        message_id=state_data["message_to_update"],
        chat_id=chat_id,
        text=text,
        reply_markup=kb
    )

    # delete messages
    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)

    # set state
    await state.set_state(states.UserSetUp.days)

# start time
def check_time_valid(text: str):
    try:    
        if ":" in text:
            hours = int(text.split(":")[0])
            minutes = int(text.split(":")[1]) 
        elif "." in text:   
            hours = int(text.split(".")[0])
            minutes = int(text.split(".")[1])
        else:
            return None
        
        # check if time in range
        if hours >= 24 or hours < 0:
            return None
        
        if minutes >= 60 or minutes < 0:
            return None

        return hours, minutes
    except Exception as ex:
        print(ex)
        return None
    
@router.message(states.UserSetUp.time_start, F.text)
async def get_start_time(message: Message, dispatcher: Dispatcher, state: FSMContext):
    message_id = message.message_id
    chat_id = message.chat.id
    bot: Bot = message.bot
    user_data = message.from_user
    
    valid_time = check_time_valid(message.text)
    if valid_time:
        # update and get state
        state_data = await state.update_data(
            time_start=message.text
        )
        lang = state_data["user_lang"]

        # send message on seccess
        await message.answer(texts.trainings_set_up[lang], reply_markup=None)

        # delete message to send time 
        try:
            await message.bot.delete_message(message.chat.id, message_id-1) 
        except Exception:
            pass

        # get time
        hours = valid_time[0]
        minutes = valid_time[1]

        # save to database
        await db.create_user_trainigs(
            user_data.id, state_data, hours, minutes
        )

        # start schedule jobs
        days = list(state_data["days"].keys())
        
        # training remind
        schedule_manager.create_training_remind(
            bot, dispatcher, 
            user_data.id, 
            days, 
            hours, minutes 
        )
        # skipped training remind
        schedule_manager.create_skipped_training_remind(
            bot, dispatcher, 
            user_data.id, 
            ALL_WEEK_DAYS, 
            SCHD_SEND_TRAINIG_SKIPPED_HOURS,
            SCHD_SEND_TRAINIG_SKIPPED_MINUTES,
        )
        # clear state
        await state.clear()
        
    else: # answer if time is invalid
        state_data = await state.get_data()
        lang = state_data["user_lang"]
        await message.answer(texts.invalid_time[lang])
