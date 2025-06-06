from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class UserSetUp(StatesGroup):
    days = State()
    time_start = State()    

    # for deleting messages
    messages_to_delete = State() # ids


class UserTraining(StatesGroup):
    user_data = State() # id, fullname etc

    full_training_data = State() # trainig data from db of specific week day

    timer = State() # in seconds
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

# *user menu and edit data
class UserEditData(StatesGroup):
    days = State()
    time_start = State()    
    
    # for deleting messages
    messages_to_delete = State() # ids