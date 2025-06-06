from aiogram.filters.callback_data import CallbackData

# *training setup
class UserConfirmSetup(CallbackData, prefix="user_confirm_setup"):
    data: str

class UserChooseDay(CallbackData, prefix="user_choose_day"):
    day: str

class UserSettingDay(CallbackData, prefix="user_setting_day"):
    day: str = " "
    setting: str = " "
    body_part: str = " "

    reps_action: str = " "
    rep_name: str = " "

# for navigation
class UserConfirmSetupNavigate(CallbackData, prefix="user_confirm_navigate"):
    kb_num: int = -1
    to: str = " "
    day: str = " "

# *edit user training
class UserEditTrainingConfirm(CallbackData, prefix="user_edit_training_confirm"):
    data: str

# *user menu and edit data
class UserEditData(CallbackData, prefix="user_edit_data"):
    kb_num: int = -1
    to: str = " "
    back_to_day: str = " "

    action: str = " "
    switch_day: str = " "

class UserEditDay(CallbackData, prefix="user_edit_day"):
    day: str = " "
    setting: str = " "
    body_part: str = " "

    reps_action: str = " "
    rep_name: str = " "

# *user trainig
class UserStartTraining(CallbackData, prefix="user_start_trainig"):
    data: str

class UserNavigateTrainingStates(CallbackData, prefix="user_navigate_training"):
    data: str

class UserControlTraining(CallbackData, prefix="user_control_training"):
    data: str

class UserBreakControll(CallbackData, prefix="user_break_controll"):
    action: str


# *finished trainigs list
class UserAddMoreFT(CallbackData, prefix="user_add_more_ft"):
    offset: int
    start: int
    