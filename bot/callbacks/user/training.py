from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
import datetime
from zoneinfo import ZoneInfo

from config import *

# states
from aiogram.fsm.context import FSMContext
from states import user as states

from keyboards import callback_filters
from keyboards.user import training as kbs
from texts import user as texts
import database as db
from database.models import User, FinishedUserTraining, UserTrainings
from training_timer import Timer, timers

# aura
from utils.user_aura import get_aura


router = Router()

async def delete_messages(bot: Bot, chat_id, messages):
    if messages:
        await bot.delete_messages(chat_id, messages)


# *user training and work with timer
async def on_timer_update(bot: Bot, chat_id, timer: Timer, state: FSMContext):
    state_data = await state.get_data()

    lang = state_data["user_lang"]

    message_id: int = state_data["message"]
    
    minutes, seconds = timer.get_clear_time()

    # checking if training state is break or warmup
    current_training_state = state_data["training_state"]

    if current_training_state == "break":
        text = texts.break_timer_title[lang].format(minutes=minutes, seconds=seconds)
    if current_training_state == "warmup":
        text = texts.warmup_timer_title[lang].format(minutes=minutes, seconds=seconds)
    
    kb = kbs.get_break_controll(lang)

    # update message
    await bot.edit_message_text(
        text, chat_id=chat_id, message_id=message_id,
        reply_markup=kb
    )


async def on_timer_end(bot: Bot, chat_id: int ,timer: Timer, state: FSMContext):
    state_data = await state.get_data()
    user_data = state_data["user_data"]

    message_id: int = state_data["message"]

    # delet message with bot
    await bot.delete_message(
        chat_id, message_id
    )

    # get and update prep ind
    current_rep_ind = state_data.get("current_rep_ind")

    # all reps 
    training_data = state_data.get("full_training_data")

    lang = state_data["user_lang"]

    # get rep data on ind
    all_reps = training_data["reps"]
    if len(all_reps) > current_rep_ind:
        rep_data = all_reps[current_rep_ind]
        rep_name = rep_data["name"]

        # find rep name on user lang in state_data
        for rep in state_data["user_reps_names"]:
            if rep["name"] == rep_name:
                rep_name = rep[lang]
                break

        if rep_name != "break":
            # send rep 
            kb = kbs.get_break(lang)
            text = texts.rep_title[lang].format(name=rep_name)
            # send message and set new in state
            msg = await bot.send_message(
                chat_id, text, reply_markup=kb
            ) # send new message to notify user
            # msg = await message.answer(text, reply_markup=kb)

            current_rep_ind += 1

            # update state
            await state.update_data(
                message=msg.message_id,
                current_rep_ind=current_rep_ind,
                training_state=f"rep_{rep_name}",
            )
    else:
        await bot.send_message(
            chat_id, texts.training_finished[lang]
        ) 
        # await message.answer(texts.training_finished[lang])

        # getting end time
        tz = ZoneInfo(DATETIME_TIME_ZONE)
        now = datetime.datetime.now(tz)

        state_data = await state.update_data(
            stopped=True,
            time_end=now,
        )

        # get text
        text, aura_got = get_finished_training_result(state_data, lang)

        await bot.send_message(
            chat_id, text
        ) 

        # adding to datebase
        await db.create_user_fihished_trainig(user_data.id, data=state_data)
        # getting and update user aura
        user = await db.get_user(user_data.id)
        aura: float = user.aura

        await db.update_user(user_data.id, {
            "aura": aura + aura_got
        })

        await state.clear()

        # gettin and stopping timer
        timer: Timer = timers[state_data["timer"]]
        if timer.on_run:
            await timer.stop()
            timer.time = 0
            timer.max_time = 0
        
        # delete timer object
        del timers[user_data.id]

