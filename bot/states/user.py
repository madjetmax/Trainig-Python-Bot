from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# *user training setup on start
class UserSetUp(StatesGroup):
    user_lang = State() # str, language code, ex: en uk

    days = State()
    time_start = State()        

    all_body_parts = State() # list
    all_reps_names = State() # list

    new_body_part = State()
    new_rep_name = State()

    selected_day = State()
    message_to_update = State() # id. to edit messae if created custom body part or rep name
    message_title_to_delete = State() # id. message that sent as a title when add new custom body part or rep

    # for deleting messages
    messages_to_delete = State() # ids

# *user training with timer, breaks
class UserTraining(StatesGroup):
    user_data = State() # id, fullname etc

    full_training_data = State() # trainig data from db of specific week day
    user_reps_names = State() # list of dict
    user_body_parts_names = State() # list of dict

    timer = State() # in seconds, has user id to get it from dict
    current_rep_ind = State() # int. its can be a break, warmup or prep data
    
    # for counting how many left and finished
    all_reps_count = State()
    reps_finished = State()

    training_state = State() # defines training state, for exaple: break, prep, warm up

    time_start = State()
    time_end = State()

    pauses = State() # Todo list of {"start": datetime, "end":datetime} (starts and ends of pauses). For calculating pauses

    message = State() # for editing, deleting and work with. As main message that shows time and training info

    stopped = State() # bool

    # for deleting messages
    messages_to_delete = State() # ids


# *user select training plan
class UserSelectTrainingPlan(StatesGroup):


    messages_to_delete = State() # ids. list

# *user menu and edit data
class UserEditData(StatesGroup):
    user_lang = State() # str, language code, ex: en uk

    days = State()
    time_start = State()    
    
    new_body_part = State()
    new_rep_name = State()

    selected_day = State()
    message_to_update = State() # id. to edit messae if created custom body part or rep name
    message_title_to_delete = State() # id. message that sent as a title when add new custom body part or rep

    # for deleting messages
    messages_to_delete = State() # ids

# *user message to admin
class UserAdminMessage(StatesGroup):
    on_admin_message = State() # bool
    text = State()
