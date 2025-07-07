from aiogram.filters.callback_data import CallbackData

# *user
# *training setup
class UserChooseLang(CallbackData, prefix="u_choose_lang"):
    lang: str

class UserConfirmSetup(CallbackData, prefix="u_confirm_setup"):
    data: str

class UserChooseDay(CallbackData, prefix="u_choose_day"):
    day: str

class UserSettingDay(CallbackData, prefix="u_setting_day"):
    day: str = " "
    setting: str = " "
    body_part_ind: int = -1
    
    add_custom_body_part: bool = False
    add_custom_rep_name: bool = False

    use_body_part_for_all_days: bool = False
    confirm_use_body_part_for_all_days: str = " "

    use_reps_for_all_days: bool = False
    confirm_use_reps_for_all_days: str = " "

    reps_action: str = " "
    rep_name_ind: int = -1

# for navigation
class UserConfirmSetupNavigate(CallbackData, prefix="u_confirm_navigate"):
    kb_num: int = -1
    to: str = " "
    day: str = " "

# *edit user training
class UserEditTrainingConfirm(CallbackData, prefix="u_edit_training_confirm"):
    data: str

# *user menu and edit data
class UserEditData(CallbackData, prefix="u_edit_data"):
    to: str = " "

    back_to_day: str = " "

    action: str = " "
    switch_day: str = " "

    set_lang: str = " "

class UserEditDay(CallbackData, prefix="u_edit_day"):
    day: str = " "
    setting: str = " "
    body_part_ind: int = -1

    add_custom_body_part: bool = False
    add_custom_rep_name: bool = False

    use_body_part_for_all_days: bool = False
    confirm_use_body_part_for_all_days: str = " "

    use_reps_for_all_days: bool = False
    confirm_use_reps_for_all_days: str = " "

    reps_action: str = " "
    rep_name_ind: int = -1

# *user trainig
class UserStartTraining(CallbackData, prefix="u_start_trainig"):
    data: str

class UserNavigateTrainingStates(CallbackData, prefix="u_navigate_training"):
    data: str

class UserControlTraining(CallbackData, prefix="u_control_training"):
    data: str

class UserBreakControll(CallbackData, prefix="u_break_controll"):
    action: str

# other day plan training
class UserStartOtherDayPlanTraining(CallbackData, prefix="u_start_od_trainig"):
    data: str

class UserSelectDayPlanTrainig(CallbackData, prefix="u_select_od_training_plan"):
    day_name: str = ' '
    get_plan: bool = False

    back_to_day: str = " "

# *finished trainigs list
class UserAddMoreFT(CallbackData, prefix="u_add_more_ft"):
    offset: int
    start: int

# *user admin message
class UserAdminMessage(CallbackData, prefix="u_admin_message"):
    data: str = " " 

class UserControllAdminMessage(CallbackData, prefix="u_ctrl_admin_msg"):
    action: str

# * admin
# * menu, edit data manage users etc
class AdminMenu(CallbackData, prefix="admin_menu"):
    to: str = " "

class AdminAddMoreAM(CallbackData, prefix="a_add_more_dm"):
    offset: int
    start: int

class ControlUser(CallbackData, prefix="controll_user"):
    user_id: int
    action: str

# *admin user message
class AdminUserMessage(CallbackData, prefix="a_u_msg_ctrl"):
    user_id: int
    action: str
    admin_message_id: int = -1

class AdminConfrimUserMessagesBlock(CallbackData, prefix="a_u_block_msgs"):
    user_id: int
    confirm_block_messages: bool = False
    confirm_unblock_messages: bool = False
    cancel: bool = False
    admin_message_id: int = -1

# sending message
class AdminCancelSendMessage(CallbackData, prefix="a_cancel_send_msg"):
    cancel: bool