@router.callback_query(callback_filters.UserStartTraining.filter())
async def confirm_start_training(call: CallbackQuery, callback_data: callback_filters.UserStartTraining, state: FSMContext):
    message: Message = call.message
    bot: Bot = message.bot
    chat_id = message.chat.id
    user_data = call.from_user
    call_data = callback_data.data

    if call_data == "start":
        # setting up timer and state_data
        state_data = await state.get_data()
        if state_data.get("timer"): # check if user on training
            return

        # clear and set state        
        await state.clear()
        await state.set_state(states.UserTraining)

        # get today day
        tz = ZoneInfo(DATETIME_TIME_ZONE)
        now = datetime.datetime.now(tz)
        day_name = now.strftime("%A").lower()[:3] # ex: getting from Monday -> mon

        # getting current day training data
        user = await db.get_user(user_data.id)
        lang = user.lang

        user_trainings_data = user.trainings
        if user_trainings_data == None:
            await call.answer()
            return
        
        training_data = user_trainings_data.days_data.get(day_name)

        # check if user has training today
        if training_data is None:
            # send select any other day's training plan

            # edit message
            text, kb = kbs.get_start_other_day_training(lang)
            text = text.format(
                day_name=texts.trans_days_of_week[lang][day_name]
            )
            await message.edit_text(
                text, reply_markup=kb
            )
            return
        
        # else setting training
        # counting reps count filtering list if reps are not breaks
        all_reps_count = len([rep for rep in training_data["reps"] if rep["name"] != "break"]) 

        # init timer 
        warmup_time = WARMUP_TIME # 4 minutes. set this value in seconds
        # set warmup on the very start of training
        training_timer = Timer(user_data.id, warmup_time)
        timers[user_data.id] = training_timer

        # setting state data
        await state.update_data(
            user_data=user_data,
            # training data
            full_training_data=training_data,
            user_reps_names=user.trainings.all_reps_names,
            user_body_parts_names=user.trainings.all_body_parts,
            # timer and time
            timer=user_data.id,
            time_start=now,
            # state
            training_state="warmup",
            # reps
            current_rep_ind=0,
            all_reps_count=all_reps_count,
            reps_finished=0,
            # message id
            message=message.message_id,
            # other state and lang
            stopped=False,
            pauses=[],
            user_lang=lang
        )


        minutes, seconds = training_timer.get_clear_time()

        # get text and kb
        text = texts.warmup_timer_title[lang].format(minutes=minutes, seconds=seconds)
        kb = kbs.get_break_controll(lang)

        # delete and send new message
        await message.edit_text(text, reply_markup=kb)       

        # setting timer update and end functions that will be call on these events
        training_timer.on_update_funk = on_timer_update
        training_timer.on_update_funk_args = (message.bot, chat_id, training_timer, state)

        training_timer.on_end_funk = on_timer_end
        training_timer.on_end_funk_args = (message.bot, chat_id, training_timer, state)

        await training_timer.start()

        

    elif call_data == "not_today": # todo reduce user aura hahahaahahhhahahha (evil laugh)
        await call.answer("poganyu😭😟😟😟🙍🏿🙍🏿🙍🏿🙍🏿🙍🏿")

# trainig plan. taking a break after rep
@router.callback_query(callback_filters.UserNavigateTrainingStates.filter())
async def navigate_training_states(call: CallbackQuery, callback_data: callback_filters.UserNavigateTrainingStates, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user
    chat_id = message.chat.id

    navigate_data = callback_data.data
    state_data = await state.get_data()

    # all reps 
    training_data = state_data.get("full_training_data")
    if training_data == None: # check if state is UserTraining and not other like UserSetUp
        await message.answer(texts.start_training[lang])
        return
    
    if state_data["stopped"]:
        return

    user = await db.get_user(user_data.id)
    lang = user.lang

    if navigate_data == "break": # start timer agin on new time of the break

        # get and update finished reps count
        reps_finished = state_data["reps_finished"]
        reps_finished += 1

        message_id: Message = state_data["message"]

        # get and update prep ind
        current_rep_ind = state_data.get("current_rep_ind")


        # get rep data on ind
        all_reps = training_data["reps"]
        if len(all_reps) > current_rep_ind:
            rep_data = all_reps[current_rep_ind]
            rep_name = rep_data["name"]

            if rep_name == "break":
                # send break 
                training_timer: Timer = timers[state_data["timer"]]

                # set time from break data
                training_timer.max_time = rep_data["minutes"] * 60 + rep_data["seconds"]
                training_timer.time = rep_data["minutes"] * 60 + rep_data["seconds"]

                # get time to show
                minutes, seconds = training_timer.get_clear_time()

                # send message
                text = texts.break_timer_title[lang].format(minutes=minutes, seconds=seconds)
                kb = kbs.get_break_controll(lang)

                # update message
                await message.bot.edit_message_text(
                    text, chat_id=chat_id, message_id=message_id,
                    reply_markup=kb
                )
                # await message.edit_text(text, reply_markup=kb)
                current_rep_ind += 1

                # update state
                await state.update_data(
                    current_rep_ind=current_rep_ind,
                    reps_finished=reps_finished,
                    training_state="break",
                )

                await training_timer.start()
        else: # finish training
            await message.answer(texts.training_finished[lang])
            # getting and stopping timer
            timer: Timer = timers[state_data["timer"]]
            if timer.on_run:
                await timer.stop()
                timer.time = 0
                timer.max_time = 0

            # getting end time
            tz = ZoneInfo(DATETIME_TIME_ZONE)
            now = datetime.datetime.now(tz)

            state_data = await state.update_data(
                stopped=True,
                time_end=now,
            )
            # get text
            text, aura_got = get_finished_training_result(state_data)

            await message.answer(text)

            # adding to datebase
            await db.create_user_fihished_trainig(user_data.id, data=state_data)
            
            # getting and update user aura
            user = await db.get_user(user_data.id)
            aura: float = user.aura

            await db.update_user(user_data.id, {
                "aura": aura + aura_got
            })
            # delete timer object
            del timers[user_data.id]
            await state.clear()

# controll break and warmup timer, add 30 seconds
@router.callback_query(callback_filters.UserBreakControll.filter())
async def break_timer_controll(call: CallbackQuery, callback_data: callback_filters.UserBreakControll, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user

    action = callback_data.action

    state_data = await state.get_data()

    timer_id: int | None = state_data.get("timer")
    if timer_id:
        timer = timers[timer_id]
        if action == "add_30_seconds":
            timer.time += 30
            timer.max_time += 30
            await timer.update_end_time()
            await timer.update_message()
    
    await call.answer("")
            

# like help commands for handlers
def get_clear_time(hours, minutes, seconds):

    if len(str(hours)) == 1:
        hours = "0" + str(hours)

    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)

    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)

    return f"{hours}:{minutes}.{seconds}"

def get_finished_training_result(state_data: dict, lang) -> tuple[str, float]:
    """Takes :code:`state_data` to get data from it, returns text as :class:`str`"""
    time_start: datetime = state_data["time_start"]
    time_end: datetime = state_data["time_end"]

    tz = ZoneInfo(DATETIME_TIME_ZONE)
    now = datetime.datetime.now(tz)

    # get clear time start
    start_hours = time_start.time().hour
    start_minutes = time_start.time().minute
    start_seconds = time_start.time().second

    clear_time_start = get_clear_time(start_hours, start_minutes, start_seconds)

    # get clear time end
    end_hours = time_end.time().hour
    end_minutes = time_end.time().minute
    end_seconds = time_end.time().second

    clear_time_end = get_clear_time(end_hours, end_minutes, end_seconds)

    # calculatin training time
    training_time: datetime.timedelta = now - time_start
    
    training_hours = int(training_time.total_seconds() // 3600)
    training_minutes = int((training_time.total_seconds() % 3600) // 60)
    training_seconds = int(training_time.total_seconds() % 60)
    
    clear_training_time = get_clear_time(training_hours, training_minutes, training_seconds)

    # calculating finished reps        
    reps_finished = state_data["reps_finished"]
    all_reps = state_data["all_reps_count"]

    # getting body_part
    body_part = state_data["full_training_data"]["selected_part"]

    for part in state_data["user_body_parts_names"]:
        if part["name"] == body_part:
            body_part = part[lang]
            break

    aura_got = get_aura(all_reps, reps_finished) # aura based on finished and all reps count. PS maybe I will change it

    text = texts.finished_training_result[lang].format(
        body_part=body_part,
        time_start=clear_time_start,
        time_end=clear_time_end,
        training_time=clear_training_time,
        reps_finished=reps_finished,
        all_reps=all_reps,
        aura_got=aura_got,
    )

    return text, aura_got

async def send_rep(message: Message, state_data, lang) -> Message:
    """to send new rep message if rep is not break or warmup. Returns message as new message to update in state"""
    # all reps 
    training_data = state_data.get("full_training_data")

    if state_data["stopped"]:
        return

    # get and update prep ind

    current_training_state = state_data["training_state"]
    if current_training_state in ("break", "warmup"): # check if rep is not break or warmup
        return
    
    current_rep_ind = state_data.get("current_rep_ind")
    
    # get rep data on ind
    all_reps = training_data["reps"]

    rep_data = all_reps[current_rep_ind-1]
    rep_name = rep_data["name"]

    
    kb = kbs.get_break(lang)
    # find rep name on user lang in state_data
    for rep in state_data["user_reps_names"]:
        if rep["name"] == rep_name:
            rep_name = rep[lang]
            break

    text = texts.rep_title[lang].format(
        name=rep_name
    )

    msg = await message.answer(text, reply_markup=kb)
    return msg

# control training. pause finish or back (delete message)
@router.callback_query(callback_filters.UserControlTraining.filter())
async def controll_training_status(call: CallbackQuery, callback_data: callback_filters.UserControlTraining, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user
    action = callback_data.data

    state_data = await state.get_data()

    user = await db.get_user(user_data.id)
    if user == None:
        call.answer()
    lang = user.lang

    if state_data.get("full_training_data"): # check if current state in UserTraining and not other
        if action == "back":
            await message.delete()

        if action == "back_to_menu":
            text, kb = kbs.get_training_control(state_data, lang)
            await message.edit_text(text, reply_markup=kb)

        if action == "finish":
            text = texts.finish_training_confirm_title[lang]
            kb = kbs.get_confirm_finish_training(lang)
            await message.edit_text(text, reply_markup=kb)

        if action == "pause":            
            text = texts.pause_training_confirm_title[lang]
            kb = kbs.get_confirm_pause_training(lang)
            await message.edit_text(text, reply_markup=kb)

        if action == "resume":
            timer: Timer = timers[state_data["timer"]]
            if not timer.on_run:
                if state_data["training_state"] in ["break", "warmup"]: # checking if training state is not rep, to avid bags and messages deletings
                    await timer.start()

            state_data = await state.update_data(stopped=False)
            text, kb = kbs.get_training_control(state_data, lang)
            await message.edit_text(text, reply_markup=kb)

            # send new rep message 
            msg = await send_rep(message, state_data, lang)

            if msg:
                # udpate_data
                await state.update_data(
                    message=msg.message_id
                )

        if action == "confirm_finish":
            # gettin and stopping timer
            timer: Timer = timers[state_data["timer"]]
            if timer.on_run:
                await timer.stop()
                timer.time = 0
                timer.max_time = 0

            # getting end time
            tz = ZoneInfo(DATETIME_TIME_ZONE)
            now = datetime.datetime.now(tz)

            state_data = await state.update_data(
                stopped=True,
                time_end=now,
            )
            # get text and aura
            text, aura_got = get_finished_training_result(state_data, lang)

            await message.edit_text(text)

            # adding to datebase
            await db.create_user_fihished_trainig(user_data.id, data=state_data)

            # get and update user aura
            user = await db.get_user(user_data.id)
            aura: float = user.aura

            await db.update_user(user_data.id, {
                "aura": aura + aura_got
            })
            # delete timer object
            del timers[user_data.id]
            await state.clear()

        if action == "confirm_pause":
            timer: Timer = timers[state_data["timer"]]
            if timer.on_run:
                await timer.stop()
                timer.time = 0
                timer.max_time = 0

            state_data = await state.update_data(stopped=True)
            
            text, kb = kbs.get_training_control(state_data, lang)
            await message.edit_text(text, reply_markup=kb)

    else:
        await message.answer(texts.start_training[lang])

        
# *user select other day training plang
@router.callback_query(callback_filters.UserStartOtherDayPlanTraining.filter())
async def start_other_day_trainig_plans(call: CallbackQuery, callback_data: callback_filters.UserStartOtherDayPlanTraining, state: FSMContext):
    message: Message = call.message
    user_data = call.from_user

    action = callback_data.data

    if action == "cancel":
        await message.delete()
    
    if action == "confirm":
        state_data = await state.get_data()

        if state_data.get("timer"):
            await call.answer()
            return
        
        

        user = await db.get_user(user_data.id)
        lang = user.lang

        # get trainings and send list to choose

        messages_to_delete = []

        # edit text
        text, messages = kbs.get_selected_days_training_plans(user.trainings.days_data, lang)
        msg = await message.edit_text(text)
        messages_to_delete.append(msg.message_id)

        # send messages
        for text, kb in messages:
            msg = await message.answer(text, reply_markup=kb)
            messages_to_delete.append(msg.message_id)

        # clear, set and update state
        await state.clear()
        await state.set_state(states.UserSelectTrainingPlan)

        await state.update_data(
            messages_to_delete=messages_to_delete
        )

@router.callback_query(callback_filters.UserSelectDayPlanTrainig.filter(F.get_plan)) # check if True 
async def get_day_training_plan(call: CallbackQuery, callback_data: callback_filters.UserSelectDayPlanTrainig, state: FSMContext):
    message: Message = call.message
    bot: Bot = message.bot
    chat_id = message.chat.id
    user_data = call.from_user

    day_name = callback_data.day_name

    state_data = await state.get_data()

    user = await db.get_user(user_data.id)
    lang = user.lang

    # get day data 
    day_data = user.trainings.days_data[day_name]
    all_body_parts = user.trainings.all_body_parts
    all_reps_names = user.trainings.all_reps_names

    # edit message
    text, kb = kbs.get_day_training_plan(day_data, all_body_parts, all_reps_names, day_name, lang)
    await message.edit_text(text, reply_markup=kb)

@router.callback_query(callback_filters.UserSelectDayPlanTrainig.filter(F.day_name != " "))
async def select_day_training_plan(call: CallbackQuery, callback_data: callback_filters.UserSelectDayPlanTrainig, state: FSMContext):
    message: Message = call.message
    bot: Bot = message.bot
    chat_id = message.chat.id
    user_data = call.from_user

    day_name = callback_data.day_name

    state_data = await state.get_data()

    if state_data.get("timer"):
        await call.answer()
        return

    # getting current day training data
    user = await db.get_user(user_data.id)
    lang = user.lang

    

    # get today day
    tz = ZoneInfo(DATETIME_TIME_ZONE)
    now = datetime.datetime.now(tz)

    user_trainings_data = user.trainings
    if user_trainings_data == None:
        await call.answer()
        return
    
    training_data = user_trainings_data.days_data.get(day_name)

    # counting reps count filtering list if reps are not breaks
    all_reps_count = len([rep for rep in training_data["reps"] if rep["name"] != "break"]) 

    # init timer 
    warmup_time = WARMUP_TIME # 4 minutes. set this value in seconds

    # set warmup on the very start of training
    training_timer = Timer(user_data.id, warmup_time)
    timers[user_data.id] = training_timer

    minutes, seconds = training_timer.get_clear_time()

    # get text and kb
    text = texts.warmup_timer_title[lang].format(minutes=minutes, seconds=seconds)
    kb = kbs.get_break_controll(lang)

    # delete and send new message
    msg = await message.answer(text, reply_markup=kb)       

    # setting timer update and end functions that will be call on these events
    training_timer.on_update_funk = on_timer_update
    training_timer.on_update_funk_args = (message.bot, chat_id, training_timer, state)

    training_timer.on_end_funk = on_timer_end
    training_timer.on_end_funk_args = (message.bot, chat_id, training_timer, state)

    await training_timer.start()

    # delete messages
    await delete_messages(
        bot, chat_id, state_data.get("messages_to_delete", [])
    )

    # clear, set and update state
    await state.clear()
    await state.set_state(states.UserTraining)

    # setting state data
    await state.update_data(
        user_data=user_data,
        # training data
        full_training_data=training_data,
        user_reps_names=user.trainings.all_reps_names,
        user_body_parts_names=user.trainings.all_body_parts,
        # timer and time
        timer=user_data.id,
        time_start=now,
        # state
        training_state="warmup",
        # reps
        current_rep_ind=0,
        all_reps_count=all_reps_count,
        reps_finished=0,
        # message id
        message=msg.message_id,
        # other state and lang
        stopped=False,
        pauses=[],
        user_lang=lang
    )

    

@router.callback_query(callback_filters.UserSelectDayPlanTrainig.filter(F.back_to_day != " "))
async def back_to_day_to_select_training_plan(call: CallbackQuery, callback_data: callback_filters.UserSelectDayPlanTrainig, state: FSMContext):
    message: Message = call.message
    bot: Bot = message.bot
    chat_id = message.chat.id
    user_data = call.from_user

    day_name = callback_data.back_to_day

    user = await db.get_user(user_data.id)
    lang = user.lang

    state_data = await state.get_data()

    # edit message
    text, kb = kbs.get_day_select_training_plan(day_name, lang)
    await message.edit_text(text, reply_markup=kb)


# *user view finished trainings
# get text from data from database
def get_training_result(f_t: FinishedUserTraining, lang, user_all_body_parts) -> tuple[str, float]:
    """Takes :code:`f_t` to get data from it, returns text as :class:`str`"""
    time_start: datetime = f_t.time_start
    time_end: datetime = f_t.time_end

    tz = ZoneInfo(DATETIME_TIME_ZONE)

    # get clear time start
    start_hours = time_start.time().hour
    start_minutes = time_start.time().minute
    start_seconds = time_start.time().second

    clear_time_start = get_clear_time(start_hours, start_minutes, start_seconds)

    # get clear time end
    end_hours = time_end.time().hour
    end_minutes = time_end.time().minute
    end_seconds = time_end.time().second

    clear_time_end = get_clear_time(end_hours, end_minutes, end_seconds)

    # calculatin training time
    training_hours = f_t.full_training_time.split(":")[0]
    training_minutes = f_t.full_training_time.split(":")[1].split(".")[0]
    training_seconds = f_t.full_training_time.split(":")[1].split(".")[1]
    
    clear_training_time = get_clear_time(training_hours, training_minutes, training_seconds)

    # calculating finished reps        
    reps_finished = f_t.reps_finished
    all_reps = f_t.all_reps_count

    # getting data in format dd-mm-yy
    date = f_t.time_start.date()
    # getting body_part
    body_part = f_t.full_training_data["selected_part"]
    for part in user_all_body_parts:
        if part["name"] == body_part:
            body_part = part[lang]
            break

    aura_got = get_aura(all_reps, reps_finished) # aura based on finished and all reps count. PS maybe I will change it

    text = texts.finished_training_text[lang].format(
        id=f_t.id,
        date=date,
        body_part=body_part,
        time_start=clear_time_start,
        time_end=clear_time_end,
        training_time=clear_training_time,
        reps_finished=reps_finished,
        all_reps=all_reps,
        aura_got=aura_got,
    )

    return text, aura_got

def sort_finished_trainings(x: FinishedUserTraining) -> int:
    # getting seconds from datetime to sort
    seconds = x.time_start.timestamp()
    return -seconds

@router.callback_query(callback_filters.UserAddMoreFT.filter())
async def add_more_ft(call: CallbackQuery, callback_data: callback_filters.UserAddMoreFT):
    message: Message = call.message
    user_data = call.from_user

    offset = callback_data.offset
    start = callback_data.start

    user = await db.get_user(user_data.id)

    if user:
        # sort trainins by date
        finished_trainings = sorted(user.finished_trainings[start:start+offset] , key=sort_finished_trainings)

        global_i = start
        for i, f_t in enumerate(finished_trainings):
            kb = None
            # add keyboard if message is last and not the last in list
            if i + 1 == len(finished_trainings) and global_i + 1 < len(user.finished_trainings):
                kb = await kbs.get_add_more_f_t(start+offset, offset, user.lang, user.trainings.all_body_parts)
            # send messsage
            text = get_training_result(f_t, user.lang)
            await message.answer(text, reply_markup=kb)

            # count global_i for checking last f_t in list
            global_i += 1

        await message.edit_reply_markup(reply_markup=None)